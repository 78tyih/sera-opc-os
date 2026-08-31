# Sera Design Intelligence System

> 版本：4.2.0 · 2026-08-31
> 定位：Sera OPC OS 的 **Evidence-first Design Intelligence System**
> 核心闭环：**Measure → Understand → Compare → Track → Remember → Create → Review → Learn**

## 核心定位

Sera Design Intelligence 不负责“照着某个网站抄一遍”。它负责把优秀产品的设计转化为可验证、可解释、可检索、可组合、可追踪、可学习的长期设计能力。

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
L2.6 Living Benchmark / Drift
        ↓
L3 Design Memory
        ↓
L4 Style Router / Design System / Generation
        ↓
L5 Review & Learning
```

**默认 URL Extraction Backend：Designlang。** Designlang 负责读取 rendered DOM / computed styles 并输出机器可读设计事实；Sera 负责判断为什么有效、跨站是否重复、随时间发生了什么变化、是否值得记忆、如何复用以及如何组合成新的产品设计。

## V4.2 架构

```text
sera-design-intelligence/
├── extraction-engine/             # 机器事实层
├── dna-engine/                    # Evidence → Style DNA
├── cross-site/                    # V4.1：多站 Pattern Learning
├── living-benchmark/              # V4.2：长期 Design Radar + Drift
│   ├── radar.json
│   ├── snapshot.py
│   ├── drift.py
│   ├── meaningful-change-policy.md
│   ├── snapshots/
│   └── tests/
├── design-direction/
├── benchmark/
├── patterns/
├── knowledge/
├── styles/
├── style-router/
├── case-studies/
├── assets/
├── memory/design-feedback/
├── workflows/
└── interfaces/
```

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

```bash
python3 cross-site/miner.py \
  --case linear=case-studies/linear \
  --case stripe=case-studies/stripe \
  --case vercel=case-studies/vercel \
  --out cross-site/studies/premium-product-web-v1/result.json
```

Promotion：

```text
1 independent site   → case_local
2 independent sites  → candidate
3+ independent sites → strong_candidate
                     ↓
                Design Review
                     ↓
              Canonical Pattern
```

同一 domain 的多个页面不重复计票。Raw HEX / font / px 默认不算跨站 Pattern。

## Living Design Benchmark

V4.2 新增长期 Design Radar。第一批目标：

- Linear
- Stripe
- Vercel
- Apple
- Raycast
- Figma

所有目标先建立 immutable baseline，再用当前 extraction 生成新 snapshot：

```text
Historical / Approved Snapshot
            ↓
       Current Snapshot
            ↓
          Drift
            ↓
none / minor / moderate / major
            ↓
Meaningful Change Gate
```

**Change ≠ Improvement。**

- `none/minor`：归档，不污染长期 Memory。
- `moderate`：进入 Design Memory Review。
- `major`：进入 Semantic Review，并重新计算相关 Cross-site Pattern。
- 新增 measurement coverage 不算 drift。
- 历史快照不能冒充 current。

详见：

- `living-benchmark/README.md`
- `living-benchmark/radar.json`
- `living-benchmark/meaningful-change-policy.md`
- `workflows/design-radar.yaml`

## Evidence Model

| 类型 | 含义 |
|---|---|
| `observed` | 机器直接测量 |
| `derived` | 可重复计算/归纳 |
| `inferred` | Agent 解释设计意图 |
| `recommended` | 面向新产品的建议 |

禁止把 `inferred` / `recommended` 冒充 `observed`。

## 当前能力

- Designlang URL 逆向 + Browser fallback
- Evidence / Provenance Contract
- Evidence-backed Style DNA
- Responsive / Interaction / Dark Mode / Motion
- Design Benchmark / Pattern Library
- Cross-site deterministic Pattern Mining
- Living Design Radar / immutable snapshots
- Semantic Drift classification + Memory Gate
- Design Strategy / Style Router
- Component / Asset Library
- UX Conversion / Design Critic Gate
- Experiment / Conversion / Feedback Learning Loop

## 路线

```text
V4.0  Evidence-first Extraction Architecture
V4.1  Cross-site Learning + Promotion Policy
V4.2  Living Benchmark + Drift Monitor             ← 当前
V4.3  Component Retrieval + Style Composition
```

## 上游边界

Designlang upstream：`Manavarya09/design-extract`（MIT）。

Designlang 是可替换 Extraction Backend；Sera 的 Design DNA、Cross-site Learning、Living Benchmark、Memory、商业判断、Style Router、生成和 Review 保持 Sera-native。
