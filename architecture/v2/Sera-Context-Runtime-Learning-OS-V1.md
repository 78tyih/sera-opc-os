# Sera Context Runtime & Learning OS V1.1

## AI 公司认知循环系统

| Field | Value |
|-------|-------|
| Version | 1.1 |
| Status | Engineering Design（V1.1：吸收对抗式审查，补 authority / Root Cause 分析 / Governor 主路径 / Kernel V0） |
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
| Agent 如何拿到正确上下文 | 静态 Context Package，一次性编译 | Context Governor（中心化主路径 P0，强制注入）+ Agent Loop（辅助 P1，按需检索） |
| 上下文如何不爆炸 | 无预算控制 | Token Budget 硬上限 + Context Ranking 排序截断 |
| 经验如何持续进化 | 手动调用 `/memory/learn`，无验证 | Learning Engine：`Root Cause 分析 → confidence × 3 次独立关联 × authority 裁决` |

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
  "authority": "founder",
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

### `authority` 枚举（V1.1 新增）

权威等级解决「Rule / Decision 冲突时谁赢」的问题，优先级从高到低：

| 值 | 含义 | 优先级 | 冲突裁决 |
|----|------|--------|---------|
| `founder` | Founder 本人手写（taste / 价值观 / 战略） | 最高 | 无条件覆盖下级 |
| `organization` | 组织级沉淀（经验证升 Rule） | 高 | 覆盖 project / agent |
| `project` | 项目级决策 / 经验 | 中 | 覆盖 agent |
| `agent` | 单 Agent 推断 | 低 | 仅作参考 |

**Rule 冲突不再依赖 `supersedes` 的先后顺序，而是先比较 `authority`：高权威直接胜出；同级才用 `supersedes` 记录替代关系。**

## 2.3 与既有 type 枚举的关系

**`data_state` + `scope` + `authority` 不取代 `type`，四者正交：**

```
type      = 它是什么（Person / Project / Decision / Experience / Rule ...）
data_state = 它有多成熟（raw / processed / structured / learned / rule）
scope     = 它在多大范围生效（session / task / project / organization）
authority = 谁的判断更权威（founder / organization / project / agent）
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

## 3.1 Context Governor（中心化主路径，P0）

### 定位

Context Governor 是 Agent 接入时的**强制第一动作**，是 Sera 提供的**唯一主路径**。它必须**主动、强制**把 Founder 判断（`authority=founder` 的 Rule）、历史失败（`root_cause` 明确的 Experience）、生效规则注入 Context，否则「Agent 不知道你的历史」这个核心痛点无法解决。

Agent 运行时按需检索（第四章）只是**辅助路径（P1）**，不能替代 Governor 的强制注入。

### 定义

输入任务与角色，输出一个受预算约束的 Context Package。

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

## 4.1 双模式架构（主次明确）

Sera 的 Context 是**双模式，但主次严格**：`Context Governor`（中心化，P0，强制注入）是**主路径**；`Agent Runtime Loop`（运行时按需检索，P1）是**辅助**。**不能依赖 Agent 主动意识到自己缺什么**——多数 Agent（Codex/Cursor 等）会直接执行，不回溯历史失败。因此 Governor 的强制注入是闭环成立的底线。

```
任务开始 ──→ Context Governor（P0 强制注入）──→ 初始 Context Package（中心化）
                                       │
                                       ▼ 注入 System Prompt
===========================================================
            Agent Runtime Loop（P1 辅助，按需检索）
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
    # Phase 0: Context Governor 中心化强制注入（P0 主路径）
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
Experience（一次任务的成败，含 root_cause / failure_mode）
        │
        ▼
Root Cause Analysis（因果归因：区分「具体缺陷」与「普遍规律」）
        │
        ▼
Pattern Detection（仅从 root_cause 层级聚类，禁止从表面 failure_mode 聚类）
        │
        ▼
Rule Extraction（提炼为 Hypothesis，status=draft + confidence 初始值）
        │
        ▼
Validation（验证，见 5.4：3 次独立关联是必要非充分条件）
        │
        ▼
Organization Memory（authority=organization 的 Rule 固化）
        │
        ▼
Better Context（下次 Context Governor 自动纳入）
```

## 5.2 Root Cause Analysis + Pattern Detection（因果层，V1.1 新增）

**关键决策：Pattern 只能从 `root_cause` 提炼，禁止从 `failure_mode` 提炼。**

反例（必须避免）：

```
三次「AI 视频失败」
  failure_mode = "视频不可信"（表面现象）
  root_cause    = "MiniMax H3 模型输出质量不足"（真实原因）

错误归纳：AI 视频 → 不可信（把具体模型缺陷上推成普遍规律）
正确归纳：MiniMax H3 → 不适合此场景（锚定到具体根因）
```

```python
def analyze_root_cause(experience):
    # 强制区分「根因」与「现象」，二者必须同时存在
    prompt = """
    对这条失败经验做因果归因：
    1. failure_mode（现象，what went wrong）
    2. root_cause（根因，why，必须是可验证的具体原因，
       拒绝"XX 整体不可信"这类泛化表达）
    """
    result = llm(prompt, context=experience)
    experience.failure_mode = result.failure_mode
    experience.root_cause   = result.root_cause  # SMOP V1 已有，本层强制利用
    return experience


def detect_patterns():
    experiences = memory.query({
        "type": "Experience",
        "data_state": "learned",
        "since": "30 days ago"
    })
    # 仅对 root_cause 聚类（不做 failure_mode 聚类）
    clusters = cluster_by_embedding([e.root_cause for e in experiences])
    return [c for c in clusters if len(c.members) >= 2]
```

## 5.3 Rule Extraction（产出 Hypothesis，不直接产 Rule）

```python
def extract_rule(cluster):
    # 提炼为「假设」，而不是直接升 Rule
    return Rule(
        content       = cluster.common_root_cause_lesson,
        scope         = infer_scope(cluster),   # project / organization
        status        = "draft",                 # Hypothesis 用 status 表达，不新增类型
        confidence    = 0.5,
        authority     = "organization",
        source_experiences = [e.id for e in cluster.members]
    )   # 等待 5.4 验证通过后才 status: draft → active
```

## 5.4 Validation（复用 SMOP 已有机制，不新造）

**关键决策：Validation 尽量复用 SMOP V1 已有机制（confidence / supersedes / status），仅新增一个 `authority` 字段用于权威裁决。**

### 机制 1：`confidence` 决定初始可信度

| confidence | 来源 | 是否可直接升 Rule |
|-----------|------|------------------|
| 1.0 | 人工确认 | 是 |
| 0.9 | 规则匹配 | 是（需 1 次人工复核） |
| 0.7 | LLM 高置信 | 否（需累计验证） |
| 0.5 | LLM 推断 | 否 |
| ≤0.3 | 未验证 | 否 |

### 机制 2：`3 次独立关联` 是**必要非充分**条件（V1.1 修正）

```
一条 lesson 升级为 Rule 必须同时满足：
  1. 因果一致：所有命中的 Experience 具有「同一 root_cause」，
     而非仅 failure_mode 表面相同；
  2. 被 ≥3 个「相互独立的 task/context」命中；
  3. 命中来源的 confidence ≥ 0.7；
  4. 不存在 authority 更高或同级的矛盾 Rule。

满足全部 → status: draft → active，data_state: learned → rule
任一不满足 → 保持 learned（或 draft），继续累计
```

**「3 次」只是门槛之一，不是充分理由。** 只有「重复 + 同根因 + 无更高权威矛盾」三者同时成立，才允许固化。

### 机制 3：`authority` 优先于 `supersedes`（V1.1 修正）

```
Rule 冲突时，先比较 authority，再考虑 supersedes：

1. authority 不同 → 高权威直接胜出（founder > organization > project > agent）
2. authority 相同 → 新 Rule 建立 supersedes → 旧 Rule，旧 Rule status → deprecated/replaced
3. Context Governor 查询时自动忽略被 supersedes 或低权威的 Rule

旧 Rule 过时（无新经验关联）：
  - rank_score 始终按半衰期公式自然衰减（rule 类型的 half_life = 90 天）
  - 30 天无 access → rank_score 已衰减至 ~0.5⁰·³³ = ~0.79，不影响 status
  - 180 天无 access + rank_score < 0.1 → status 标记为 "deprecated"（可恢复，访问后自动回升）
  - 365 天无 access → status 标记为 "archived"（不可恢复，仅保留审计记录）
  - 注意：**衰减作用于 rank_score 而非 status**，旧 Rule 即使 rank_score 很低也不丢失，
    通过 /learn 接口的关联访问可自然回升 rank_score，无需人工干预
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
                    │  structured  │  Experience Object（含 root_cause）
                    └──────┬───────┘
                           │ Root Cause Analysis 提炼 lesson
                           ▼
                    ┌──────────────┐
                    │  learned     │  经验教训（data_state=learned）
                    └──────┬───────┘
                           │ 同 root_cause 聚类 → 提炼 Hypothesis
                           ▼
                    ┌──────────────┐
                    │  draft       │  Rule 假设（status=draft, confidence=0.5）
                    └──────┬───────┘
                           │ 3 次独立关联 + 同根因 + confidence≥0.7 + authority 无矛盾
                           ▼
                    ┌──────────────┐
                    │  active      │  组织原则（data_state=rule, status=active）
                    └──────────────┘
```

---

# 六、Golden Path MVP — Sera Memory Kernel V0

## 6.1 目标

用**最小可验证闭环**证明价值，不做全功能系统，更不做 MCP / Agent Loop（它们是协议与执行，不是核心价值）。

```
你给任务 → Agent 拿到历史（含 Founder 判断 + 失败根因）→ 完成任务
        → 写经验 → 第二次任务命中该经验
```

## 6.2 纳入范围（Kernel V0 必须）

| 组件 | 说明 | 技术选型 |
|------|------|---------|
| Memory Store | objects + relations + events 三表 | **SQLite**（零配置，不用 Postgres） |
| SMOP Object | 二维矩阵 + authority 字段落地 | JSON 列 + 索引 |
| Context Governor | build_context（ranking + budget + 强制注入 Founder Rule） | 纯函数模块 |
| Learn API | learn（root_cause 归因 + 3 次验证升 Rule） | 纯函数模块 |
| Seed 数据 | 用 Obsidian 现成的 TradeSpan 内容导入 | 手动/脚本 import |

### 6.2.1 三表 Schema 定义（SQLite DDL）

```sql
-- ========== objects 表（SMOP 对象） ==========
CREATE TABLE objects (
    id          TEXT PRIMARY KEY,          -- 点分命名，如 "project.tradespan"
    type        TEXT NOT NULL,             -- Project / Decision / Experience / Rule / Agent / Task
    data_state  TEXT NOT NULL DEFAULT 'raw'
                CHECK(data_state IN ('raw','processed','structured','learned','rule')),
    scope       TEXT NOT NULL DEFAULT 'project'
                CHECK(scope IN ('company','organization','project','agent')),
    authority   TEXT NOT NULL DEFAULT 'agent'
                CHECK(authority IN ('founder','organization','project','agent')),
    status      TEXT NOT NULL DEFAULT 'active'
                CHECK(status IN ('active','deprecated','archived','draft','replaced')),
    confidence  REAL NOT NULL DEFAULT 0.0 CHECK(confidence >= 0.0 AND confidence <= 1.0),
    importance  REAL NOT NULL DEFAULT 0.5 CHECK(importance >= 0.0 AND importance <= 1.0),
    rank_score  REAL NOT NULL DEFAULT 0.5 CHECK(rank_score >= 0.0 AND rank_score <= 1.0),
    payload     TEXT NOT NULL DEFAULT '{}', -- JSON: 各类型专有字段
    created_at  TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at  TEXT NOT NULL DEFAULT (datetime('now')),
    accessed_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX idx_objects_type ON objects(type);
CREATE INDEX idx_objects_data_state ON objects(data_state);
CREATE INDEX idx_objects_rank_score ON objects(rank_score DESC);
CREATE INDEX idx_objects_scope ON objects(scope);
CREATE INDEX idx_objects_authority ON objects(authority);

-- ========== relations 表（SMOP 关系边） ==========
CREATE TABLE relations (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id   TEXT NOT NULL REFERENCES objects(id),
    target_id   TEXT NOT NULL REFERENCES objects(id),
    type        TEXT NOT NULL,             -- supersedes / derived_from / led_to / related_to / depends_on
    weight      REAL NOT NULL DEFAULT 1.0 CHECK(weight >= 0.0 AND weight <= 1.0),
    metadata    TEXT NOT NULL DEFAULT '{}', -- JSON: 关系元数据
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX idx_relations_source ON relations(source_id);
CREATE INDEX idx_relations_target ON relations(target_id);
CREATE INDEX idx_relations_type ON relations(type);

-- ========== events 表（不可变事件日志，append-only） ==========
-- 注意：此表为 append-only，禁止 UPDATE 和 DELETE（通过 SQLite 触发器强制）
-- 所有 Memory 变更（创建/更新/状态变更/学习/访问）都在此留下审计记录
CREATE TABLE events (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type  TEXT NOT NULL,             -- object_created / object_updated / status_changed / rank_score_decayed / learned / rule_promoted / context_built / access
    object_id   TEXT,                      -- 关联对象 ID（可为 NULL，如系统事件）
    actor       TEXT NOT NULL DEFAULT 'system',  -- 触发者：agent_id / "system" / "human"
    summary     TEXT NOT NULL,             -- 人类可读的描述
    payload     TEXT NOT NULL DEFAULT '{}', -- JSON: 事件详情（如旧值/新值/根因等）
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX idx_events_type ON events(event_type);
CREATE INDEX idx_events_object ON events(object_id);
CREATE INDEX idx_events_created ON events(created_at DESC);

-- 强制 events 表为 append-only（防止篡改审计日志）
CREATE TRIGGER prevent_events_update BEFORE UPDATE ON events
BEGIN
    SELECT RAISE(ABORT, 'events table is append-only: UPDATE forbidden');
END;
CREATE TRIGGER prevent_events_delete BEFORE DELETE ON events
BEGIN
    SELECT RAISE(ABORT, 'events table is append-only: DELETE forbidden');
END;
```

### 6.2.2 Staging 闸门机制

Kernel V0 在写入 objects 表前，需经过 staging 闸门验证，确保数据质量：

```
用户/Agent 提交数据
       │
       ▼
┌─────────────────────────────┐
│       Staging Buffer        │  临时存储，不进入主表
│  (内存 dict / 临时 JSON)    │
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│     Staging Gate Checks     │
│  ┌───────────────────────┐  │
│  │ 1. ID 格式验证         │  │  点分命名，非空
│  │ 2. data_state 合法性   │  │  必须是 5 态之一
│  │ 3. authority 合法性    │  │  必须是 4 级之一
│  │ 4. required 字段完整性 │  │  type/payload 非空
│  │ 5. 重复 ID 检测        │  │  已存在则报错(非幂等)
│  │ 6. 关系一致性检查      │  │  source/target 必须存在
│  └───────────────────────┘  │
└─────────────┬───────────────┘
              │ 全部通过
              ▼
┌─────────────────────────────┐
│    写入 objects 表          │
│    同时写入 events 表       │  事件类型: object_created
└─────────────────────────────┘
```

Staging Gate 实现为一个纯函数模块，Kernel V0 中直接调用：

```python
def staging_gate(obj: dict) -> dict:
    """
    验证并写入 SMOP 对象。
    返回: {"ok": True, "id": "..."} 或 {"ok": False, "error": "..."}
    """
    checks = [
        validate_id_format(obj.get("id", "")),
        validate_data_state(obj.get("data_state", "")),
        validate_authority(obj.get("authority", "")),
        validate_required_fields(obj, ["type", "payload"]),
        validate_no_duplicate_id(obj.get("id", "")),
        validate_relation_consistency(obj.get("relations", [])),
    ]
    for check in checks:
        if not check["ok"]:
            return {"ok": False, "error": check["error"]}
    # 写入 objects 表
    object_store(obj)
    # 写入 events 表（append-only）
    events_append("object_created", obj["id"], actor=obj.get("actor", "system"))
    return {"ok": True, "id": obj["id"]}
```

## 6.3 明确排除（Kernel V0 不做）

| 组件 | 理由 | 推迟到 |
|------|------|-------|
| MCP Server | 连接协议，非核心价值，闭环不依赖它 | Phase 2 |
| Agent Runtime Loop | 执行循环，非闭环必需 | Phase 2 |
| LanceDB 向量 | 语义搜索非闭环必需 | Phase 3 |
| 图遍历引擎（Neo4j/pgRouting） | relations 表 + 递归 CTE 足够 | Phase 3 |
| 多源 Extractor | Obsidian 手动导入可验证闭环 | Phase 4 |
| Cron Memory Builder | 日结是优化非必需 | Phase 4 |
| PostgreSQL | 违反零配置原则 | 分布式阶段 |

## 6.4 最小 API 端点（只这两个是闭环核心）

```
POST /context/build          # build_context(task_id) → Context Package（Kernel 核心）
POST /learn                  # learn(result) → root_cause 归因 + 触发验证（Kernel 核心）

# 辅助（支撑上面两个，可简化为函数而非 HTTP 端点）
object_get / object_store / search（FTS5 关键词，MVP 替代向量）/ stats
```

## 6.5 验收标准（真实案例，非假数据）

以 **TradeSpan** 为唯一验收场景，数据来自你 Obsidian 现成的项目内容：

```
1. 用 Obsidian 里 TradeSpan 的决策/失败经验 seed SQLite
2. 任务 A："重做 TradeSpan 官网" → build_context 注入 dark-ui 决策 + trust-first 规则
3. 任务 A 完成后 learn(成功/失败，含 root_cause)
4. 任务 B："做 TradeSpan 宣传视频" → build_context 命中任务 A 沉淀的失败根因

验收通过 = 第 4 步的 Context Package 里，出现了第 3 步写入的 root_cause。
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
Context Governor → GET /object/{id}, POST /search
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

## Phase 1: Memory Kernel V0（最小闭环）

```
目标：闭环可跑，不做 MCP / Agent Loop
├── SQLite 三表 DDL（objects/relations/events）+ data_state/scope/authority CHECK 约束
├── events 表 append-only 触发器（防止篡改审计日志）
├── Staging Gate 纯函数（写入前 6 项验证：ID 格式 / data_state / authority / 完整性 / 重复 / 关系）
├── Context Governor（build_context：ranking + budget + 强制注入 Founder Rule）
├── Learn API（root_cause 归因 + 3 次验证升 Rule）
├── TradeSpan 真实数据 seed（来自 Obsidian）
└── 验收：任务 A 写入的失败根因，出现在任务 B 的 Context Package 中
```

## Phase 2: MCP & Agent Loop

```
目标：接入真实 Agent 执行
├── MCP server（sera-memory 6 工具）
├── Agent Runtime Loop（Plan→Act→Learn，P1 辅助）
├── Context Governor 与 Loop 打通
└── 验收：Codex 通过 MCP 调 build_context，任务后自动 learn
```

## Phase 3: Semantic Retrieval

```
目标：模糊查询
├── LanceDB 向量集成
├── Hybrid Search（RRF fusion）
├── Context Governor 接入语义候选
└── 验收：自然语言问"视频失败根因"能命中
```

## Phase 4: Graph Traversal

```
目标：关系推理
├── 递归 CTE 图遍历
├── Context Ranking 加入 relation_weight 深层传播
└── 验收：查 Project 能沿 depends_on/created_by 走 ≥3 层
```

## Phase 5: Autonomous Learning

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
| Context Governor | 强制注入上下文的中心化主路径（P0），Agent Loop 之前 |
| authority | 权威等级（founder > organization > project > agent），用于冲突裁决 |
| Root Cause Analysis | 因果归因：区分「具体根因」与「表面现象」，Pattern 只从根因提炼 |
| Hypothesis | Rule 的假设态（status=draft + confidence 0.5），验证后才 active |

# 附录 B: 与 SMOP V1 的差异清单

| 变更 | SMOP V1 | 本层 |
|------|---------|------|
| 基类新增 `data_state` | 无 | ✅ |
| 基类新增 `scope` | 无 | ✅ |
| 基类新增 `authority` | 无 | ✅（V1.1） |
| ID 命名 | 点分（正确）| 明确废弃下划线格式 |
| Context Package | 静态 | + budget / truncated / stale_markers |
| Context 生成 | 仅 Builder | Context Governor（主）+ Agent Loop（辅） |
| 学习 | 手动 learn | 强制 Learn + Root Cause 分析 + 3 次验证（必要非充分） |
| Rule 冲突裁决 | supersedes 先后 | authority 优先，同级才 supersedes（V1.1） |

---

*Document Version: 1.1*
*Last Updated: 2026-08-21（V1.1 修订：authority / Root Cause 分析 / Governor 主路径 / Kernel V0）*
*Next: Sera Context Runtime & Learning OS Implementation Guide V1（代码实现）*