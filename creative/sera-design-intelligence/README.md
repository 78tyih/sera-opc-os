# Sera Design Intelligence System

> 版本：4.4.0 · 2026-08-31
> 定位：Sera OPC OS 的 **Evidence-first Design Intelligence + Productization System**
> 核心闭环：**Measure → Understand → Compare → Track → Remember → Create → Review → Learn → Productize**

## 核心定位

Sera Design Intelligence 不负责“照着某个网站抄一遍”。它把优秀网站、真实项目、成熟 Design Skill 与长期反馈转化为可验证、可解释、可检索、可组合、可追踪、可复用的设计能力。

```text
URL / Figma / Local Code / Design Skill
        ↓
L0 Capture & Reference Intake
        ↓
L1 Evidence & Provenance
        ↓
L2 Design DNA & Understanding
        ↓
L2.5 Cross-site Learning
        ↓
L2.6 Living Benchmark / Drift
        ↓
L2.7 Skill Benchmark Ingestion
        ↓
L3 Design Memory
        ↓
L4 Style Router / Design System / Generation
        ↓
L5 Review & Learning
        ↓
L6 Component / Template / Skill Productization
```

**默认 URL Extraction Backend：Designlang。** Designlang 负责 rendered DOM / computed styles 等机器事实；Sera 负责设计推理、跨站学习、长期 drift、Skill Benchmark、Memory、Style Router、生成、Review 与商品化。

## V4.4 架构

```text
sera-design-intelligence/
├── extraction-engine/             # 机器事实层
├── dna-engine/                    # Evidence → Style DNA
├── cross-site/                    # 多站 Pattern Learning
├── living-benchmark/              # 长期 Design Radar + Drift
├── benchmark/
│   ├── ai-products/
│   ├── dashboards/
│   ├── fintech/
│   ├── landing-pages/
│   ├── saas/
│   ├── trading/
│   └── internal-skills/           # V4.4：受限/内部成熟 Skill Benchmark
├── patterns/
├── knowledge/
├── styles/                        # Style DNA Registry
├── component-library/             # Composite Component Registry + Demo
├── template-library/              # Reusable Solution Templates
├── style-router/
├── case-studies/
├── assets/
├── memory/design-feedback/
├── workflows/
└── interfaces/
```

## Evidence Model

| 类型 | 含义 |
|---|---|
| `observed` | 机器直接测量 |
| `document_observed` | 授权文档直接写明 |
| `user_reported` | 用户 / 作者公告提供，尚未独立验证 |
| `derived` | 可重复计算/归纳 |
| `inferred` | Agent 解释设计意图 |
| `recommended` | 面向新产品或 Sera 的建议 |

禁止把 `inferred`、`recommended`、`user_reported` 冒充 `observed`。

## Single-site Extraction

```bash
python3 extraction-engine/adapter.py https://linear.app \
  --out case-studies/linear/raw/designlang
```

Canonical Case：

```text
case-studies/linear/
├── raw/designlang/
├── normalized/extraction-manifest.json
├── dna/STYLE_DNA.json
├── analysis.md
├── extracted-rules.md
└── reproduction-prompt.md
```

## Cross-site Learning

```text
1 independent site   → case_local
2 independent sites  → candidate
3+ independent sites → strong_candidate
                     ↓
                Design Review
                     ↓
              Canonical Pattern
```

同一 domain 多页面不重复计票；Raw HEX / font / px 默认不自动升级成跨站 Pattern。

## Living Design Benchmark

第一批长期 Radar 包括 Linear、Stripe、Vercel、Apple、Raycast、Figma。

```text
Approved Baseline
      ↓
Current Snapshot
      ↓
Drift
      ↓
none / minor / moderate / major
      ↓
Meaningful Change Gate
```

**Change ≠ Improvement。** moderate / major 变化必须进入 Review，不能自动覆盖 canonical Memory。

## Skill Benchmark Ingestion

V4.4 开始，成熟 Design Skill 本身也成为学习对象。

```text
Skill / Docs / Release
        ↓
Metadata Registration
        ↓
Authorized Review
        ↓
Capability Extraction
        ↓
Normalize + Compare
        ↓
Conflict / Privacy / Portability Review
        ↓
Adopt / Adapt / Reject
        ↓
Generic Test
        ↓
Sera-native Rule / Pattern / Component / Workflow
```

### Restricted / Internal Sources

对于公司内网、私有、付费或受限文档：

- 公共仓库只登记最小 metadata；
- 不公开内部 Wiki URL、原文、截图、附件和凭证；
- 没有授权访问时维持 `metadata-only`；
- 发布公告中的能力声明记录为 `user_reported`；
- 只有经过授权阅读、冲突审查与可迁移性审查后才能进入 canonical Sera Memory。

首批已登记：

- `hx-skill` / 火效
- `MarketUI skill`

详见：

- `benchmark/internal-skills/registry.json`
- `benchmark/internal-skills/hx-marketui-2026-08-31.md`
- `workflows/ingest-restricted-design-skill.md`

## Productization

真实项目不应在交付结束后失效：

```text
Real Project
  ↓
Case Study
  ↓
Style DNA
  ↓
Composite Components
  ↓
Reusable Template
  ↓
Agent Skill
  ↓
Demo / Solution Pack / Commercial Asset
```

当前首批产品化资产：

- Regulated Deal Desk
- Execution Command Center
- Composite Component Library

## 当前能力

- Designlang URL 逆向 + Browser fallback
- Evidence / Provenance Contract
- Evidence-backed Style DNA
- Responsive / Interaction / Dark Mode / Motion
- Cross-site Pattern Mining
- Living Design Radar / immutable snapshots
- Semantic Drift + Memory Gate
- Internal / restricted Skill Benchmark intake
- Design Strategy / Style Router
- Composite Component Registry
- Template Library
- Generic Demo / Productization Pipeline
- UX Conversion / Design Critic Gate
- Experiment / Conversion / Feedback Learning Loop

## 路线

```text
V4.0  Evidence-first Extraction Architecture
V4.1  Cross-site Learning + Promotion Policy
V4.2  Living Benchmark + Drift Monitor
V4.3  Component / Template Productization
V4.4  Design Skill Benchmark Ingestion                 ← 当前
V4.5  Component Retrieval + Automatic Composition
```

## 上游边界

Designlang upstream：`Manavarya09/design-extract`（MIT）。

Designlang 与其他 Design Skill 都是可学习、可替换、可比较的输入源；Sera 的 Evidence Model、Memory、Style Router、Productization、商业判断与 Review 保持 Sera-native。
