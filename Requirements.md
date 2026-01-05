# EchoSim 需求文档

<div align="center">

**OpenAgents 合成用户调研系统**  
版本: 0.1.0 | 状态: 草稿 | 框架: OpenAgents

</div>

## 📋 目录

1. [核心业务流程](#核心业务流程)
2. [数据结构规范](#数据结构规范)

---

## 1. 核心业务流程 (Core Workflow)

### Epic 1: 智能问卷设计 (Survey Architecture)

**Owner**: Agent A (Survey Architect)

#### Story 1.1: 模糊需求转化为结构化问卷

> **As a** 产品经理 (PM),  
> **I want** 输入一句话的调研目标（如"调查 Z 世代对咖啡的偏好"），  
> **So that** 我不需要具备专业市场调研知识也能获得一份逻辑严密的问卷。

**Acceptance Criteria (EARS Notation)**:

| 类型 | 描述 |
|------|------|
| Event-driven | 当用户输入自然语言描述的调研目标时，系统应生成包含封闭式（Likert 量表）和开放式问题的结构化问卷 |
| Ubiquitous | 系统应以标准 JSON 格式输出最终问卷配置（兼容 Agent C） |
| Optional | 启用 Web Search Mod 时，系统应在生成问题前查询当前市场趋势 |
| Unwanted | 如果用户输入过于模糊（少于 5 个词），系统应请求用户明确目标人群或产品类型 |

#### Story 1.2: 目标样本定义

> **As a** 调研发起人,  
> **I want** 明确定义目标用户的画像维度（如年龄分布、职业、收入水平），  
> **So that** 生成的虚拟用户符合我的潜在市场定位。

**Acceptance Criteria (EARS Notation)**:

| 类型 | 描述 |
|------|------|
| Event-driven | 当问卷逻辑确定后，系统应生成目标受众规范，详细说明人口分布（如"30% 工程师，70% 设计师"） |
| Ubiquitous | 系统应允许用户手动覆盖推荐的分布百分比 |

---

### Epic 2: 合成用户生成 (Synthetic User Generation)

**Owner**: Agent B (Persona Factory)

#### Story 2.1: 批量生成多样化画像

> **As a** 系统,  
> **I want** 根据样本定义批量生成独立的 User Persona 数据，  
> **So that** 模拟调研能够覆盖不同的性格和背景，避免千篇一律。

**Acceptance Criteria (EARS Notation)**:

| 类型 | 描述 |
|------|------|
| Event-driven | 当 Agent A 传递目标受众规范后，系统应生成 N 个唯一画像（默认 N=10） |
| Ubiquitous | 系统应在每个 persona JSON 中包含特定的"心理图形属性"（如消费习惯、技术熟练度、当前情绪） |
| Unwanted | 如果同一批次生成的画像共享相同的"姓名"或"背景故事"字段，系统应自动重新生成重复项 |

---

### Epic 3: 沉浸式模拟调研 (Simulation & Role-Playing)

**Owner**: Agent C (Synthetic Respondent)

#### Story 3.1: 角色带入与问卷填答

> **As a** 虚拟受访者,  
> **I want** 严格按照分配给我的 Persona 进行思考和回答，  
> **So that** 产生的数据能够反映真实人类在特定背景下的反应。

**Acceptance Criteria (EARS Notation)**:

| 类型 | 描述 |
|------|------|
| State-driven | 回答问卷时，系统应将 Agent 的知识库限制为仅分配 Persona 合理范围内的内容（如非技术用户不应了解技术术语） |
| Event-driven | 当呈现选择题时，系统应根据 Persona 的"偏好逻辑"字段选择选项 |
| Ubiquitous | 系统应以结构化键值对格式输出响应（如 `{"question_id": 1, "choice": "B", "reasoning": "..."}`） |

#### Story 3.2: 深度虚拟访谈

> **As a** 调研员,  
> **I want** 对虚拟用户进行多轮追问，  
> **So that** 我能挖掘出封闭式问题无法涵盖的深层动机。

**Acceptance Criteria (EARS Notation)**:

| 类型 | 描述 |
|------|------|
| Optional | 选择交互模式时，系统应为开放式问题启动多轮对话 |
| Unwanted | 如果对话超过 5 轮，系统应自动总结观点并结束对话以节省 token |

---

### Epic 4: 全量数据挖掘 (Data Ingestion & Analysis)

**Owner**: Agent D (Insight Hunter) & Mods

#### Story 4.1: 外部真实数据导入 (Mod 实现)

> **As a** 数据分析师,  
> **I want** 导入历史客服记录或 App Store 评论，  
> **So that** 我可以将虚拟用户的反馈与真实用户的吐槽进行综合分析。

**Acceptance Criteria (EARS Notation)**:

| 类型 | 描述 |
|------|------|
| Event-driven | 当通过数据导入 Mod 上传文件（CSV/TXT）时，系统应解析并清理文本数据 |
| Unwanted | 如果文件格式不兼容，系统应返回明确错误消息，说明支持的格式 |

#### Story 4.2: 情感分析与痛点聚类

> **As a** 产品决策者,  
> **I want** 看到一份可视化的分析报告，包含痛点优先级排序，  
> **So that** 我可以决定下一个迭代优先修复什么。

**Acceptance Criteria (EARS Notation)**:

| 类型 | 描述 |
|------|------|
| Event-driven | 当收集到所有模拟数据后，系统应执行聚类分析，识别前 3 个用户痛点 |
| Ubiquitous | 系统应生成包含定量图表（模拟）和定性引言（模拟和真实）的 Markdown 报告 |
| State-driven | 生成洞察时，系统应交叉引用合成数据与上传的真实数据（如果有）以突出差异 |

---

### Epic 5: 架构与协作 (Infrastructure & Orchestration)

#### Story 5.1: OpenAgents 任务编排

> **As a** 开发者,  
> **I want** 通过 OpenAgents 的机制自动串联各 Agent，  
> **So that** 我只需要点击一次"开始"，流程即可自动流转。

**Acceptance Criteria (EARS Notation)**:

| 类型 | 描述 |
|------|------|
| State-driven | 当模拟阶段运行时，系统应管理多个 Agent C 实例的并发执行（批处理） |
| Ubiquitous | 系统应维护共享上下文内存，允许 Agent D 访问 Agent B 创建的原始 Personas |
| Event-driven | 当任何 Agent 发生严重错误时，系统应记录事件并在终止流程前尝试重试 |

---

## 2. 数据结构规范 (Data Schemas)

为了确保 Agent 间协作顺畅，规定以下核心数据交换格式：

### 2.1 Persona Schema (Agent B Output → Agent C Input)

```json
{
  "id": "user_001",
  "demographics": {
    "age": 28,
    "gender": "Female",
    "occupation": "UX Designer",
    "location": "Shanghai"
  },
  "psychographics": {
    "traits": ["Detail-oriented", "Anxious", "Price-sensitive"],
    "pain_points": ["Slow loading times", "Cluttered UI"],
    "goals": ["Improve work efficiency"]
  },
  "current_context": "Feeling stressed due to a deadline."
}
```

### 2.2 Survey Response Schema (Agent C Output → Agent D Input)

```json
{
  "respondent_id": "user_001",
  "survey_id": "survey_alpha",
  "responses": [
    {
      "q_id": 1,
      "type": "scale_1_5",
      "value": 4,
      "rationale": "The feature is good but a bit expensive."
    },
    {
      "q_id": 2,
      "type": "open_text",
      "value": "I would like a dark mode."
    }
  ]
}
