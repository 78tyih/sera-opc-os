---
name: sera-design-intelligence
version: 4.1.0
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
> **不是复制网站的 Skill，也不是 Designlang 的包装器。**
> V4.1 增加 Cross-site Learning：单站提供事实，多站共同支持的模式才有资格晋升长期 Design Memory。

## Purpose

1. **Measure** — 用机器提取真实设计事实
2. **Understand** — 分析为什么设计选择有效
3. **Compare** — 跨独立网站识别重复 Pattern
4. **Remember** — 进入 Case / Pattern / Component / Style Memory
5. **Route** — 根据产品目标选择或组合风格
6. **Create** — 驱动 Design System / Page Generator
7. **Review** — UX / Design Critic 门禁
8. **Learn** — 实验、转化与反馈更新规则

## Architecture

```text
Capture
  ↓
Extraction Backend (Designlang primary)
  ↓
Evidence Normalizer
  ↓
Evidence-backed Design DNA
  ↓
Design Strategy / Case Analysis
  ↓
Cross-site Pattern Miner
  ↓
Pattern Candidate Review
  ↓
Case + Pattern + Component + Style Memory
  ↓
Style Router / Design Direction
  ↓
Design System / Generator
  ↓
UX Gate + Critic Gate
  ↓
Evolution Loop
```

## When to Use

- 给出网站 URL，希望拆解 / 提取 / 学习 / 保存设计
- 对比多个网站的设计语言并寻找共同 Pattern
- 新产品设计前建立 Reference Pack
- 提炼颜色、字体、间距、组件、动效、响应式
- 将优秀设计沉淀到 Style / Pattern / Component Library
- 为 AI Coding Agent 输出可复用设计约束
- 根据行业、用户、品牌目标选择设计方向
- 审查页面是否符合 Sera Design Memory

## Evidence Model

每个重要结论属于：

- `observed`：机器直接测得
- `derived`：从 observed facts 可重复计算
- `inferred`：Agent 对设计意图/心理/策略的解释
- `recommended`：面向新产品的建议

**禁止 inferred / recommended 冒充 observed。**

## Single-site Workflow

```text
Preflight → Browser Capture → Designlang Extraction → Normalize → Validate
→ STYLE_DNA → Design Reasoning → Case Study → Memory Candidate → Review
```

详见 `workflows/design-extraction.yaml`。

## Cross-site Workflow

```text
Site A → STYLE_DNA ─┐
Site B → STYLE_DNA ─┼→ deterministic overlap → semantic review → critic gate → Pattern Candidate
Site C → STYLE_DNA ─┘
```

详见：

- `workflows/cross-site-learning.yaml`
- `cross-site/miner.py`
- `cross-site/promotion-policy.md`
- `cross-site/comparison.schema.json`

Promotion rule：

- 1 independent domain → `case_local`
- 2 independent domains → `candidate`
- 3+ independent domains → `strong_candidate`
- same domain never counts twice
- no Candidate becomes canonical without review

`miner.py` 不调用 LLM，只做确定性 overlap。Design Strategy / Critic 负责判断重复是否真的构成可复用 Pattern。

## New Product Workflow

```text
Product Brief
  ↓
Design Director
  ↓
Reference Set / Cross-site Evidence
  ↓
Psychology / Strategy
  ↓
Style Router + Pattern Retrieval
  ↓
Design System
  ↓
Page Generator
  ↓
UX Conversion Gate
  ↓
Design Critic Gate
  ↓
Asset + Memory Update
```

## Iron Rules

1. **Measure before reason**：可测量事实不先靠截图猜。
2. **Facts ≠ opinions**：Observed / Derived / Inferred / Recommended 分层。
3. **Provenance required**：Style DNA 关键字段必须有 evidence reference。
4. **Backend replaceable**：上层不得耦死 Designlang 私有 Schema。
5. **Raw is immutable**：原始证据只新增，不人工改写。
6. **Normalize before memory**：第三方产物先归一化。
7. **No credential persistence**：Cookie / token / session 不写入 Git。
8. **No blind cloning**：学习规律，不默认复制第三方代码或品牌资产。
9. **Single-site ≠ global rule**：单站发现默认 case-local。
10. **Independent support**：同一 domain 多页面不重复计票。
11. **Raw token ≠ pattern**：HEX / px / font 相同不自动等于设计规律。
12. **Review before promotion**：Candidate 必须经过 Design Review / Critic。
13. **Conflict visible**：Extraction 与截图冲突必须记录。
14. **Learning needs outcome**：长期规则优先结合实验、转化和用户反馈。

## Failure Handling

Designlang 失败：

```text
sera-browser-automation
  ↓
screenshot + DOM/CSS evidence
  ↓
same extraction-manifest contract
```

缺失字段保持 unknown/omitted，不允许 LLM 补假值。

Ambiguous reference URL：标记 `needs_url_verification`，不生成伪 Extraction / Design DNA。

## Design Philosophy

Sera 的默认 prior：

```text
Trust + Technology + Premium + Conversion
```

它是路由起点，不是所有产品的硬编码答案。

## Version History

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-08-21 | Design Memory + Case Study |
| 1.1 | 2026-08-21 | Knowledge Engine + Registry |
| 3.2 | 2026-08-21 | Cyber Engine + Multi-Agent Pipeline |
| 3.3 | 2026-08-21 | Design Director / Direction Matching |
| 3.4 | 2026-08-21 | Benchmark + Pattern Intelligence |
| 3.5 | 2026-08-21 | Evolution / Feedback Loop |
| 4.0 | 2026-08-31 | Evidence-first Extraction + Designlang Backend |
| **4.1** | **2026-08-31** | **Cross-site Learning + Pattern Promotion Policy** |