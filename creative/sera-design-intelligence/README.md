# Sera Design Intelligence System

> 版本：4.1.0 · 2026-08-31
> 定位：Sera OPC OS 的 **Evidence-first Design Intelligence System**
> 核心闭环：**Measure → Understand → Compare → Remember → Create → Review → Learn**

## 核心定位

Sera Design Intelligence 不负责“照着某个网站抄一遍”。它负责把优秀产品的设计转化为可验证、可解释、可检索、可组合、可学习的长期设计能力。

```text
URL / Figma / Local Code
        ↓
L0 Capture & Extraction
        ↓
L1 Evidence & Provenance
        ↓
L2 Design DNA & Understanding
        ↓
L2.5 Cross-site Learning
        ↓
L3 Design Memory
        ↓
L4 Style Router / Design System / Generation
        ↓
L5 Review & Learning
```

**默认 URL Extraction Backend：Designlang。** Designlang 负责读取 rendered DOM / computed styles 并输出机器可读设计事实；Sera 负责判断为什么有效、跨站是否重复、是否值得记忆、如何复用以及如何组合成新的产品设计。

## V4.1 架构

```text
sera-design-intelligence/
├── extraction-engine/             # 机器事实层
│   ├── adapter.py
│   ├── designlang-adapter.yaml
│   └── extraction-contract.schema.json
├── dna-engine/                    # Evidence → Style DNA
├── cross-site/                    # V4.1：多站 Pattern Learning
│   ├── miner.py
│   ├── comparison.schema.json
│   ├── promotion-policy.md
│   ├── tests/
│   └── studies/
├── design-direction/              # 产品 × 风格决策
├── benchmark/                     # 设计基准
├── patterns/                      # Pattern Library
├── knowledge/                     # 原则 / 心理 / 商业知识
├── styles/                        # Style Registry
├── style-router/                  # 风格路由
├── case-studies/                  # 已分析案例
├── assets/                        # 资产索引
├── memory/design-feedback/        # 实验 / 转化 / 用户反馈
├── workflows/                     # Extraction / Cross-site / Design Pipeline
└── interfaces/                    # Product Factory 协议
```

## 单站提取

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

## 跨站学习

```bash
python3 cross-site/miner.py \
  --case linear=case-studies/linear \
  --case stripe=case-studies/stripe \
  --case vercel=case-studies/vercel \
  --out cross-site/studies/premium-product-web-v1/result.json \
  --markdown cross-site/studies/premium-product-web-v1/result.md
```

Promotion：

```text
1 independent site  → case_local
2 independent sites → candidate
3+ independent sites → strong_candidate
                   ↓
             Design Review
                   ↓
           Canonical Pattern
```

同一 domain 的多个页面不重复计票。Raw HEX / font / px 默认不算跨站 Pattern；优先挖组件、布局、转化、动效和品牌语义模式。

## Evidence Model

| 类型 | 含义 | 示例 |
|---|---|---|
| `observed` | 机器直接测量 | CSS 变量、字体、圆角、breakpoint |
| `derived` | 可重复计算/归纳 | spacing 呈现统一 scale |
| `inferred` | Agent 解释设计意图 | 弱化侧栏提高主内容聚焦 |
| `recommended` | 面向新产品的建议 | 当前 Hero 可采用 product-in-context demo |

禁止把 `inferred` / `recommended` 冒充 `observed`。

## First Cross-site Smoke Test

Ready anchors：

- Linear
- Stripe
- Vercel

Panda AI 已保留为 queued target；`pandaai.com` 的 intended product canonical URL 在确认前不生成伪 Extraction / DNA。

## 当前能力

- Designlang URL 逆向 + Browser fallback
- Evidence / Provenance Contract
- Evidence-backed Style DNA
- Responsive / Interaction / Dark Mode / Motion
- Design Benchmark / Pattern Library
- Cross-site deterministic Pattern Mining
- Design Strategy / Style Router
- Component / Asset Library
- UX Conversion / Design Critic Gate
- Experiment / Conversion / Feedback Learning Loop

## 路线

```text
V4.0  Evidence-first Extraction Architecture
V4.1  Cross-site Learning + Promotion Policy       ← 当前
V4.2  Drift Monitor + scheduled re-extraction
V4.3  Component Retrieval + Style Composition
```

## 上游边界

Designlang upstream：`Manavarya09/design-extract`（MIT）。

Designlang 是可替换 Extraction Backend；Sera 的 Design DNA、Cross-site Learning、Memory、商业判断、Style Router、生成和 Review 保持 Sera-native。