# Sera Context Runtime & Learning OS V1

## AI 公司认知循环系统

| Field | Value |
|-------|-------|
| Version | 1.0 |
| Status | Engineering Design |
| Owner | Sera CTO |
| Layer | Runtime（横切 Memory / Organization / Workflow / Execution） |
| Dependencies | SMOP V1, Memory Engine V1, Organization OS V1, Workflow OS V1 |
| Target | DeepSeek / Trae / Codex Direct Execution |

---

# 0. Executive Summary

## 问题

Sera OPCOS 已经定义了「Memory Infrastructure（记忆基础设施）」：

- **Memory Graph** — 公司知道什么
- **Memory Engine** — 公司记住什么
- **SMOP** — 公司如何描述对象
- **Organization OS** — 公司如何组织员工
- **Workflow OS** — 公司如何自动运转

但缺少两个决定成败的东西：

1. **Context Runtime** — 一个 Agent 在执行任务时，"此刻应该知道什么、并且能按需获取更多"。
2. **Learning OS** — 一次任务的成败，如何被提炼、验证、沉淀，最终让下一个 Agent 变得更聪明。

## 一句话定义

Sera OPCOS 不是一个「AI 公司知识库」，而是一个「AI 公司认知循环系统」。

```
                 Memory
                   ↓
                 Context
                   ↓
                  Agent
                   ↓
                 Action
                   ↓
               Experience
                   ↓
                Learning
                   ↓
                  Rule
                   ↓
              Better Context   ← 闭环
```

## 本层要解决的三个核心问题

| 问题 | 现状 | 本层方案 |
|------|------|---------|
| Agent 如何拿到正确上下文 | 静态 Context Package，一次性编译 | Context Builder（初始包）+ Agent Runtime Loop（按需检索） |
| 上下文如何不爆炸 | 无预算控制 | Token Budget 硬上限 + Context Ranking 排序截断 |
| 经验如何持续进化 | 手动调用 `/memory/learn`，无验证 | Learning Engine：`confidence × 3 次独立关联 × supersedes` |

---

# 一、架构定位（修正分层模型）

## 1.1 为什么不能把 Context / Learning 硬塞成「层」

前序讨论中曾出现「六层 / 七层架构」的争议。这里给出唯一正确的答案：

**Context 和 Learning 不是「层」，它们是两种不同的东西。**

- **Context OS** 是一个**纵向层** —— 它是 Agent 与整个系统交互的入口，位于 Organization 之上。
- **Learning OS** 是一个**横切反馈环** —— 它贯穿所有层，把每一层的产出回流成 Memory。

把它们都当成"层"并列，会导致「Learning OS 和 Memory OS 谁管写入」这种无解问题。

## 1.2 正确结构

```
                    Founder (person.sera)
                        │
                 Sera Intelligence
                        │
==========================================================
  Vertical Layer 4:  Context OS        ← 本层（入口大脑）
  ─────────────────────────────────────────────────────
  - Context Builder（初始包）
  - Token Budget / Context Ranking
  - Agent Runtime Loop（Plan → Retrieve → Act → ...）
==========================================================
                        │
==========================================================
  Vertical Layer 3:  Organization OS    （AI 公司结构）
  Vertical Layer 2:  Workflow OS       （业务流程）
  Vertical Layer 1:  Execution OS      （工具/机器）
==========================================================
                        │
==========================================================
  Horizontal Base:   Memory OS          （横贯所有层）
  - SMOP（对象协议）
  - Memory Engine（SQLite + LanceDB + Filesystem）
  - Memory Graph（Entities + Relations）
==========================================================
                        │
          ┌─────────────┴─────────────┐
          │   Learning OS（反馈环）    │  ← 贯穿所有层
          │   Experience → Rule →     │
          │   Better Context          │
          └─────────────┬─────────────┘
                        │
              回流写入 Memory Graph
```

**口诀：4 个纵向层 + 1 个横向记忆底座 + 1 个学习反馈环。**

---

# 二、Canonical Memory Schema（二维矩阵）

## 2.1 解决 3 层 vs 5 层冲突

历史上存在两种记忆分层，它们不是冲突，而是两个正交维度。本层将其统一为二维模型：

### 第一维：Data State（信息处于什么生命周期）—— 5 态

```
Raw        →  未经处理的原始数据（对话原文、commit diff、邮件正文）
Processed  →  已解析的结构化片段（提取出的实体、摘要）
Structured →  已入库的 Object（SMOP Object，带 relations）
Learned    →  被提炼的经验教训（Experience / 跨任务模式）
Rule       →  被验证的组织原则（Rule，约束未来行为）
```

### 第二维：Scope（谁在使用）—— 4 域

```
Session        →  单次 Agent 会话（用完即弃）
Task           →  单个任务（Task 生命周期内有效）
Project        →  单个项目（项目存续期内有效）
Organization   →  全公司（永久，跨项目）
```

## 2.2 字段落地

每个 SMOP Object 的基类，在 SMOP V1 基础上新增两个字段：

```json
{
  "id": "project.tradespan",
  "type": "Project",
  "name": "TradeSpan",
  "data_state": "structured",
  "scope": "organization",
  "importance": 0.9,
  "confidence": 1.0,
  "...": "其余 SMOP V1 字段不变"
}
```

### `data_state` 枚举

| 值 | 含义 | 典型来源 |
|----|------|---------|
| `raw` | 原始数据 | Extractor 直接落库 |
| `processed` | 解析片段 | Entity Recognizer 输出 |
| `structured` | 完整 Object | SMOP Object store |
| `learned` | 提炼经验 | Learning Engine 输出 |
| `rule` | 验证规则 | 3 次验证后升级 |

### `scope` 枚举

| 值 | 生命周期 | 典型对象 |
|----|---------|---------|
| `session` | 会话结束即归档 | 临时查询、中间结果 |
| `task` | Task 结束即归档 | Task 执行过程数据 |
| `project` | 项目归档时归档 | Project 决策、资产 |
| `organization` | 永久 | Rule、组织级 Decision |

## 2.3 与既有 type 枚举的关系

**`data_state` + `scope` 不取代 `type`，三者正交：**

```
type        = 它是什么（Person / Project / Decision / Experience / Rule ...）
data_state  = 它有多成熟（raw / processed / structured / learned / rule）
scope       = 它在多大范围生效（session / task / project / organization）
```

一个对象可以同时是 `Experience × learned × project`，或 `Decision × structured × organization`。这消除了旧设计中"用 type 去猜生命周期"的歧义。

## 2.4 ID 命名统一（最终裁决）

**采用点分命名 `namespace.name`，废弃下划线编号格式。**

```
正确:  project.tradespan
废弃:  project_tradespan_001
```

理由：点分命名支持自然层级（`decision.tradespan.dark-ui`）、可读、且与 SMOP V1 的 `{namespace}.{name}[.{subtype}]` 规范一致。旧文档中的下划线格式标记为 `superseded`。

---

# 三、Context Runtime

## 3.1 Context Builder（中心化初始包）

### 定义

Context Builder 是 Agent 接入时的第一个动作。输入任务与角色，输出一个受预算约束的 Context Package。

```
输入:
  task_id      — Task Object ID
  agent_id     — Agent Object ID
  budget_tokens — 本次预算上限

输出:
  ContextPackage — 受 Token Budget 硬约束的知识包
```

### 构建算法

```python
def build_context(task_id, agent_id, budget_tokens):
    task    = memory.get_object(task_id)
    project = memory.traverse(task_id, "part_of", depth=1)[0]
    agent   = memory.get_object(agent_id)

    # 1. Mission（固定，预算的 10%）
    mission = compile_mission(task, project)

    # 2. 候选记忆收集
    candidates = []
    candidates += memory.query({"type": "Decision", "applies_to": project.id, "status": "active"})
    candidates += memory.query({"type": "Rule",     "applies_to": project.id, "status": "active"})
    candidates += memory.query({"type": "Experience", "related_to": project.id, "data_state": "learned"})
    candidates += memory.query({"type": "Asset",    "part_of": project.id})
    candidates += memory.query({"type": "Skill",    "depends_on": project.id})

    # 3. 过滤 superseded + 过期
    candidates = [c for c in candidates if not is_superseded(c)]
    candidates = [c for c in candidates if not is_stale(c)]

    # 4. Context Ranking 打分排序
    for c in candidates:
        c.rank_score = rank(c, agent, task)

    candidates.sort(key=lambda c: c.rank_score, reverse=True)

    # 5. Token Budget 截断
    package = {"mission": mission, "sections": {}}
    remaining = budget_tokens - count_tokens(mission)

    for section, ratio in BUDGET_ALLOCATION.items():
        limit = int(budget_tokens * ratio)
        package.sections[section] = fill_until(candidates_of(section), limit)

    return package
```

## 3.2 Context Ranking（排序打分）

### 综合评分公式

```
rank_score = w1·importance + w2·recency + w3·relation_weight + w4·confidence
```

| 分量 | 权重 | 来源 | 说明 |
|------|------|------|------|
| `importance` | 0.40 | Object 字段 | 公司战略级 > 项目级 > 参考级 |
| `recency` | 0.25 | 半衰期衰减 | 最近访问的权重更高 |
| `relation_weight` | 0.20 | relations.weight | 与当前 task/project 的关系强度 |
| `confidence` | 0.15 | Object 字段 | 可信度越高越优先 |

### Recency 半衰期衰减

```
recency = 0.5 ^ (days_since_last_access / half_life_days)

half_life_days（按 data_state 分级）:
  rule        → 90 天半衰期（组织原则，长期稳定）
  learned     → 30 天半衰期（经验教训）
  structured  → 14 天半衰期（普通对象）
  processed   → 7 天半衰期（解析片段）
  raw         → 2 天半衰期（原始数据，快速过期）
```

## 3.3 Token Budget Management

### 预算分级

| 任务复杂度 | 默认预算 | 适用场景 |
|-----------|---------|---------|
| `simple` | 4,000 tokens | 单一明确任务 |
| `standard` | 8,000 tokens | 常规开发/内容任务 |
| `complex` | 16,000 tokens | 多步、跨领域任务 |

### 分配比例（从 budget 中切分）

```yaml
budget_allocation:
  mission:                0.10   # 任务使命（固定）
  active_decisions:       0.20   # 生效决策
  active_rules:           0.15   # 生效规则
  relevant_experiences:   0.25   # 失败/成功经验（Learning 的输入）
  available_assets:       0.15   # 可用资产
  relevant_skills:        0.10   # 相关技能
  stale_markers:          0.05   # 被取代/过期标记（防止 Agent 踩旧坑）
```

### 硬约束

1. **任何 Context Package 不得超过预算上限**，超过一律按 rank_score 截断。
2. **被 `supersedes` 的对象不进入 package，只进入 `stale_markers`**，并标注 `superseded_by`。
3. 截断后，package 底部附 `truncated: true` + `omitted_count`，让 Agent 知道"还有更多没放进来"。

## 3.4 Context Package V2 Schema

```json
{
  "context_id": "ctx.tradespan-landing.20260821",
  "target_agent": "agent.frontend.engineer",
  "target_task": "task.tradespan.landing-page",
  "compiled_at": "2026-08-21T09:00:00Z",
  "budget_tokens": 8000,
  "used_tokens": 6120,
  "truncated": false,
  "omitted_count": 0,

  "mission": {
    "summary": "构建 TradeSpan 着陆页",
    "project": "project.tradespan",
    "deadline": "2026-08-25",
    "priority": "high"
  },

  "active_decisions": [
    {
      "id": "decision.tradespan.dark-ui",
      "decision": "暗色金融科技风格",
      "reason": "增强交易者信任感",
      "constraints": ["主黑 #05070A", "主题蓝 #146EFF", "避免大面积渐变"],
      "scope": "project",
      "confidence": 1.0
    }
  ],

  "active_rules": [
    {
      "id": "rule.financial.trust-first",
      "content": "金融产品可信度 > 炫技",
      "priority": "high",
      "scope": "organization"
    }
  ],

  "relevant_experiences": [
    {
      "id": "experience.video.ui-failure",
      "lesson": "纯 AI 内容缺乏 UI 可信度",
      "data_state": "learned",
      "applies_to": ["Landing Page"]
    }
  ],

  "available_assets": [
    {"id": "asset.logo.tradespan", "format": "SVG", "path": "assets/logo.svg"}
  ],

  "relevant_skills": [
    {"id": "skill.react.v18", "proficiency": "required"}
  ],

  "stale_markers": [
    {
      "id": "decision.tradespan.light-ui",
      "reason": "已被 supersedes",
      "superseded_by": "decision.tradespan.dark-ui"
    }
  ]
}
```

---

# 四、Agent Runtime Loop（Letta 式）

## 4.1 双模式架构

Sera 的 Context 不是"中心化一次性编译"或"Agent 完全自取"二选一，而是**双模式**：

```
任务开始 ──→ Context Builder ──→ 初始 Context Package（中心化）
                                       │
                                       ▼ 注入 System Prompt
===========================================================
            Agent Runtime Loop（运行时，自我管理记忆）
===========================================================
   Plan ──→ Retrieve ──→ Act ──→ Observe ──→ Reflect ──→ Learn
     │         │                             │           │
     │         └─ 按需调 MCP 工具 ────────────┘           │
     │              memory.search / object_get            │
     └──────────────← 反馈写入 ───────────────────────────┘
```

## 4.2 Loop 各阶段

| 阶段 | 动作 | 工具 |
|------|------|------|
| `Plan` | 拆解任务，判断还缺什么信息 | — |
| `Retrieve` | 按需向 Memory 检索补充上下文 | `memory.search`, `object.get` |
| `Act` | 执行（调 MCP 工具/模型推理） | GitHub / Terminal / API ... |
| `Observe` | 记录结果、成本、产出 | — |
| `Reflect` | 判断成败、提取 lesson | — |
| `Learn` | 强制回写（成功经验/失败教训） | `memory.learn` |

## 4.3 MCP 工具暴露

SMOP 作为 MCP Server `sera-memory` 暴露以下工具，供运行时 Loop 按需调用：

```json
{
  "tools": [
    {"name": "memory_search",     "desc": "语义/混合检索记忆", "args": {"query", "types?", "top_k?"}},
    {"name": "object_get",        "desc": "按 ID 获取对象",    "args": {"id"}},
    {"name": "object_store",      "desc": "写入新对象",        "args": {"entity", "relations?"}},
    {"name": "object_relate",     "desc": "建立关系",          "args": {"source_id", "target_id", "relation_type"}},
    {"name": "memory_learn",      "desc": "提交经验教训",      "args": {"task_id", "result", "lesson", "applies_to?"}},
    {"name": "memory_decision",   "desc": "记录决策",          "args": {"context", "decision", "reason"}}
  ]
}
```

## 4.4 Runtime 伪代码

```python
def agent_run(task, agent):
    # Phase 0: 中心化初始包
    ctx = build_context(task.id, agent.id, budget_for(task.complexity))
    prompt = render_system_prompt(ctx)

    # Phase 1..N: 运行时循环
    loop = AgentLoop(agent, prompt, tools=[MCPTools.sera_memory])
    observations = []

    while not loop.done:
        plan = loop.plan()

        if plan.needs_info:
            # 运行时按需检索（Letta 式 self-editing）
            plan.context = loop.retrieve(plan.missing_info)

        result = loop.act(plan)
        obs = loop.observe(result)
        observations.append(obs)

        reflection = loop.reflect(obs)
        if reflection.has_lesson:
            # 强制学习回写，不允许跳过
            loop.learn(reflection.lesson)

    return loop.outcome
```

**硬性规定：** `Learn` 阶段是 Loop 的强制出口，任务成功也要提交经验（成功路径本身就是可复用的 Skill），失败则必须提交失败模式。这保证「Memory → Context → Action → Experience → Learning」的环永远闭合。

---

# 五、Learning Engine

## 5.1 学习闭环

```
Experience（一次任务的成败）
        │
        ▼
Pattern Detection（跨任务模式识别）
        │
        ▼
Rule Extraction（提炼成可复用原则）
        │
        ▼
Validation（验证，见 5.4）
        │
        ▼
Organization Memory（升级为 Rule，写入规则层）
        │
        ▼
Better Context（下次 Context Builder 自动纳入）
```

## 5.2 Pattern Detection

```python
def detect_patterns():
    # 从近 N 天的 Experience 中找共性
    experiences = memory.query({
        "type": "Experience",
        "data_state": "learned",
        "since": "30 days ago"
    })

    # 聚类：相同 failure_mode / root_cause / lesson
    clusters = cluster_by_embedding(experiences)
    return [c for c in clusters if len(c.members) >= 2]
```

## 5.3 Rule Extraction

```python
def extract_rule(cluster):
    # 只有被反复验证的模式才值得升 Rule
    if len(cluster.members) < 3:
        return None   # 不够格，仍停留为 Experience

    return Rule(
        content      = cluster.common_lesson,
        scope        = infer_scope(cluster),   # project / organization
        source_experiences = [e.id for e in cluster.members]
    )
```

## 5.4 Validation（复用 SMOP 已有机制，不新造）

**关键决策：Validation 不发明新字段，直接复用 SMOP V1 已定义的三个机制。**

### 机制 1：`confidence` 决定初始可信度

| confidence | 来源 | 是否可直接升 Rule |
|-----------|------|------------------|
| 1.0 | 人工确认 | 是 |
| 0.9 | 规则匹配 | 是（需 1 次人工复核） |
| 0.7 | LLM 高置信 | 否（需累计验证） |
| 0.5 | LLM 推断 | 否 |
| ≤0.3 | 未验证 | 否 |

### 机制 2：`3 次独立关联` 是升 Rule 的门槛

```
一条 lesson 升级为 Rule 必须满足：
  - 被 ≥3 个「相互独立的 task/context」命中；
  - 且命中来源的 confidence ≥ 0.7；
  - 且不存在 active 状态的矛盾 Rule。

满足 → data_state: "learned" → "rule"
不满足 → 保持 "learned"，继续累计
```

### 机制 3：`supersedes` 处理冲突与废止

```
新 Rule 与旧 Rule 冲突时：
  - 新 Rule 建立关系 supersedes → 旧 Rule
  - 旧 Rule status: "active" → "deprecated"/"replaced"
  - Context Builder 查询时自动忽略被 supersedes 的 Rule

旧 Rule 过时（无新经验关联）：
  - 30 天无 access → status 降级为 "deprecated"
```

## 5.5 Experience → Rule 演化状态机

```
                    ┌──────────────┐
                    │   raw        │  原始记录
                    └──────┬───────┘
                           │ 提取实体/关系
                           ▼
                    ┌──────────────┐
                    │  processed   │  解析片段
                    └──────┬───────┘
                           │ 结构化入库
                           ▼
                    ┌──────────────┐
                    │  structured  │  Experience Object
                    └──────┬───────┘
                           │ Reflect 提炼 lesson
                           ▼
                    ┌──────────────┐
                    │  learned     │  经验教训（data_state=learned）
                    └──────┬───────┘
                           │ 3 次独立关联 + confidence≥0.7
                           ▼
                    ┌──────────────┐
                    │  rule        │  组织原则（data_state=rule）
                    └──────────────┘
```

---

# 六、Golden Path MVP

## 6.1 目标

用最小实现证明闭环，而不是做全功能系统。

```
一个 Agent 接入 → 拿到正确 Context → 完成任务 → 经验沉淀 → 另一个 Agent 能复用
```

## 6.2 纳入范围（Phase 1 必须）

| 组件 | 说明 | 技术选型 |
|------|------|---------|
| Memory Store | entities + relations + memories 三表 | **SQLite**（零配置，不用 Postgres） |
| SMOP Object | 二维矩阵字段落地 | JSON 列 + 索引 |
| Context Builder | 静态初始包 + ranking + budget | 纯函数模块 |
| Agent Runtime Loop | 最小 Plan→Act→Learn 循环 | Python 脚本 |
| Learning API | `memory.learn` + 3 次验证升级 | confidence 计数 |
| MCP Server | `sera-memory` 暴露 6 个工具 | MCP SDK |

## 6.3 排除范围（Phase 1 不做）

| 组件 | 理由 | 推迟到 |
|------|------|-------|
| LanceDB 向量 | 语义搜索非闭环必需 | Phase 2 |
| 图遍历引擎（Neo4j/pgRouting） | relations 表 + 递归 CTE 足够 | Phase 3 |
| 多源 Extractor | 手动导入可验证闭环 | Phase 4 |
| Cron Memory Builder | 日结是优化非必需 | Phase 4 |
| PostgreSQL | 违反零配置原则 | 分布式阶段 |

## 6.4 最小 API 端点

```
POST /context/build          # build_context(task_id, agent_id, budget)
POST /context/rank           # 纯排名（调试用）
GET  /object/{id}            # 对象查询
POST /object/store           # 对象写入
POST /learn                  # 经验提交 + 触发验证
POST /search                 # SQLite FTS5 关键词检索（MVP 替代向量）
GET  /stats                  # entities/relations/rules 计数
```

---

# 七、与现有层的集成

## 7.1 分层职责边界（最终裁决）

| 层 | 职责 | 不负责 |
|----|------|-------|
| **Context OS** | 此刻该知道什么、能按需取什么 | 不决定"怎么存" |
| **Memory OS** | 存什么、怎么查 | 不决定"给谁看多少" |
| **Learning OS** | 提炼、验证、升 Rule | 不直接执行任务 |
| **Organization OS** | Agent 是谁、如何分配 | 不定义业务流程 |
| **Workflow OS** | 业务流程如何串 | 不管理 Agent 档案 |
| **Execution OS** | 工具调用落地 | 不管理记忆 |

## 7.2 本层使用的 SMOP 端点

```
Context Builder  → GET /object/{id}, POST /search
Agent Runtime    → POST /search, GET /object/{id}, POST /learn, POST /decision
Learning Engine  → POST /learn（触发验证）, POST /object/store（写 Rule）
```

## 7.3 完整架构（V3 修正版）

```
                 person.sera
                      │
              Sera Intelligence
                      │
================================================
  Context OS     ← 当前任务的大脑（本层）
================================================
  Organization OS   （AI 公司结构：部门/角色/Agent）
  Workflow OS       （业务流程：Trigger/Pipeline/Approval）
  Execution OS      （工具/机器：MCP/API/Terminal）
================================================
  Memory OS     ← 横向底座（SMOP + Engine + Graph）
================================================
  Learning OS   ← 反馈环（贯穿所有层，写回 Memory）
================================================
```

---

# 八、实现路线图

## Phase 1: Golden Path（MVP）

```
目标：闭环可跑
├── SQLite 三表 + data_state/scope 字段
├── Context Builder（ranking + budget）
├── 最小 Agent Loop（Plan→Act→Learn）
├── memory.learn + 3 次验证升 Rule
├── MCP server（6 工具）
└── 验收：Agent A 任务 → 经验 → Agent B Context 中包含该经验
```

## Phase 2: Semantic Retrieval

```
目标：模糊查询
├── LanceDB 向量集成
├── Hybrid Search（RRF fusion）
├── Context Builder 接入语义候选
└── 验收：自然语言问"视频失败经验"能命中
```

## Phase 3: Graph Traversal

```
目标：关系推理
├── 递归 CTE 图遍历
├── Context Ranking 加入 relation_weight 深层传播
└── 验收：查 Project 能沿 depends_on/created_by 走 ≥3 层
```

## Phase 4: Autonomous Learning

```
目标：自动进化
├── Extractor（Obsidian/GitHub/Chat）
├── Cron Memory Builder（日结）
├── Pattern Detection 自动化
└── 验收：无人工干预，一条经验自动升 Rule
```

---

# 附录 A: 术语表

| 术语 | 定义 |
|------|------|
| Context Package | 给特定 Agent+Task 编译的受预算约束知识包 |
| Context Builder | 中心化生成初始 Context Package 的组件 |
| Agent Runtime Loop | Plan→Retrieve→Act→Observe→Reflect→Learn 循环 |
| data_state | 对象成熟度（raw/processed/structured/learned/rule） |
| scope | 对象生效范围（session/task/project/organization） |
| rank_score | 记忆排序综合分 |
| Token Budget | 单个 Context Package 的 token 硬上限 |
| Learning Engine | Experience→Rule 的验证与升级系统 |

# 附录 B: 与 SMOP V1 的差异清单

| 变更 | SMOP V1 | 本层 |
|------|---------|------|
| 基类新增 `data_state` | 无 | ✅ |
| 基类新增 `scope` | 无 | ✅ |
| ID 命名 | 点分（正确）| 明确废弃下划线格式 |
| Context Package | 静态 | + budget / truncated / stale_markers |
| Context 生成 | 仅 Builder | Builder + Runtime Loop 双模式 |
| 学习 | 手动 learn | 强制 Learn + 3 次验证升 Rule |

---

*Document Version: 1.0*
*Last Updated: 2026-08-21*
*Next: Sera Context Runtime & Learning OS Implementation Guide V1（代码实现）*