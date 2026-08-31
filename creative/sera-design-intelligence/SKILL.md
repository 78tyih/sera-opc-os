---
name: sera-design-intelligence
version: 4.4.0
type: design-intelligence
author: Sera
category: creative
compatible:
  - WorkBuddy
  - Codex
  - Trae
  - Claude-Code
  - Cursor
status: active
---

# Sera Design Intelligence Skill

> Sera OPC OS 的 Evidence-first Design Intelligence System。
> **不是复制网站的 Skill，也不是 Designlang 或其他单一 Design Skill 的包装器。**
> V4.4 在 Productization Layer 之上增加 Skill Benchmark Ingestion：能够把外部、内部、开源或受限访问的成熟设计 Skill 注册为学习对象，经过证据分层、冲突审查和可迁移性审查后再吸收进 Sera-native 设计能力。

## Purpose

1. **Measure** — 用机器提取真实设计事实
2. **Understand** — 分析为什么设计选择有效
3. **Compare** — 跨独立网站识别重复 Pattern
4. **Track** — 通过 immutable snapshot 追踪长期 Design Drift
5. **Remember** — 进入 Case / Pattern / Component / Style Memory
6. **Route** — 根据产品目标选择或组合风格
7. **Create** — 驱动 Design System / Page Generator
8. **Review** — UX / Design Critic 门禁
9. **Learn** — 实验、转化、反馈与长期 drift 更新规则
10. **Productize** — 把真实项目沉淀为可复用 Component / Template / Skill / Solution Pack
11. **Benchmark Skills** — 学习其他成熟 Design Skill，但不盲目复制或覆盖 Sera 规则

## Architecture

```text
Capture / Reference Intake
  ↓
Extraction Backend (Designlang primary)
  ↓
Evidence Normalizer
  ↓
Evidence-backed Design DNA
  ├──────────────┬─────────────────────┐
  ↓              ↓                     ↓
Cross-site       Living Benchmark      Skill Benchmark Intake
Pattern Miner    Snapshot → Drift      Public / Internal / Restricted
  ↓              ↓                     ↓
Pattern Review   Meaningful Gate       Extract → Compare → Review
  └──────────────┴──────────┬──────────┘
                            ↓
              Case + Pattern + Component + Style Memory
                            ↓
              Style Router / Design Direction
                            ↓
              Design System / Generator
                            ↓
              UX Gate + Critic Gate
                            ↓
              Productization Layer
                ├─ Component Library
                ├─ Template Library
                ├─ Agent Skill
                └─ Solution Pack
                            ↓
                     Evolution Loop
```

## When to Use

- 给出网站 URL，希望拆解 / 提取 / 学习 / 保存设计
- 对比多个网站的设计语言并寻找共同 Pattern
- 追踪优秀产品设计是否发生重要变化
- 新产品设计前建立 Reference Pack
- 提炼颜色、字体、间距、组件、动效、响应式
- 将优秀设计沉淀到 Style / Pattern / Component Library
- 为 AI Coding Agent 输出可复用设计约束
- 根据行业、用户、品牌目标选择设计方向
- 审查页面是否符合 Sera Design Memory
- 用户要求“把这个页面 / 项目打包成模板、Skill、可复用零件”
- 一个真实项目完成后，需要判断哪些设计资产值得进入长期库
- 希望把已有设计资产包装成可展示、可交付或可出售的产品
- 用户提供其他成熟 Design Skill、内部 Skill 或使用文档，希望“收录、学习、对比、吸收”

## Evidence Model

每个重要结论属于：

- `observed`：机器直接测得
- `document_observed`：授权文档中直接出现的规则或能力
- `user_reported`：用户、作者公告或发布说明提供，尚未独立核验
- `derived`：从 observed facts 可重复计算或归纳
- `inferred`：Agent 对设计意图/心理/策略的解释
- `recommended`：面向新产品或 Sera 的适配建议

**禁止 inferred / recommended / user_reported 冒充 observed。**

## Single-site Workflow

```text
Preflight → Browser Capture → Designlang Extraction → Normalize → Validate
→ STYLE_DNA → Design Reasoning → Case Study → Memory Candidate → Review
```

详见 `workflows/design-extraction.yaml`。

## Cross-site Workflow

```text
Site A → STYLE_DNA ─┐
Site B → STYLE_DNA ─┼→ deterministic overlap → semantic review → Pattern Candidate
Site C → STYLE_DNA ─┘
```

Promotion rule：

- 1 independent domain → `case_local`
- 2 independent domains → `candidate`
- 3+ independent domains → `strong_candidate`
- same domain never counts twice
- no Candidate becomes canonical without review

## Living Benchmark Workflow

```text
Radar Target
   ↓
Live Extraction
   ↓
STYLE_DNA
   ↓
Immutable Snapshot
   ↓
Compare with latest approved baseline
   ↓
Drift Severity
   ├─ none/minor → archive only
   ├─ moderate   → Design Memory Review
   └─ major      → Semantic Review + Cross-site recompute
```

详见：

- `living-benchmark/radar.json`
- `living-benchmark/snapshot.py`
- `living-benchmark/drift.py`
- `living-benchmark/meaningful-change-policy.md`
- `workflows/design-radar.yaml`

## Skill Benchmark Ingestion

### 目标

其他成熟 Skill 可以作为 **Benchmark / Learning Source**，但不能直接当作 Sera canonical rule。

```text
Skill / Docs / Release Announcement
        ↓
Access Classification
        ↓
Metadata Registration
        ↓
Authorized Source Review
        ↓
Capability + Rule Extraction
        ↓
Normalize to Sera Evidence Model
        ↓
Compare with Existing Sera Rules
        ↓
Conflict / Portability / Privacy Review
        ↓
Adopt / Adapt / Reject
        ↓
Generic Test
        ↓
Promote to Sera-native Memory
```

### Restricted / Internal Skill

如果 Skill 文档属于内网、付费、私有或受限访问：

- 公共仓库只登记最小 metadata；
- 不镜像原文、附件、截图、凭证或内部链接；
- 无授权内容访问时停止在 `metadata-only`，禁止猜测详细能力；
- 用户或作者公告中的能力描述标为 `user_reported`；
- 完成授权阅读后，再抽取 `document_observed` 规则；
- 只有通过冲突、隐私和可迁移性审查的抽象规则才能进入 Sera canonical memory。

当前首批内部 Benchmark：

- `hx-skill` / 火效
- `MarketUI skill`

索引：`benchmark/internal-skills/registry.json`。

工作流：`workflows/ingest-restricted-design-skill.md`。

## Productization Workflow

### 核心模型

```text
Real Project
   ↓
Case Study
   ↓
Style / Design DNA
   ↓
Composite Components
   ↓
Reusable Template
   ↓
Agent Skill
   ↓
Demo / Solution Pack / Commercial Asset
```

### 触发条件

以下任一情况出现时，Agent 应主动检查 Productization Candidate：

- 项目已经上线或通过真实业务验证；
- 某个页面结构明显可跨品牌复用；
- 某个组合组件解决了重复出现的业务问题；
- 用户认为设计“可以给别人直接抄作业”；
- 用户希望沉淀成模板、Skill、Design System 或出售。

### Productization 输出层

#### 1. Case Study
保存项目事实、设计决策、结果与证据。

#### 2. Style DNA
提炼视觉语言：颜色、字体、密度、圆角、阴影、动效、布局规律与情绪。

#### 3. Component Library
只保存**有业务意图的组合组件**，例如：

- High-Trust Hero
- Executive Summary Card
- KPI Metric Card
- Process Stepper
- Multi-Step Lead Form
- Status Pipeline Board
- Dependency Map

不要为了数量重复制造 Button / Input / Badge 等低价值 primitive。

机器可读索引：`component-library/registry.json`。

#### 4. Template Library
把多个组件组合成完整任务解决方案，例如：

- Regulated Deal Desk
- Execution Command Center

机器可读索引：`template-library/registry.json`。

#### 5. Skill
写明 Agent 在什么用户、任务、行业、信任等级和信息密度下应该选择该 Style / Component / Template。

#### 6. Demo / Solution Pack
必须使用通用假数据和脱敏品牌，证明资产可以脱离原项目独立成立。

### 组件选择顺序

```text
Intent
→ Audience
→ Trust Level
→ Information Density
→ Style DNA
→ Component Selection
→ Template Composition
→ Data / Content Binding
→ UX Review
```

### Productization Workflows

- `workflows/package-project-as-template.md`
- `workflows/component-productization.md`
- `component-library/README.md`
- `template-library/README.md`

## Iron Rules

1. **Measure before reason**：可测量事实不先靠截图猜。
2. **Facts ≠ opinions**：Observed / Derived / Inferred / Recommended 分层。
3. **Provenance required**：关键字段必须有 evidence reference。
4. **Backend replaceable**：上层不得耦死 Designlang 私有 Schema。
5. **Raw is immutable**：原始证据只新增，不人工改写。
6. **Normalize before memory**：第三方产物先归一化。
7. **No credential persistence**：Cookie / token / session 不写入 Git。
8. **No blind cloning**：学习规律，不默认复制第三方代码或品牌资产。
9. **Single-site ≠ global rule**：单站发现默认 case-local。
10. **Independent support**：同一 domain 多页面不重复计票。
11. **Raw token ≠ pattern**：HEX / px / font 相同不自动等于设计规律。
12. **Review before promotion**：Candidate 必须经过 Review。
13. **Change ≠ improvement**：网站改变不等于设计进步。
14. **New coverage ≠ drift**：Extractor 新测到字段不制造假变化。
15. **Historical ≠ current**：历史快照必须标 freshness。
16. **No automatic memory overwrite**：moderate/major drift 先 Review。
17. **Conflict visible**：Extraction 与截图冲突必须记录。
18. **Learning needs outcome**：长期规则优先结合实验、转化和用户反馈。
19. **Composite value over primitive volume**：Component Library 优先保存有业务意图的组合组件，不为数量重复造基础控件。
20. **De-brand before reuse**：真实项目进入 Template / Component 公共层前必须删除品牌专属与敏感业务数据。
21. **Relationship required**：Productized asset 必须关联 Case / Style / Component / Template / Skill 中至少两个对象，避免孤岛资产。
22. **Generic demo required**：可出售模板必须证明脱离原品牌、原数据后仍能独立成立。
23. **Restricted source stays restricted**：内网/私有 Design Skill 的原文、内部 URL、截图与附件不得镜像到公共仓库。
24. **No benchmark auto-merge**：其他 Skill 的规则必须经过 Extract → Compare → Review，不直接覆盖 Sera canonical rules。
25. **Reported claim ≠ verified capability**：发布公告或用户描述只能记为 `user_reported`，不能直接作为能力事实。

## Failure Handling

Designlang 失败时使用 `sera-browser-automation`，但继续遵守同一 Evidence Contract。

缺失字段保持 unknown/omitted，不允许 LLM 补假值。

Ambiguous reference URL 标记 `needs_url_verification`，不生成伪 Extraction / Design DNA。

Drift extraction 失败时保留上一版 baseline，不用失败/缺失结果覆盖 canonical snapshot。

Productization 时无法确认某内容是否敏感，则默认不进入公共 Demo / Template，只保留结构性抽象。

Restricted Skill 无授权访问时，只登记 metadata 与来源状态；禁止凭名称推测能力。

## Design Philosophy

Sera 的默认 prior：

```text
Trust + Technology + Premium + Conversion
```

它是路由起点，不是所有产品的硬编码答案。

长期目标：

> 既不让优秀项目在交付结束后失效，也不让优秀外部经验停留在“看过”。每一条新设计能力都必须经过证据、比较和审查后，才能沉淀成下一次真正可调用的 Sera 能力。

## Version History

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-08-21 | Design Memory + Case Study |
| 3.4 | 2026-08-21 | Benchmark + Pattern Intelligence |
| 3.5 | 2026-08-21 | Evolution / Feedback Loop |
| 4.0 | 2026-08-31 | Evidence-first Extraction + Designlang Backend |
| 4.1 | 2026-08-31 | Cross-site Learning + Pattern Promotion Policy |
| 4.2 | 2026-08-31 | Living Design Benchmark + Semantic Drift Monitor |
| 4.3 | 2026-08-31 | Component / Template Productization Layer + Commercial Asset Pipeline |
| **4.4** | **2026-08-31** | **Skill Benchmark Ingestion + Restricted-source policy; registered hx-skill and MarketUI skill** |
