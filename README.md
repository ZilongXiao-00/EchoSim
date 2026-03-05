# EchoSim

## 视频演示

| 平台 | 链接 |
|------|------|
| B站 | [EchoSim 功能演示](https://www.bilibili.com/video/BV1KakFBSE5P/) |
| YouTube | [EchoSim Demo](https://youtu.be/GMoQi9y_ceI) |

<div align="center">

[![MIT License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![OpenAgents](https://img.shields.io/badge/Powered%20by-OpenAgents-orange.svg)](https://github.com/aitomatic/openagents)
[![Network ID](https://img.shields.io/badge/Network-MultiAgentChatroom-blue.svg)](./openagents/EchoSim/network.yaml)

</div>

## 📋 项目概述

### 项目名称与标识
- **项目名称**：EchoSim
- **Network Name**：`Mirrorswarm-network` 
- **Network ID**：`EchoSim` 
- **网络模式**：Centralized

### 一句话简介
EchoSim 是一个基于 OpenAgents 驱动的**自动化市场调研框架**，通过 6 个智能体的协作编排，实现从问卷设计、质量审核、用户画像生成到高保真模拟填答及洞察抽取的**完整调研生命周期自动化**。

### 目标用户
- 🎯 **产品经理**：快速验证产品假设，收集用户反馈
- 📊 **市场研究人员**：低成本进行大规模用户调研
- 🚀 **创业者**：在资源有限的情况下快速测试市场需求
- 🔬 **研究人员**：需要合成数据进行社会科学研究

### 使用场景
- ✅ 新产品概念测试（如：折叠屏手机购买意向调研）
- ✅ 竞品分析与市场定位
- ✅ 用户痛点挖掘与需求验证
- ✅ 广告文案 A/B 测试前期筛选
- ✅ 用户体验（UX）设计决策支持

---

## 🏗️ 技术架构

### 技术栈
| 组件 | 技术 | 说明 |
|------|------|------|
| **框架** | OpenAgents 0.8.5+ | 多智能体编排平台 |
| **语言** | Python 3.8+ | 核心逻辑与工具开发 |
| **传输协议** | gRPC + HTTP | 双协议支持，gRPC 为推荐协议 |
| **数据存储** | SQLite (network.db) | 轻量级本地持久化 |
| **UI** | Studio (内置) | 基于 Web 的可视化管理界面 |
| **并发引擎** | asyncio + httpx | 异步高并发模拟池 |

### Agent Network 设计思路

**架构模式**：**审核驱动的流水线 + 星型协作**

```
┌─────────────────────────────────────────────────────────────────────┐
│                          EchoSim 工作流                              │
└─────────────────────────────────────────────────────────────────────┘

   用户输入                ┌──────────────┐
 (调研主题) ────────────> │   Agent A    │  调研架构师
                          │Survey Architect│ (市场情报扫描)
                          └───────┬────────┘
                                  │ [SURVEY_TASK_INIT]
                                  ▼
                          ┌──────────────┐
                          │   Agent E    │  问卷审核员
                          │Survey Auditor│ (质量把关)
                          └───┬──────┬───┘
                               │      │
           [REJECTED] ◄────────┘      └─────────> [APPROVED]
                 │                                 │
                 └────────> 修订循环 (最多2次)     │
                                                   ▼
                                          ┌──────────────┐
                                          │   Agent B    │  画像生成工厂
                                          │Persona Factory│
                                          └───────┬──────┘
                                                  │ [PERSONA_BATCH_READY]
                                                  ▼
                                          ┌──────────────┐
                                          │   Agent F    │  记忆管理器
                                          │Memory Manager│ (向量数据库)
                                          └───────┬──────┘
                                                  │ [MEMORY_STORED]
                                                  ▼
                                          ┌──────────────┐
                                          │   Agent C    │  虚拟受访者
                                          │Synthetic Resp│ (并发模拟池)
                                          └───────┬──────┘
                                                  │ [SIMULATION_COMPLETE]
                                                  ▼
                                          ┌──────────────┐
                                          │   Agent D    │  洞察分析师
                                          │Insight Hunter│
                                          └───────┬──────┘
                                                  │
                                                  ▼
                                             最终报告
```

### 核心特性
- 🔒 **质量保证机制**：Agent E 审核驱动，防止低质量问卷流入下游
- 🔄 **防死锁设计**：最多 2 次修订限制，强制通过机制
- 🧠 **动态记忆存储**：Agent F 将生成的用户画像持久化到向量数据库，支持后续召回与复用
- 🌐 **实时情报采集**：market_scanner 工具抓取 Google News、Reddit、Hacker News
- ⚡ **高并发模拟引擎**：sim_worker_pool 支持异步批量调用，实时监控并发峰值
- 📡 **频道化通信**：基于 Workspace Messaging Mod 的 4 频道隔离
- 🔖 **任务追踪系统**：task_id + revision 版本管理，端到端可追溯
- 🎨 **结构化协议**：[SURVEY_TASK_INIT]、[SURVEY_APPROVED]、[PERSONA_BATCH_READY]、[MEMORY_STORED] 等协议消息规范

---

## 🤖 智能体设计

### Agent 网络拓扑

| Agent ID | 角色名称 | 核心职责 | 工具依赖 | 输入频道 | 输出频道 |
|----------|---------|---------|---------|---------|---------|
| **Agent A** | 调研架构师<br>(Survey Architect) | • 理解调研需求<br>• 扫描市场情报<br>• 设计问卷结构 | market_scanner | survey-requests | persona-db |
| **Agent E** | 问卷审核员<br>(Survey Auditor) | • 质量把关<br>• 方法论审核<br>• 防死锁控制 | - | persona-db | persona-db |
| **Agent B** | 画像生成工厂<br>(Persona Factory) | • 解析目标受众<br>• 批量生成用户画像<br>• 注入背景与偏好 | - | persona-db | persona-db |
| **Agent F** | 记忆管理器<br/>(Memory Manager) | • 将画像存入向量库<br/>• 确认存储状态 <br/>• 监听 persona-db<br/> | store_persona_to_memory<br/>retrieve_similar_personas<br/>update_persona_history | persona-db | persona-db |
| **Agent C** | 虚拟受访者<br>(Synthetic Respondent) | • 加载画像角色扮演<br>• 高保真模拟填答<br>• 并发批量执行 | sim_worker_pool | persona-db | field-work |
| **Agent D** | 洞察分析师<br>(Insight Hunter) | • 收集模拟数据<br>• 定量+定性分析<br>• 生成 Markdown 报告 | - | field-work | insight-reports |

### 多 Agent 协作机制

#### 1️⃣ 频道化通信（Workspace Messaging Mod）
EchoSim 采用 **4 个专用频道** 隔离不同阶段的工作流：

| 频道名称 | 用途 | 参与者 |
|---------|------|-------|
| **#survey-requests** | 用户发布调研主题 | User → Agent A |
| **#persona-db** | 问卷设计、审核、画像传递 | Agent A ⇄ Agent E → Agent B→ Agent F |
| **#field-work** | 模拟填答数据汇总 | Agent C → Agent D |
| **#insight-reports** | 最终分析报告发布 | Agent D → User |

#### 2️⃣ 结构化协议消息
所有 Agent 间通信遵循**严格的协议格式**，避免误触发：

```json
// 示例：Agent A 发布问卷
[SURVEY_TASK_INIT]
{
  "task_id": "survey_20260115_102030",
  "revision": 0,
  "topic": "折叠屏手机购买意向",
  "target_audience": [...],
  "survey_config": {...}
}

// Agent E 审核通过
[SURVEY_APPROVED]
{"task_id": "survey_20260115_102030", "revision": 0}

// Agent F 存储确认
[MEMORY_STORED]
{"task_id": "survey_20260115_102030", "stored_count": 2, "status": "ok"}

// Agent C 完成模拟
[SIMULATION_COMPLETE]
{"task_id": "survey_20260115_102030", "respondents": ["user_01", "user_02"]}
```

#### 3️⃣ 传输层优化
- **推荐协议**：gRPC（高性能、支持流式传输）
- **备用协议**：HTTP（兼容性、Studio UI）
- **端口配置**：
  - gRPC: 8600
  - HTTP: 8700（含 Studio UI + MCP + A2A）

### OpenAgents 高级特性应用

✅ **Workspace Messaging Mod**  
实现频道系统、消息持久化、历史记录查询（`get_channel_history`）

✅ **Custom Tools 系统**  
自研工具无缝集成到 Agent 配置：
- `market_scanner.get_market_intel(query)` - 市场情报扫描
- `sim_worker_pool.simulate_survey_batch(...)` - 并发模拟引擎
- `vector_db.store_persona(...)` - 用户画像向量存储
- `vector_db.retrieve_personas(...)` - 相似画像召回
- `vector_db.update_history(...)` - 参与历史更新

✅ **CollaboratorAgent 类型**  
所有 Agent 基于 `openagents.agents.collaborator_agent.CollaboratorAgent`，支持：
- 事件驱动触发（`react_to_all_messages: true`）
- 工具调用能力
- 指令注入（instruction）

---

## 💡 协作场景与创新点

### 协作场景描述

**场景示例：折叠屏手机购买意向调研**

1. **需求输入阶段**  
   产品经理在 `#survey-requests` 发送："调研用户对折叠屏手机的购买意向"

2. **智能问卷设计**  
   Agent A 自动：
   - 调用 `market_scanner` 扫描 Google News（竞品动态）、Reddit（用户吐槽）、Hacker News（技术质疑）
   - 基于情报设计问卷，包含：价格敏感度、使用场景、顾虑因素等维度
   - 发布到 `#persona-db`

3. **质量审核循环（Agent E Gatekeeper）**  
   Agent E 作为“方法论审计员”，对 Agent A 输出的问卷进行质量把关，只允许合格问卷进入下游链路。

   - ✅ 通过 → 产出 `[SURVEY_APPROVED]`，触发 Agent B 生成用户画像
   - ❌ 拒绝 → 产出 `[SURVEY_REJECTED]` + 可执行修改建议，触发 Agent A 按同一 `task_id` 修订（`revision+1`，最多 2 次）

4. **画像生成**  
   Agent B 解析目标受众（如：25-35岁科技爱好者），批量生成详细画像：
   ```json
   {
     "id": "user_01",
     "name": "张明",
     "age": 28,
     "role": "软件工程师",
     "traits": ["追求新技术", "对价格敏感"],
     "context": "目前使用 iPhone 13，考虑换机"
   }
   ```

5. **记忆存储（Agent F 动态记忆库）**  
   Agent F 监听 `[PERSONA_BATCH_READY]`，对每个人物画像调用 `store_persona_to_memory`，将其存入向量数据库 `openagents/local_vector_db/persona_db/chroma.sqlite3`，并发布 `[MEMORY_STORED]` 确认存储状态。

6. **高保真模拟填答**  
   Agent C 调用 `sim_worker_pool`：

   - 并发模拟 N 个画像（如 N=100）
   - 每个画像严格从其背景出发回答问题
   - 监控并发峰值（如：配置 max_concurrency=8）

7. **洞察分析**  
   Agent D 自动分析：
   - **定量**：选择题频次统计、价格区间偏好
   - **定性**：提取主题（"担心折痕影响寿命"、"期待大屏办公"）
   - 生成 Markdown 报告发布到 `#insight-reports`

8. **结果交付**  
   产品经理在 Studio UI 查看报告，**总耗时 < 5 分钟**

---

### 创新点

#### 1. **动态记忆存储与人物画像复用**

- **传统痛点**：每次调研生成新用户，调研完即销毁，无法沉淀用户资产
- **EchoSim 解决方案**：
  - 引入 **Agent F（Memory Manager）**，监听 `[PERSONA_BATCH_READY]` 消息
  - 将每个生成的用户画像实时存入 **ChromaDB 向量数据库**（`store_persona_to_memory`）
  - 实现人物画像的长期保存、结构化存储与元数据管理
  - 为后续“相似画像召回”、“跨调研用户复用”打下基础

#### 2. **审核驱动的质量保证**
- 传统 AI 调研缺乏质量把控，易产生无效问卷
- EchoSim 引入 **Agent E 审核员**，从方法论角度评估：
  - 是否存在引导性问题
  - 是否覆盖核心维度
  - 是否适配目标受众
- **防死锁机制**：最多 2 次修订，避免无限循环

#### 3. **实时市场情报驱动**
- 不依赖人工经验，**自动抓取实时数据**：
  - Google News：竞品发布、行业趋势
  - Reddit：真实用户痛点与抱怨
  - Hacker News：技术社区质疑与期待
- 问卷设计基于**真实市场反馈**而非主观假设

#### 4. **可扩展并发模拟引擎**
- 传统方案：逐个调用 LLM（样本数 N 增大时，总耗时近似线性增长）
- EchoSim 方案：
  - 使用 `asyncio` + `httpx.AsyncClient` 实现批量异步并发调用（`create_task` + `gather`）
  - 通过 `asyncio.Semaphore` 限制最大并发（`max_concurrency`），降低触发限流（429）的概率
  - 内置自动重试：遇到 429 优先遵循 `Retry-After`，否则采用退避等待 + 抖动（jitter）
  - 并发观测与诊断：记录 `_MAX_ACTIVE_TASKS`，并在返回中输出 `concurrency_report`（configured / observed）
  - 兼容运行环境：当宿主环境已有 event loop 时，使用线程 + 新 event loop 执行，避免 asyncio 冲突
- **性能收益**：在并发度为 `k` 时，整体耗时可从串行的 O(N) 缩短到接近 O(N/k) 的量级（受模型延迟与限流影响）


#### 5. **任务版本追踪系统**
- 每个调研任务分配唯一 `task_id`（如：`survey_20260115_102030`）
- `revision` 字段追踪修订历史（0 → 1 → 2）
- 端到端可追溯：从问卷设计到最终报告

#### 6. **频道化隔离与协议严格化**
- 传统多 Agent 系统易产生"串话"问题
- EchoSim 通过：
  - **频道隔离**：4 个专用频道各司其职
  - **协议消息**：`[SURVEY_TASK_INIT]` 等前缀标记，避免误触发
  - **硬性规则**：Agent 只能在指定频道发言

---

## 🎯 实际应用价值

### 解决的问题

| 传统市场调研痛点 | EchoSim 解决方案 | 效果 |
|----------------|-----------------|------|
| ⏰ **周期长**（2-4 周） | 自动化流程 | ⚡ 5-30 分钟完成 |
| 💰 **成本高**（$3-10K） | 零人工成本，仅 API 费用 | 💰 成本降低 95%+ |
| 👥 **样本偏差大** | 合成画像覆盖多元人群 | 📊 减少招募偏差 |
| 🔁 **难以重复验证** | 代码化调研，一键重跑 | 🔬 支持迭代实验 |
| 📉 **响应率低**（<10%） | 模拟受访者 100% 响应 | ✅ 数据完整性保证 |

### 适用场景矩阵

| 场景类型 | 适用性 | 推荐理由 |
|---------|-------|---------|
| 🚀 **MVP 验证** | ⭐⭐⭐⭐⭐ | 快速测试产品假设，迭代成本低 |
| 📊 **大规模预调研** | ⭐⭐⭐⭐⭐ | 筛选核心问题后再投入真实调研 |
| 🎨 **文案/设计测试** | ⭐⭐⭐⭐ | A/B 测试前期快速排除弱方案 |
| 💊 **敏感话题探索** | ⭐⭐⭐⭐ | 合成数据保护隐私，无伦理风险 |
| 🏛️ **政策影响评估** | ⭐⭐⭐ | 模拟不同人群反应，辅助决策 |
| 📱 **真实用户调研** | ⭐⭐ | 不可替代真实用户，但可作为补充 |

### 可扩展性

#### 记忆系统扩展（Agent F 已实现存储，待扩展召回）

- 🔍 **相似画像召回**：基于语义搜索（已集成 `retrieve_similar_personas` 工具）
- 🔄 **跨调研用户复用**：唤醒历史画像参与新调研
- 📈 **用户演进追踪**：更新 `update_history` 记录参与轨迹
- 🧠 **个性化响应建模**：基于历史回答调整模拟策略

#### 横向扩展（数据源）
- 🔌 **App Store / Google Play 评论**：接入应用商店爬虫
- 🐦 **Twitter / 微博**：社交媒体情绪分析
- 📈 **电商平台评论**：京东、淘宝商品反馈
- 🎥 **视频平台弹幕**：B站、YouTube 用户态度

#### 纵向扩展（问卷类型）
- 📊 **MaxDiff 分析**：最大差异量表
- 🎲 **Conjoint 分析**：联合分析定价策略
- 🧪 **Van Westendorp PSM**：价格敏感度测试
- 📋 **NPS 调研**：净推荐值跟踪

#### 垂直扩展（行业定制）
- 🏥 **医疗健康**：患者体验调研（符合 HIPAA 合规）
- 💰 **金融服务**：风险偏好评估
- 🎓 **教育培训**：学员满意度与课程设计
- 🛒 **电商零售**：购物体验优化

---

## 🚀 开发、发布与使用说明

### 环境依赖

#### 系统要求
- **操作系统**：Windows 10/11、macOS 10.15+、Linux（Ubuntu 20.04+）
- **Python 版本**：3.8 或更高（推荐 3.10+）
- **内存**：至少 4GB RAM（推荐 8GB+）
- **磁盘空间**：500MB+

#### 依赖包
- **OpenAgents**：0.8.5+
- **httpx**：异步 HTTP 客户端
- **requests**：market_scanner 工具依赖
- **SQLite**：内置，无需额外安装

---

### 安装与运行步骤

#### 1️⃣ 克隆代码仓库

```bash
git clone https://github.com/ZilongXiao-00/EchoSim.git
cd EchoSim
```

#### 2️⃣ 安装 OpenAgents和相关依赖

**选项 A：通过 pip 安装（推荐）**
```bash
pip install openagents>=0.8.5
pip install chromadb
pip install -U sentence_transformers
```

**选项 B：从源码安装（开发者模式）**
```bash
cd openagents
pip install -e .
```

#### 3️⃣ 配置环境变量

**⚠️ 安全提示**：请勿将 API 密钥提交到 Git 仓库！建议使用 `.env` 文件或系统环境变量管理。

**必须配置**：
```bash
# Windows (CMD)
set OPENAI_API_KEY=sk-your-api-key-here

# Windows (PowerShell)
$env:OPENAI_API_KEY="sk-your-api-key-here"

# macOS / Linux
export OPENAI_API_KEY="sk-your-api-key-here"
```

**可选配置**：
```bash
# 自定义 API 端点（如使用 Azure OpenAI / MiniMax / 其他兼容服务）
export OPENAI_BASE_URL="https://api.minimax.chat/v1"

# 自定义模型名称
export DEFAULT_LLM_MODEL_NAME="gpt-4o-mini"
```

#### 4️⃣ 启动 Agent Network &&  Agent（open 7 terminal）

```bash
cd openagents/EchoSim
openagents-cli network start
openagents agent start ./EchoSim/agents/Agent_A_SurveyArchitect.yaml
openagents agent start ./EchoSim/agents/Agent_B_generator.yaml
openagents agent start ./EchoSim/agents/Agent_C_Simulator.yaml
openagents agent start ./EchoSim/agents/Agent_D_Analyst.yaml
openagents agent start ./EchoSim/agents/Agent_F_Memory.yaml
openagents agent start ./EchoSim/agents/Agent_E_SurveyAuditor.yaml
```

**预期输出**：

```
[INFO] Loading network configuration from network.yaml
[INFO] Starting gRPC transport on port 8600
[INFO] Starting HTTP transport on port 8700
[INFO] Studio UI available at http://localhost:8700/studio
[INFO] Network MultiAgentChatroom (chatroom-1) started successfully
```





#### 5️⃣ 访问 Studio UI

在浏览器打开：**http://localhost:8700/studio**

**首次使用提示**：
- 如果网络配置了密码，需要先初始化管理员密码：
  ```bash
  curl -X POST http://localhost:8700/api/network/initialize/admin-password \
    -H "Content-Type: application/json" \
    -d '{"password": "your_secure_password"}'
  ```

---

### 快速体验

#### 场景：调研折叠屏手机购买意向

**Step 1：在 Studio UI 进入 `#survey-requests` 频道**

**Step 2：发送消息**
```
调研用户对折叠屏手机的购买意向
```

**Step 3：观察自动化流程**

你将在不同频道看到 Agent 依次工作：

1. **#survey-requests**  
   ```
   [Agent A] I have scanned the market and designed the survey.
   ```

2. **#persona-db**  
   ```
   [SURVEY_TASK_INIT]
   {"task_id":"survey_20260115_103045", "revision":0, ...}
   
   [SURVEY_APPROVED]
   {"task_id":"survey_20260115_103045", "revision":0}
   
   [PERSONA_BATCH_READY]
   {"task_id":"survey_20260115_103045", "personas":[...]}
   ```

3. **#field-work**  
   ```
   {"task_id":"survey_20260115_103045", "responses_batch":[...]}
   
   [SIMULATION_COMPLETE]
   {"task_id":"survey_20260115_103045", "respondents":["user_01","user_02"]}
   ```

4. **#insight-reports**  
   ```markdown
   # Survey Analysis Report: survey_20260115_103045
   
   ## Executive Summary
   基于 2 个合成用户画像的模拟调研结果...
   
   ## Key Findings
   ### Quantitative Analysis
   - Q1 价格接受度：50% 选择 "$1000-1500"
   
   ### Qualitative Themes
   1. **耐用性担忧**："担心折痕影响长期使用"
   2. **大屏生产力**："期待大屏办公和多任务处理"
   ...
   ```

**Step 4：查看完整报告**

总耗时：**约 5-10 分钟**（取决于 LLM API 响应速度）

---

### 关键配置说明

#### 调整并发数（提升模拟速度）

编辑 `openagents/EchoSim/agents/Agent_C_Simulator.yaml`：

```yaml
instruction: |
  ...
  3) Call tool `simulate_survey_batch` with:
     - max_concurrency = 8  # 改为 16 或 32（注意 API 限流）
     - timeout_s = 30
  ...
```

#### 自定义频道（扩展工作流）

编辑 `openagents/EchoSim/network.yaml`：

```yaml
mods:
  - name: openagents.mods.workspace.messaging
    config:
      default_channels:
        - name: data-collection  # 新增数据采集频道
          description: Raw data from external sources
```

#### 更换 LLM 模型

```bash
# 使用 OpenAI GPT-4
export DEFAULT_LLM_MODEL_NAME="gpt-4"

# 使用 Claude（需兼容 OpenAI API 格式）
export OPENAI_BASE_URL="https://api.anthropic.com/v1"
export DEFAULT_LLM_MODEL_NAME="claude-3-opus-20240229"
```

---

### 常见问题排查

#### ❌ 错误：`OPENAI_API_KEY is empty`

**原因**：环境变量未配置  
**解决**：按照上述"配置环境变量"步骤设置

---

#### ❌ 错误：`429 Too Many Requests`

**原因**：API 速率限制  
**解决**：
- 降低 `max_concurrency`（如从 16 改为 4）
- 等待速率限制重置（通常 1 分钟）

---

#### ❌ Agent 无响应

**排查步骤**：
1. 检查 `openagents/EchoSim/logs/` 目录下的日志文件
2. 确认 gRPC/HTTP 端口未被占用（8600/8700）
3. 验证 `network.yaml` 配置正确

---

#### ❌ Studio UI 无法访问

**解决**：
- 确认防火墙允许 8700 端口
- 检查 `network.yaml` 中 `serve_studio: true`
- 尝试使用 `http://127.0.0.1:8700/studio`

---

## 📁 项目结构

```
EchoSim/
├── README.md                          # 本文档
├── LICENSE                            # MIT 许可证
├── .gitignore                         # Git 忽略配置
├── Requirements.md                    # 需求文档
│
├── openagents/                        # OpenAgents 框架源码（可选）
│   ├── custom_tools/                  # 自研工具集
│   │   ├── __init__.py
│   │   ├── market_scanner.py          # 市场情报扫描工具
│   │   └── sim_worker_pool.py         # 并发模拟引擎
│   │
│   └── EchoSim/                       # EchoSim Agent Network
│       ├── network.yaml               # 网络配置（端口、传输协议、频道）
│       ├── network.db                 # SQLite 数据库（消息、状态）
│       ├── README.md                  # 网络简介
│       │
│       ├── agents/                    # Agent 定义目录
│       │   ├── Agent_A_SurveyArchitect.yaml   # 调研架构师
│       │   ├── Agent_E_SurveyAuditor.yaml     # 问卷审核员（质量保证）
│       │   ├── Agent_B_generator.yaml         # 画像生成工厂
│       │   ├── Agent_C_Simulator.yaml         # 虚拟受访者（并发池）
│       │   ├── Agent_D_Analyst.yaml           # 洞察分析师
│				│		└── Agent_F_Memory.yaml            # 记忆管理器（向量存储）
│       │
│       ├── config/                    # 配置文件目录
│       ├── mods/                      # 自定义 Mod 目录（如有）
│       ├── tools/                     # Agent 专用工具（如有）
│       ├── events/                    # 事件订阅配置（如有）
│       └── logs/                      # 运行日志目录
│
└── .env.example                       # 环境变量模板（需创建）
```

---
## 🤝 团队与分工
#### ZilongXiao-00 @ xiaozl_00@foxmail.com

**个人介绍**：
测试开发工程师，AI 爱好者。擅长挖掘前沿技术落地场景，专注于多智能体协作（Multi-Agent Systems）与自动化流程重构。

**项目贡献**：

1. 项目发起与构思：独立提出 EchoSim 项目概念，通过 AI 合成样本解决传统调研“慢、贵、难”的痛点，定义了“模拟受访者”与“实时市场情报驱动”的核心产品逻辑。

2. 多 Agent 协作工作流搭建：

- 架构设计：主导设计了 A/B/C/D 四个智能体的分工协议，建立了基于 Workspace Messaging Mod 的四频道隔离通信机制。
- 🤖Agent A (Architect)：设计了基于实时情报（market_scanner）的动态问卷生成逻辑，确保调研维度的时效性。

- 🎨Agent B (Factory)：构建了高保真用户画像生成引擎，实现从人口统计学到心理动机的深度刻画。

- 🚀Agent C (Simulator)：主导开发了基于异步 IO 的 sim_worker_pool，实现了工业级的 LLM 并发填答能力。

- 📊Agent D (Analyst)：定义了定性与定量结合的报告生成模板，确保输出洞察的可落地性。

3. 技术路线与升级方案：规划了项目的演进蓝图，包括纵向的专业调研方法论集成（如 MaxDiff、Conjoint）以及横向的多源数据接入。

#### YechengJiao @ Yecheng@u.nus.edu｜Scofield213@gmail.com

**个人介绍**：  
新加坡国立大学（NUS）机械工程博士研究生，研究方向聚焦于**多加工机器人协作**与**能耗预测与优化**。同时关注多智能体协作（Multi-Agent Systems）在复杂工程系统中的应用，致力于将智能算法与真实制造场景深度融合。

**项目贡献**：

1. 项目体系完善与流程强化：  
   在原有 ABCD Agents 基础上，引入 **Agent E（Survey Auditor）** 审计角色，构建“审核驱动型”工作流，对问卷设计阶段进行方法论与质量把关，形成 **设计—审核—修订—放行** 的标准化闭环，有效避免低质量问卷进入下游模拟环节。

2. 多 Agent 协作工作流升级：

- 架构优化：在原有 A/B/C/D 协作模型上扩展为 **A/B/C/D/E 五智能体体系**，解决多 Agent 在非职责频道“插嘴”的稳定性问题。  

- 🤖 Agent A (Architect)：保留基于实时情报（market_scanner）的动态问卷生成逻辑，并与 Agent E 的审核流程深度耦合，形成可追溯的问卷版本管理机制。  

- 🛡️ Agent E (Auditor)：新增设计并落地问卷审核与防死锁控制策略，支持“最多两次修订 + 强制放行”机制，在保证质量的同时避免流程阻塞。    

- 🚀 Agent C (Simulator)：对原有串行模拟流程进行工程级重构，开发并集成 `sim_worker_pool` 工具，基于 `asyncio + httpx` 实现 **受控并发模拟引擎**，支持：
  - 并发上限控制（Semaphore）
  - 自动重试与指数退避
  - 并发峰值监控  
  - 显著提升大规模画像场景下的执行效率与系统吞吐能力，将 EchoSim 升级为**可扩展、可维护的多智能体系统**。
  
3. 技术路线与升级方案：  
   在原有演进蓝图基础上，补充了**审核驱动流程设计**与**工业级并发模拟能力**两条核心技术主线。
   
#### Pangpang526 @ wpengyu05@gmail.com
   
   **个人介绍**：  
   AI 大模型工程师，专注于多智能体系统、模型高质量数据集微调处理与企业级RAG应用。擅长将前沿 AI 技术转化为可落地的产品化解决方案。
   
   **项目贡献**：
   
   1. **Agent B（Persona Factory）优化与扩展**：
      - 重构了 Agent B 的触发逻辑，确保其**仅监听 `[SURVEY_APPROVED]` 消息**，避免对未审核问卷产生响应。
      - 将画像生成规模从固定 2 个扩展为**动态可配置（10-20 个）**，支持更丰富的用户群体模拟。
      - 优化了画像生成提示词，确保输出结构标准化、字段完整（id, name, age, role, traits, context）。
   
   2. **Agent F（Memory Manager）设计与实现**：
      - **问题识别**：解决了传统调研中“用户画像零沉淀、无法复用”的痛点。
      - **解决方案**：设计了基于向量数据库的长期记忆存储系统，监听 `[PERSONA_BATCH_READY]` 消息，自动将生成的用户画像存入 **ChromaDB**。
      - **核心功能**：
        - 实时存储：调用 `store_persona_to_memory` 将画像结构化存储至向量库（`openagents/local_vector_db/persona_db/chroma.sqlite3`）
        - 确认机制：发布 `[MEMORY_STORED]` 消息，确保存储状态可追溯
        - 工具集成：实现了 `retrieve_similar_personas` 与 `update_persona_history` 工具，支持后续召回与历史更新
      - **创新价值**：首次在自动化调研框架中引入**动态记忆存储**，为后续“跨调研用户复用”、“相似画像召回”打下基础，实现用户资产的长期沉淀。
   
   3. **技术债务清理与架构优化**：
      - 统一了 Agent 间的协议消息格式，确保 `[PERSONA_BATCH_READY]` 和 `[MEMORY_STORED]` 的标准化输出。
      - 增强了系统的可扩展性，为未来“个性化响应建模”、“用户演进追踪”提供了数据基础。
---

## 🚀 遇到的挑战与解决方案

#### 1. Agent 插嘴

- **问题阐述**：  
早期多 Agent 在 `react_to_all_messages: true` 的条件下，可能对非职责频道消息产生响应（跨频道“串话”），引发误触发、重复输出与流程污染。

- **解决方案**：  
  通过“协议前缀 + 频道护栏 + 幂等去重”三层治理，系统性消除插嘴：

  1) **协议前缀触发**：所有关键阶段仅响应指定前缀（如 `[SURVEY_TASK_INIT]` / `[PERSONA_BATCH_READY]` / `[SIMULATION_COMPLETE]`），其余消息静默忽略。  
  2) **Channel Guard**：在每个 Agent 指令中加入硬性频道校验，只允许从指定频道触发；非目标频道事件一律 `silent ignore`。  
  3) **Idempotency 去重**：对关键输出（如 Agent D 报告）引入 `task_id` 级去重检查，确保同一任务最多输出一次，避免网络重放或重复事件导致二次发言。

#### 2. 尝试联网搜索时遇到了安全机制问题
- **问题阐述**：
在尝试联网搜索时遇到了安全机制问题： Agent 确实听懂了指令，并且试图调用搜索工具紧接着工具调用，Agent A 发送了一条消息：
"I apologize, but I don't have access to live web search capabilities..."
当它生成工具调用的代码后，它的“自我认知”部分立刻跳出来反驳自己，生成了道歉信，导致整个流程被中断（调用了Tool: finish）。它没有等待搜索结果回来，就自己把对话结束了。

- **解决方案**：
尝试了修改提示词，发现不稳定后，采用了让Agent调用python工具‘market_scanner’，通过三个不同的渠道（Google News、Reddit 和 Hacker News）抓取特定话题的最新动态，并将结果整合为标准化的数据格式。

#### 3. 生成用户画像速度慢

- **问题阐述**：  
Agent C 早期采用串行逐个 persona 调用 LLM，样本数增大后总耗时线性增长，难以满足实际调研场景的规模需求。
- **解决方案**：  
引入 `sim_worker_pool` 并封装为自定义工具 `simulate_survey_batch`，将 persona 填答改为**批量并行模拟**，通过 `max_concurrency` 控制并发上限以兼顾吞吐与限流稳定性。  
效果：在相同模型与问题规模下，整体耗时显著下降，使得 50/100+ personas 的模拟具备实际可用性。

## 🤝 贡献

欢迎提交 Pull Request 或 Issue！

### 贡献方向
- 🛠️ **新增工具**：App Store 评论爬虫、Twitter API 集成
- 🎨 **UI 优化**：Studio 插件、可视化报告
- 📚 **文档完善**：教程、案例库
- 🐛 **Bug 修复**：错误处理、性能优化

### 提交规范
- Fork 本仓库
- 创建特性分支 (`git checkout -b feature/AmazingFeature`)
- 提交更改 (`git commit -m 'Add some AmazingFeature'`)
- 推送到分支 (`git push origin feature/AmazingFeature`)
- 开启 Pull Request

---

## 📝 许可证

本项目采用 **MIT 许可证** 开源。

```
MIT License

Copyright (c) 2026 ZilongXiao-00

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 📧 联系方式

- **项目维护者**：ZilongXiao-00, Yecheng Jiao,pangpang526
- **GitHub**：https://github.com/ZilongXiao-00/EchoSim
- **问题反馈**：通过 GitHub Issues 提交

---

## 🌟 致谢

- [OpenAgents](https://github.com/aitomatic/openagents) - 多智能体编排框架
- 所有贡献者 @ZilongXiao-00 @YechengJiao @pangpang526

---

<div align="center">

**⚡ 让市场调研从 4 周缩短到 5 分钟 ⚡**

Made with ❤️ by the EchoSim Team

</div>
