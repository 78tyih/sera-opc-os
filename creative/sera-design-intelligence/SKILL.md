---
name: sera-design-intelligence
version: 4.0.0
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
> 它把“事实提取 → 设计理解 → 长期记忆 → 风格路由 → 生成 → 审查 → 学习”连接成一个闭环。

## Purpose

1. **Measure** — 用机器提取真实设计事实
2. **Understand** — 分析为什么设计选择有效
3. **Remember** — 进入 Case / Pattern / Component / Style Memory
4. **Route** — 根据产品目标选择或组合风格
5. **Create** — 驱动 Design System / Page Generator
6. **Review** — 用 UX 与 Design Critic 门禁审查
7. **Learn** — 从实验、转化与反馈更新规则

## Core Architecture

```text
Capture
  ↓
Extraction Backend
  ↓
Evidence Normalizer
  ↓
Design DNA
  ↓
Design Strategy / Analyst
  ↓
Case + Pattern + Component + Style Registry
  ↓
Style Router / Design Direction
  ↓
Design System / Generator
  ↓
UX Gate + Critic Gate
  ↓
Design Memory / Evolution Loop
```

### Backend Policy

```text
primary: designlang
fallback: sera-browser-automation + manual normalized extraction
```

Designlang 只负责事实层。它不得直接决定：设计好不好、为什么有效、是否适合当前产品、该复制什么、如何组合多个参考来源、是否进入 Style Registry。

## When to Use

- 给出优秀网站 URL，希望拆解 / 提取 / 学习 / 保存设计
- 新产品设计前需要建立 Reference Pack
- 比较多个网站的设计语言
- 提炼颜色、字体、间距、圆角、阴影、动效、响应式、组件
- 将优秀设计沉淀到 Style / Pattern / Component Library
- 为 AI Coding Agent 输出可复用设计约束
- 根据行业、用户、品牌目标选择设计方向
- 审查页面是否符合 Sera Design Memory

## Evidence Model

每个重要结论必须属于四类之一：

- `observed`：浏览器或 Extraction Backend 直接测得
- `derived`：由 observed facts 可重复计算或归纳
- `inferred`：Agent 对设计意图、品牌心理、视觉策略的解释
- `recommended`：面向新产品的复用建议

**禁止把 inferred / recommended 写成 observed fact。**

## URL Extraction Workflow

```text
1. Preflight
   ├─ URL 可访问性
   ├─ designlang doctor
   └─ 是否需要认证
2. Capture
   ├─ browser screenshot
   └─ page/section map
3. Machine Extraction
   └─ extraction-engine/adapter.py → designlang
4. Normalize
   └─ extraction-manifest.json
5. Validate
   ├─ screenshot vs extracted evidence
   └─ missing / conflicting facts
6. DNA Synthesis
   └─ STYLE_DNA.json + evidence refs
7. Design Reasoning
   ├─ brand / hierarchy / psychology / conversion
   └─ motion / interaction logic
8. Benchmark + Pattern Mining
9. Register / Archive
   ├─ Case Study / Style Registry
   ├─ Pattern / Component Library
   └─ Asset Index
10. Review
   └─ provenance / legal / quality gate
```

详见 `workflows/design-extraction.yaml`。

## New Product Workflow

```text
Product Brief
  ↓
Design Director
  ↓
(optional) Reference URL Extraction
  ↓
Psychology / Market Context
  ↓
Style Router
  ↓
Design DNA / Pattern Match
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

## Design Department Roles

| Agent | V4 职责 |
|---|---|
| `design-director-agent` | 最终设计方向与取舍 |
| `design-strategy-agent` | 市场、竞品、差异化、设计策略 |
| `design-research-agent` | 发现参考、建立 Reference Set |
| `design-extraction-agent` | **Evidence-first 提取与证据归一化** |
| `design-system-agent` | 将方向与 DNA 编译成设计系统 |
| `design-generator-agent` | 页面/组件生成 |
| `ux-conversion-agent` | 转化路径与 CTA 门禁 |
| `design-critic-agent` | 高阶视觉与品牌门禁 |
| `design-review-agent` | 实现一致性检查 |
| `asset-manager-agent` | 资产索引与存储 |

## Iron Rules

1. **Measure before reason**：可测量事实不先靠截图猜。
2. **Facts ≠ opinions**：Observed / Derived / Inferred / Recommended 分层。
3. **Provenance required**：Style DNA 关键字段必须有 evidence reference。
4. **Backend replaceable**：上层逻辑不得耦死 Designlang 私有文件结构。
5. **Raw is immutable**：`raw/` 原始证据只新增，不人工改写。
6. **Normalize before memory**：第三方产物先归一化再进入 Memory。
7. **No credential persistence**：Cookie / session / token 不写入 Case / Git。
8. **No blind cloning**：学习结构规律，不默认复制第三方受保护代码或品牌资产。
9. **Cross-project reusable**：进入 Pattern / Style Registry 的规则必须有跨项目价值。
10. **Conflict visible**：截图与 Extraction Backend 冲突必须记录。
11. **Review before promotion**：Style / Rule Candidate 必须过 Reviewer 才晋升 canonical。
12. **Learning needs outcome**：长期规则优先结合测试、转化或明确用户反馈。

## Extraction Backend Contract

见：

- `extraction-engine/README.md`
- `extraction-engine/designlang-adapter.yaml`
- `extraction-engine/extraction-contract.schema.json`
- `extraction-engine/adapter.py`

未来任何 Backend 只要输出同一 `extraction-manifest.json`，上层 DNA / Memory 无需变化。

## Failure Handling

Designlang 不可用时：

```text
sera-browser-automation
  ↓
screenshot + DOM/CSS evidence
  ↓
manual normalized manifest
```

并显式标记 `fallback_used: true`。缺失字段保持 unknown/omitted，不允许 LLM 补假值。

登录页面只允许传本地 `cookie-file` / browser state 路径；不得持久化 cookie 内容。

## Design Philosophy

Sera 基础设计偏好作为 default prior，而不是硬编码答案：

```text
Trust + Technology + Premium + Conversion
```

Information First · Trust Before Action · Consistency Over Novelty · Subtle Motion · Conversion Oriented · Dark Mode Ready。

## Version History

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-08-21 | Design Memory + Case Study |
| 1.1 | 2026-08-21 | Knowledge Engine + Registry |
| 3.2 | 2026-08-21 | Cyber Engine + 9-Agent Pipeline |
| 3.3 | 2026-08-21 | Design Director / Direction Matching |
| 3.4 | 2026-08-21 | Benchmark + Pattern Intelligence |
| 3.5 | 2026-08-21 | Evolution / Feedback Loop |
| **4.0** | **2026-08-31** | **Evidence-first Extraction Layer + Designlang Backend** |