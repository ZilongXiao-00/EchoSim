import os
import json
import asyncio
import random
import time
import hashlib
import threading
from typing import Any, Dict, List, Optional
from contextlib import asynccontextmanager

import httpx

# =========================================================
# Config (NO hardcoded key; show hash only)
# =========================================================
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.minimax.chat/v1").rstrip("/")
DEFAULT_MODEL = os.getenv("DEFAULT_LLM_MODEL_NAME", "MiniMax-M2.1")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()

CHAT_COMPLETIONS_URL = f"{OPENAI_BASE_URL}/chat/completions"


def _key_hash(k: str) -> str:
    if not k:
        return "EMPTY"
    return hashlib.sha256(k.encode()).hexdigest()[:10]


print(
    f"[SIM][BOOT] base_url={OPENAI_BASE_URL} model={DEFAULT_MODEL} key_hash={_key_hash(OPENAI_API_KEY)}"
)

# =========================================================
# Concurrency instrumentation
# =========================================================
_ACTIVE_TASKS = 0
_MAX_ACTIVE_TASKS = 0
_LOCK = asyncio.Lock()


@asynccontextmanager
async def _track_concurrency(tag: str):
    global _ACTIVE_TASKS, _MAX_ACTIVE_TASKS
    start_t = time.time()

    async with _LOCK:
        _ACTIVE_TASKS += 1
        _MAX_ACTIVE_TASKS = max(_MAX_ACTIVE_TASKS, _ACTIVE_TASKS)
        cur = _ACTIVE_TASKS
        print(f"[SIM][CONC] START persona={tag} active={cur} t={start_t:.2f}")

    try:
        yield
    finally:
        end_t = time.time()
        async with _LOCK:
            _ACTIVE_TASKS -= 1
            cur = _ACTIVE_TASKS
            print(f"[SIM][CONC] END   persona={tag} active={cur} dt={end_t-start_t:.2f}s")

def _extract_json_substring(s: str) -> Optional[str]:
    """
    从模型输出里尽量提取一个 JSON 子串：
    - 先找第一个 '{'...' }' 的最大平衡段
    - 找不到再试 '['...']'
    """
    if not isinstance(s, str):
        return None

    def find_balanced(open_ch: str, close_ch: str) -> Optional[str]:
        start = s.find(open_ch)
        if start < 0:
            return None
        depth = 0
        for i in range(start, len(s)):
            ch = s[i]
            if ch == open_ch:
                depth += 1
            elif ch == close_ch:
                depth -= 1
                if depth == 0:
                    return s[start:i+1]
        return None

    obj = find_balanced("{", "}")
    if obj:
        return obj
    arr = find_balanced("[", "]")
    if arr:
        return arr
    return None
# =========================================================
# Safe JSON loads
# =========================================================
def _safe_json_loads(x: Any, fallback: Any):
    if x is None:
        return fallback
    if isinstance(x, (dict, list)):
        return x
    if isinstance(x, str):
        # 1) 直接 loads
        try:
            return json.loads(x)
        except Exception:
            pass
        # 2) 尝试从文本里抽取 JSON 子串再 loads
        j = _extract_json_substring(x)
        if j:
            try:
                return json.loads(j)
            except Exception:
                pass
        return fallback
    return fallback


# =========================================================
# Prompt builder
# =========================================================
def _build_persona_prompt(
    persona: Dict[str, Any],
    survey_questions: List[Dict[str, Any]]
) -> List[Dict[str, str]]:
    persona_str = json.dumps(persona, ensure_ascii=False)
    questions_str = json.dumps(survey_questions, ensure_ascii=False)

    system = (
        "You are a synthetic survey respondent. "
        "You MUST answer strictly from the given persona's perspective. "
        "Return ONLY valid JSON, no extra text."
    )

    user = f"""
Persona:
{persona_str}

Survey Questions:
{questions_str}

Return ONLY JSON in this schema:
{{
  "respondent_id": "<string>",
  "persona_name": "<string>",
  "responses": [
    {{"q_id": 1, "choice": "<string>", "reasoning": "<string>"}},
    {{"q_id": 2, "text": "<string>"}}
  ]
}}

Rules:
- Keep q_id consistent with the questions.
- No markdown. No commentary. JSON only.
""".strip()

    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]


async def _call_llm_json(
    client: httpx.AsyncClient,
    messages: List[Dict[str, str]],
    model: str,
    timeout_s: float,
    max_retries: int = 5,
) -> Dict[str, Any]:
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }

    # 尝试启用 JSON 模式（如果服务端不支持，可能返回 400；我们会自动降级）
    payload_json_mode = {
        "model": model,
        "messages": messages,
        "temperature": 0.2,
        "response_format": {"type": "json_object"},
    }

    payload_plain = {
        "model": model,
        "messages": messages,
        "temperature": 0.2,
    }

    last_err = None
    used_json_mode = True  # 第一次先试 JSON 模式

    for attempt in range(max_retries):
        try:
            payload = payload_json_mode if used_json_mode else payload_plain
            print(f"[SIM][HTTP] POST {CHAT_COMPLETIONS_URL} attempt={attempt+1} json_mode={used_json_mode}")

            resp = await client.post(
                CHAT_COMPLETIONS_URL,
                headers=headers,
                json=payload,
                timeout=timeout_s,
            )

            # 429
            if resp.status_code == 429:
                ra = resp.headers.get("Retry-After")
                if ra:
                    try:
                        wait_s = float(ra)
                    except Exception:
                        wait_s = 10.0
                else:
                    wait_s = min(20.0, 8.0 * (attempt + 1)) + random.random() * 1.5
                print(f"[SIM][HTTP][429] rate limited; sleep {wait_s:.1f}s")
                await asyncio.sleep(wait_s)
                last_err = RuntimeError(f"429 rate limited, waited {wait_s:.1f}s")
                continue

            # JSON 模式不被支持时，很多兼容层会 400/422，直接降级到普通模式重试
            if used_json_mode and resp.status_code in (400, 401, 403, 404, 422):
                print(f"[SIM][HTTP] json_mode unsupported? status={resp.status_code}, fallback to plain mode")
                used_json_mode = False
                await asyncio.sleep(0.2)
                continue

            resp.raise_for_status()
            data = resp.json()

            content = data["choices"][0]["message"]["content"]
            obj = _safe_json_loads(content, None)

            # 允许两种返回：
            # A) 直接符合 schema：{"respondent_id":..., "responses":[...]}
            # B) 外层包裹：{"data":{...schema...}} 或 {"result":{...}}
            if isinstance(obj, dict):
                if "responses" in obj:
                    print("[SIM][HTTP] OK: got JSON with responses")
                    return obj
                for k in ("data", "result", "output"):
                    inner = obj.get(k)
                    if isinstance(inner, dict) and "responses" in inner:
                        print(f"[SIM][HTTP] OK: got wrapped JSON under '{k}'")
                        return inner

            # 如果还是不行：打印一小段 content 方便诊断（截断，避免刷屏）
            preview = content[:200].replace("\n", "\\n") if isinstance(content, str) else str(type(content))
            print(f"[SIM][HTTP][BAD] cannot parse responses; preview={preview}")

            last_err = ValueError("Model did not return valid JSON with 'responses'.")

        except Exception as e:
            print(f"[SIM][HTTP][ERR] {e}")
            last_err = e

        await asyncio.sleep((2 ** attempt) * 0.5 + random.random() * 0.3)

    raise RuntimeError(f"LLM call failed after retries: {last_err}")


# =========================================================
# Parallel runner
# =========================================================
async def _run_parallel(
    personas: List[Dict[str, Any]],
    survey_questions: List[Dict[str, Any]],
    model: str,
    max_concurrency: int,
    timeout_s: float,
) -> List[Dict[str, Any]]:
    global _MAX_ACTIVE_TASKS
    _MAX_ACTIVE_TASKS = 0

    print(f"[SIM][RUN] personas={len(personas)} max_concurrency={max_concurrency}")

    semaphore = asyncio.Semaphore(max(1, int(max_concurrency)))

    async with httpx.AsyncClient() as client:

        async def one(persona: Dict[str, Any]) -> Dict[str, Any]:
            tag = (
                str(persona.get("id"))
                or str(persona.get("respondent_id"))
                or str(persona.get("name"))
                or str(persona.get("persona_name"))
                or "unknown"
            )
            async with semaphore:
                async with _track_concurrency(tag):
                    messages = _build_persona_prompt(persona, survey_questions)
                    return await _call_llm_json(
                        client=client,
                        messages=messages,
                        model=model,
                        timeout_s=timeout_s,
                    )

        tasks = [asyncio.create_task(one(p)) for p in personas]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    print(f"[SIM][RUN] MAX_CONCURRENCY_OBSERVED={_MAX_ACTIVE_TASKS}")

    out: List[Dict[str, Any]] = []
    for r in results:
        if isinstance(r, Exception):
            out.append({
                "respondent_id": "UNKNOWN",
                "persona_name": "UNKNOWN",
                "responses": [],
                "error": str(r),
            })
        else:
            out.append(r)
    return out


# =========================================================
# Event-loop safe coroutine runner (fix asyncio event loop error)
# =========================================================
def _run_coro_safely(coro):
    """
    If there's no running loop: asyncio.run(coro)
    If there IS a running loop (common inside OpenAgents): run in a new thread with a new loop.
    """
    try:
        asyncio.get_running_loop()
        running = True
    except RuntimeError:
        running = False

    if not running:
        return asyncio.run(coro)

    result_box = {"result": None, "error": None}

    def _thread_target():
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result_box["result"] = loop.run_until_complete(coro)
        except Exception as e:
            result_box["error"] = e
        finally:
            try:
                loop.close()
            except Exception:
                pass

    t = threading.Thread(target=_thread_target, daemon=True)
    t.start()
    t.join()

    if result_box["error"] is not None:
        raise result_box["error"]
    return result_box["result"]


# =========================================================
# OpenAgents tool entry
# =========================================================
def simulate_survey_batch(
    task_id: str,
    survey_questions: Any,
    personas: Any,
    model_name: Optional[str] = None,
    max_concurrency: int = 4,
    timeout_s: float = 30.0,
) -> str:
    """
    Tool entry: parallel persona simulation, with debug + safe event loop handling.
    """
    print(f"[SIM][TOOL] CALLED simulate_survey_batch task_id={task_id}")
    print(f"[SIM][TOOL] key_hash={_key_hash(OPENAI_API_KEY)} base_url={OPENAI_BASE_URL}")

    survey_questions = _safe_json_loads(survey_questions, [])
    personas = _safe_json_loads(personas, [])

    if not OPENAI_API_KEY:
        return json.dumps({"error": "OPENAI_API_KEY is empty. export OPENAI_API_KEY first."}, ensure_ascii=False)

    if not isinstance(survey_questions, list):
        return json.dumps({"error": "survey_questions must be a list"}, ensure_ascii=False)

    if not isinstance(personas, list) or len(personas) == 0:
        return json.dumps({"error": "personas must be a non-empty list"}, ensure_ascii=False)

    model = model_name or DEFAULT_MODEL

    try:
        results = _run_coro_safely(_run_parallel(
            personas=personas,
            survey_questions=survey_questions,
            model=model,
            max_concurrency=max(1, int(max_concurrency)),
            timeout_s=float(timeout_s),
        ))
    except Exception as e:
        return json.dumps({
            "task_id": task_id,
            "status": "failed",
            "error": f"simulate_survey_batch tool execution failed - {type(e).__name__}: {e}"
        }, ensure_ascii=False)

    respondents: List[str] = []
    for r in results:
        rid = r.get("respondent_id")
        if isinstance(rid, str) and rid:
            respondents.append(rid)

    return json.dumps({
        "task_id": task_id,
        "status": "ok",
        "responses_batch": results,
        "respondents": respondents,
        "concurrency_report": {
            "max_concurrency_configured": int(max_concurrency),
            "max_concurrency_observed": int(_MAX_ACTIVE_TASKS),
            "key_hash": _key_hash(OPENAI_API_KEY),
        }
    }, ensure_ascii=False, indent=2)
