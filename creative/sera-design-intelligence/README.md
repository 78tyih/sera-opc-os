# Sera Design Intelligence System

> 版本：4.0.0 · 2026-08-31
> 定位：Sera OPC OS 的 **Evidence-first Design Intelligence System**
> 核心闭环：**Measure → Understand → Remember → Create → Review → Learn**

## 核心定位

Sera Design Intelligence 不负责“照着某个网站抄一遍”。它负责把优秀产品的设计转化为可验证、可解释、可检索、可组合、可学习的长期设计能力。

V4.0 将 URL 事实提取与设计推理正式分层：

```text
URL / Figma / Local Code
        ↓
L0 Capture & Extraction
        ↓
L1 Evidence & Provenance
        ↓
L2 Design DNA & Understanding
        ↓
L3 Design Memory
        ↓
L4 Style Router / Design System / Generation
        ↓
L5 Review & Learning
```

**默认 URL Extraction Backend：Designlang。** 它负责读取 rendered DOM / computed styles 并输出机器可读设计事实；Sera 负责判断为什么有效、是否值得记忆、如何复用以及如何组合成新的产品设计。

## V4 架构

```text
sera-design-intelligence/
├── extraction-engine/             # L0/L1：机器事实层
│   ├── README.md
│   ├── adapter.py
│   ├── designlang-adapter.yaml
│   └── extraction-contract.schema.json
├── dna-engine/                    # L2：Evidence → Style DNA
├── design-direction/              # 产品 × 风格决策
├── benchmark/                     # 设计基准
├── patterns/                      # Pattern Library
├── knowledge/                     # 原则 / 心理 / 商业知识
├── styles/                        # Style Registry
├── style-router/                  # 风格路由
├── case-studies/                  # 已分析案例
├── assets/                        # 资产索引
├── memory/design-feedback/        # 实验 / 转化 / 用户反馈 / 规则进化
├── workflows/                     # Extraction / Design Intelligence 流水线
└── interfaces/                    # Product Factory 输入输出协议
```

## URL 快速提取

```bash
cd creative/sera-design-intelligence

python3 extraction-engine/adapter.py https://linear.app \
  --out case-studies/linear/raw/designlang
```

Canonical case structure：

```text
case-studies/linear/
├── raw/designlang/                 # 上游原始证据，immutable
├── normalized/
│   └── extraction-manifest.json    # Sera 稳定接口
├── dna/
│   └── STYLE_DNA.json              # Evidence-backed DNA
├── analysis.md                     # 为什么有效
├── extracted-rules.md              # 可复用规则
└── reproduction-prompt.md          # AI 实现约束
```

环境检查：

```bash
npx -y designlang doctor
```

MCP 模式：

```bash
npx -y designlang mcp --output-dir ./case-studies/<case>/raw/designlang
```

## Evidence Model

| 类型 | 含义 | 示例 |
|---|---|---|
| `observed` | 机器直接测量 | CSS 变量、字体、圆角、breakpoint |
| `derived` | 可重复计算/归纳 | 主要 spacing 落在 8px scale |
| `inferred` | Agent 对设计意图的解释 | 高留白强化 premium 感 |
| `recommended` | 面向新产品的建议 | 某 Hero pattern 适合当前产品 |

任何关键 Style DNA / Case Study 结论都应能追溯到 `extraction-manifest.json`、截图或其他证据。禁止把 `inferred` / `recommended` 冒充 `observed`。

## 当前能力

- URL 设计系统逆向：Designlang + Browser fallback
- Design Tokens / Typography / Spacing / Radius / Shadow / Components
- Responsive / Interaction / Dark Mode / Motion
- Design DNA 提炼与 provenance
- Design Benchmark / Pattern Library
- Design Strategy / Design Direction
- Style Router
- Component / Asset Library
- UX Conversion Review / Design Critic Review
- Experiment / Conversion / Feedback Learning Loop

## 版本路线

```text
V1.0  Design Memory 起步
V1.1  Knowledge + Case Study + Registry
V3.2  Cyber Design Intelligence Engine
V3.3  Design Director / Direction Matching
V3.4  Benchmark + Pattern Library
V3.5  Evolution Loop
V4.0  Evidence-first Extraction Architecture  ← 当前
V4.1  Drift Monitor + scheduled re-extraction
V4.2  Cross-site Pattern Mining
V4.3  Component retrieval + style composition
```

## 上游边界

Designlang upstream：`Manavarya09/design-extract`（MIT）。

Sera 只把它作为可替换 Extraction Backend；Style DNA、Design Memory、商业判断、Style Router、生成与 Review 继续保持 Sera-native。