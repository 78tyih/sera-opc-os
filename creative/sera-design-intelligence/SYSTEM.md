# Sera Design Intelligence System V4

> 架构版本：4.0.0 · 2026-08-31
> 定位：Sera OPC OS 的 **Evidence-first Design Intelligence System**
> 目标：把外部优秀设计转化为可验证、可解释、可检索、可组合、可学习的长期设计能力。

## 1. V4 架构修正

V3.x 已具备 Design Director、Benchmark、DNA Engine、Style Router、Pattern Library 与 Evolution Loop，但 URL 逆向仍把“观察事实 + 推断规律 + 审美判断”混在同一个 Agent 中。

V4 改为：

```text
Machine Extraction
      ↓
Normalized Evidence
      ↓
Design DNA
      ↓
Design Reasoning
      ↓
Design Memory
```

核心原则：**Machine measures. Agent reasons. Memory learns.**

## 2. 六层模型

```text
Sera Design Intelligence V4
│
├── L0 Capture & Extraction
│   ├── Designlang URL backend
│   ├── Browser capture
│   └── Figma / local code adapters
├── L1 Evidence & Provenance
│   ├── raw artefacts
│   ├── extraction-manifest.json
│   ├── evidence type
│   └── confidence / conflicts
├── L2 Understanding
│   ├── DNA Engine
│   ├── Design Strategy
│   ├── Psychology
│   ├── Benchmark
│   └── Pattern Mining
├── L3 Memory
│   ├── Case Studies
│   ├── Style Registry
│   ├── Pattern Library
│   ├── Component Library
│   └── Asset Index
├── L4 Create
│   ├── Design Direction
│   ├── Style Router
│   ├── Design System
│   └── Generator
└── L5 Review & Learn
    ├── UX Conversion Gate
    ├── Design Critic Gate
    ├── Experiments
    ├── Conversion Feedback
    └── Rules Engine
```

## 3. Extraction Layer

### Default Backend: Designlang

Designlang 负责 rendered DOM / computed style 等机器事实。Sera 不依赖其“观点”，只依赖机器可读 artefacts。

```text
URL → designlang → raw/designlang/* → Sera Adapter → normalized/extraction-manifest.json
```

### Backend 可替换

上层只依赖 `extraction-contract.schema.json`。未来可接自研 Playwright Extractor、Figma Variables Extractor、Browser MCP、Chrome DevTools Protocol 或其他 Design Token 工具。

只要输出：

```text
Extraction Manifest + Artefact Index + Provenance + Capture Flags + Quality State
```

DNA / Case / Memory 层不需要修改。

### Fallback

```text
designlang fail
   ↓
sera-browser-automation
   ↓
DOM / CSS / screenshot capture
   ↓
manual normalized manifest
```

Fallback 必须记录 `fallback_used: true`。

## 4. Evidence Model

- `observed`：机器直接观察到
- `derived`：由 observed facts 可重复计算
- `inferred`：Agent 对设计意图、品牌、心理和体验的解释
- `recommended`：面向当前产品的设计建议

规则：

```text
observed → 可直接进入 evidence
derived → 必须引用 observed
inferred → 必须声明 confidence
recommended → 必须声明目标产品/场景
```

任何关键 Style DNA 字段必须拥有 evidence ref。

## 5. Raw / Normalized / Intelligence

```text
case-studies/<case>/raw/                              # immutable upstream evidence
case-studies/<case>/normalized/extraction-manifest.json
case-studies/<case>/dna/STYLE_DNA.json
case-studies/<case>/analysis.md
case-studies/<case>/extracted-rules.md
```

`normalized` 是 Sera 自己的稳定接口，用来隔离上游工具未来的文件名/Schema 变化。

## 6. DNA Engine V4

DNA Engine 不再负责爬网页，而负责：

```text
Normalized Evidence → Feature Synthesis → Design DNA → Evidence Mapping
```

STYLE_DNA 可包含 brand personality、color system、typography、layout、components、responsive、interaction states、motion、dark mode、accessibility、CSS health、conversion patterns、provenance、evidence 与 confidence。

## 7. Design Understanding

Extraction 结束后才进入“为什么”。Design Strategy / Analyst 负责判断信息层级、品牌语气、第一印象、信任、CTA / Conversion、motion、跨项目 pattern、适用/不适用场景。

## 8. Memory Promotion

```text
External Website
      ↓
Raw Evidence
      ↓
Normalized Evidence
      ↓
Case-local Analysis
      ↓
Design Review
      ↓
Candidate Pattern / Component / Style
      ↓
Benchmark / User Feedback / Outcome
      ↓
Canonical Design Memory
```

Promotion 至少要求 provenance、evidence、跨项目复用价值、第三方资产边界清晰、Reviewer 通过。

## 9. Design Drift

V4 预留 Drift Layer：

```text
Extraction A → Canonical Snapshot → Re-extraction B → Token/Component/Motion Diff → Meaningful Change Classifier → Update Candidate
```

上游 drift / visual diff 只负责发现变化；Sera 负责判断变化是否值得进入 Design Memory。计划在 V4.1 接入定时监控。

## 10. 生产流水线

```text
Product Brief
    ↓
Design Director
    ↓
Reference Set
    ↓
[URL exists?] yes → Evidence Extraction / no → Existing Memory
    ↓
Psychology / Strategy
    ↓
Style Router
    ↓
DNA / Pattern Match
    ↓
Design System
    ↓
Page Generator
    ↓
UX Conversion Gate
    ↓
Design Critic Gate
    ↓
Assets → Design Memory
```

## 11. Design Department V4

| Agent | 主要职责 |
|---|---|
| Design Director | 设计方向最终决策 |
| Design Strategy | 市场 / 竞品 / 差异化策略 |
| Design Research | 发现参考与 Reference Set |
| Design Extraction | 机器提取编排、归一化、证据质量 |
| Design System | 生成可执行系统规范 |
| Design Generator | 页面/组件产出 |
| UX Conversion | 商业转化门禁 |
| Design Critic | 视觉/品牌高级审查 |
| Design Reviewer | 实现一致性审查 |
| Asset Manager | 资产索引与入库 |

V4 最大变化：Design Extraction Agent 从“视觉猜测者”改为 **Extraction Orchestrator + Evidence Curator**。

## 12. Security / Legal Boundary

- 不把 cookie / token / session 写入 Git。
- `cookie-file` 只作为运行时输入，manifest 只记录 authenticated true/false。
- 不默认复制第三方源代码。
- 不默认把第三方 Logo / Illustration / Photo 当作生产资产。
- 对自有项目可执行更深的 code-level extraction。

## 13. Failure Semantics

| 情况 | 行为 |
|---|---|
| Designlang 未安装 | `npx` 临时运行；失败则 fallback |
| Chromium / Playwright 异常 | doctor fail，记录 quality |
| SPA 未加载完整 | 增加 wait / interaction capture |
| Auth 页面 | runtime cookie-file，不持久化秘密 |
| Screenshot 与 token 冲突 | 记录 conflict，不静默覆盖 |
| 某字段缺失 | unknown / omit，不让 LLM 填假值 |
| Backend 输出变化 | Adapter 重映射，DNA 层保持不变 |

## 14. V4 文件

```text
extraction-engine/
├── README.md
├── adapter.py
├── designlang-adapter.yaml
└── extraction-contract.schema.json

workflows/
├── design-extraction.yaml
└── design-intelligence-pipeline.yaml

dna-engine/
└── extraction-schema.json
```

## 15. 版本记录

| 版本 | 日期 | 变更 |
|---|---|---|
| 1.0 | 2026-08-21 | Design Memory 初版 |
| 1.1 | 2026-08-21 | Knowledge Engine |
| 3.2 | 2026-08-21 | Cyber Design Intelligence |
| 3.3 | 2026-08-21 | Design Direction / Director |
| 3.4 | 2026-08-21 | Benchmark / Pattern Intelligence |
| 3.5 | 2026-08-21 | Evolution Loop |
| **4.0** | **2026-08-31** | **Evidence-first + Designlang Extraction Backend** |