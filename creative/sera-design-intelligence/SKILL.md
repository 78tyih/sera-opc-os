---
name: sera-design-intelligence
version: 3.2.0
type: design-system
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

> 这不是一个"复制页面"的技能。
> 这是 Sera Agent OS 的 Cyber Design Intelligence Engine。
> 它能学习优秀设计、提炼 Design DNA、自动驱动产品设计，并通过反馈循环持续优化。

## Purpose

从已完成的设计项目中提取、沉淀并复用 Sera 的视觉语言体系。V3.2 升级为 Cyber Design Intelligence Engine，具备：
1. **学习** — 从 Benchmark 和案例中学习优秀设计
2. **提取** — 通过 DNA Engine 自动提取 Design DNA
3. **决策** — 通过 Style Router 自动选择设计方向
4. **生成** — 完整流水线自动生成设计系统
5. **优化** — 通过 Design Memory 循环持续改进

## When to Use

- 开始新产品页面设计前，需要参考过往设计经验
- 对现有项目做设计复盘，提取视觉规则
- 需要为新 Agent 提供设计规范参考
- 希望确保不同项目之间的设计一致性
- 训练 Design Agent 理解 Sera 的个人审美偏好

## Input

| 类型 | 说明 |
|---|---|
| 已有项目代码 | HTML / CSS / JS 项目目录 |
| 截图 / 设计稿 | 页面截图或 Figma 设计稿链接 |
| 产品 Brief | 产品需求文档或设计 Brief |
| 网页 URL | 已上线产品的 URL |

## Output

| 产出物 | 说明 |
|---|---|
| `awesome-design.md` | **核心设计智能文档** — Sera FinTech Visual Language V1.0 |
| `design-system.md` | 设计系统完整规范 |
| `visual-language.md` | 视觉语言详细定义 |
| `component-library.md` | 组件库定义与使用场景 |
| `motion-guidelines.md` | 动效系统指南 |
| `case-studies/*/analysis.md` | 项目案例分析 |
| `case-studies/*/extracted-rules.md` | 项目级规则提取 |
| `case-studies/*/reproduction-prompt.md` | AI Agent 可复现 Prompt |
| `styles/registry.json` | 风格注册表 |
| `assets/library-index.md` | 资产库索引 |
| `workflows/design-extraction.yaml` | 设计提取工作流 |
| `knowledge/` | 设计知识库（原则/心理/模式/商业） |
| `benchmark/` | 设计基准评分系统（6 维度评分） |
| `dna-engine/` | 设计 DNA 提取器（STYLE_DNA.json） |
| `style-router/` | 风格路由引擎（router.py + rules.yaml） |
| `memory/` | 设计记忆循环（反馈/实验/迭代） |
| `interfaces/` | 产品线接口定义 |
| `docs/DESIGN-INTELLIGENCE-V3.2.md` | V3.2 完整报告 |

## Sera Design Philosophy

### 核心信念

```
Trust（信任）
+
Technology（科技）
+
Premium（质感）
+
Conversion（转化）
```

### 设计目标

让用户 **5 秒内理解**：
- **你是谁** — 品牌定位一目了然
- **你解决什么问题** — 价值主张清晰明确
- **为什么相信你** — 信任信号可见可信

### 设计原则

| 原则 | 含义 |
|---|---|
| **Information First** | 信息层级优于视觉装饰，内容即设计 |
| **Trust Before Action** | 转化前先建立信任，信任信号前置 |
| **Consistency Over Novelty** | 一致性优于新奇感，复用优于创造 |
| **Subtle Motion** | 动效克制、统一、有目的性 |
| **Conversion Oriented** | 每个板块都有明确的客户动作 |
| **Dark Mode Ready** | 深色模式不是取反，是独立设计 |

### 设计语气

```
专业 · 克制 · 清晰 · 可信
不 aggressive · 不炫耀 · 不制造焦虑
```

## Workflow

```text
1. 输入分析：分析项目代码 / 设计稿 / URL
2. 视觉审计：提取品牌定位、色彩、字体、布局、动效、转化
3. 规则提取：将视觉决策转化为可复用的设计规则
4. 更新 awesome-design.md：将新规则写入 Sera FinTech Visual Language
5. 生成 case-study：写入 case-studies/<project>/analysis.md + extracted-rules.md
6. 更新 component-library.md：补充新组件
7. 更新 SKILL 版本

每次完成优秀项目后，自动执行以上流程。
```

## Iron Rules

1. **不复制代码**：提炼设计规律而非复制 HTML/CSS
2. **不暴露敏感信息**：不包含客户真实数据、内部审核规则、银行链路
3. **品牌一致性优先**：新项目优先参考 Design Memory 中的已有规则
4. **版本管理**：每次更新 Design Memory 时更新 SKILL 版本号
5. **跨项目可复用**：规则应设计为通用模式，而非仅适用于单一项目

## Design Memory

### 项目案例库

| 项目 | 状态 | 版本 | 核心风格 | 覆盖类型 |
|---|---|---|---|---|
| HTX OTC Landing | ✅ active | v1.0 | 金融信任 · Premium Fintech | 金融产品页 |
| HTX OTC Progress Hub | ✅ active | v1.0 | 数据驱动 · 运营 Dashboard | Dashboard |
| PropFirm TV | ⏳ pending | - | 媒体 + 信息平台 | 内容平台 |
| TradeSpan | ⏳ pending | - | 交易软件 SaaS | SaaS |
| 牛牛 AI | ⏳ pending | - | AI 产品 | AI 产品 |
| Sera Control Center | ⏳ pending | - | 管理后台 | 后台系统 |

### 文件结构

```
	sera-design-intelligence/          ← 📁 Design Intelligence System V3.2
		│
		│   # 核心文档
		├── SKILL.md                       ← 技能定义
		├── SYSTEM.md                      ← 系统架构文档
		├── README.md                      ← 系统总览
		├── awesome-design.md              ← Sera FinTech Visual Language V1.0
		├── design-system.md               ← 设计系统规范
		├── component-library.md           ← 组件库
		├── motion-guidelines.md           ← 动效指南
		├── visual-language.md             ← 视觉语言定义
		│
		│   # 设计知识库（V3.2 新增）
		├── knowledge/
		│   ├── principles/                ← 5 个设计原则
		│   ├── psychology/                ← 6 个设计心理学
		│   ├── patterns/                  ← 6 个 UI 模式
		│   └── business/                  ← 3 个商业设计框架
		│
		│   # 设计基准系统（V3.2 新增）
		├── benchmark/
		│   ├── scoring-system.md          ← 评分标准
		│   ├── benchmark-index.json       ← 基准排名
		│   ├── fintech/                   ← 金融案例
		│   ├── ai-products/               ← AI 产品案例
		│   ├── saas/                      ← SaaS 案例
		│   ├── dashboards/                ← Dashboard 案例
		│   └── landing-pages/             ← 着陆页案例
		│
		│   # Design DNA 提取器（V3.2 新增）
		├── dna-engine/
		│   ├── README.md                  ← 引擎文档
		│   ├── extraction-schema.json     ← 提取 Schema
		│   ├── dna-template.json          ← DNA 模板
		│   └── examples/                  ← 示例 DNA
		│
		│   # 风格注册表
		├── styles/
		│   └── registry.json              ← 风格 DNA 注册表 V3.0
		│
		│   # 风格路由引擎（V3.2 升级）
		├── style-router/
		│   ├── README.md                  ← 引擎文档
		│   ├── router.py                  ← 路由引擎（Python）
		│   ├── rules.yaml                 ← 路由规则（8 条）
		│   └── style-selection.json       ← 选择结果
		│
		│   # 设计记忆循环（V3.2 新增）
		├── memory/
		│   └── design-feedback/
		│       ├── experiments/           ← 实验记录
		│       ├── user-feedback/         ← 用户反馈
		│       ├── conversion-results/    ← 转化数据
		│       └── iteration-log.md       ← 迭代日志
		│
		│   # 产品线接口（V3.2 新增）
		├── interfaces/
		│   ├── design-input.schema.json   ← 输入接口
		│   └── design-output.schema.json  ← 输出接口
		│
		│   # 资产库
		├── assets/
		│   └── library-index.md           ← 资产库索引
		│
		│   # 模板库
		├── templates/
		│   ├── design-case-study-template.md
		│   ├── fintech-landing/
		│   └── dashboard/
		│
		│   # 工作流
		├── workflows/
		│   ├── design-extraction.yaml     ← 设计提取工作流
		│   └── design-intelligence-pipeline.yaml  ← 完整流水线（V3.2）
		│
		│   # 文档
		└── docs/
		    └── DESIGN-INTELLIGENCE-V3.2.md  ← V3.2 完整报告
```

## 与 Design Department 的关系

```
Design Department V3.2
│
├── Design Director Agent     → 设计战略决策（战略层）⭐
├── Design Research Agent     → 发现优秀设计（探索层）
├── Design Extraction Agent   → 拆解网站设计（提取层）
├── Design System Agent       → 生成设计规范（规范层）
├── Design Generator Agent    → 生成页面（执行层）
├── UX Conversion Agent       → 商业转化审查（转化层）⭐
├── Design Critic Agent       → 高级设计审查（审查层）
├── Design Reviewer Agent     → 审查产出（质检层）
└── Asset Manager Agent       → 资产管理（资产层）
```

| 层 | Agent | 职责 | 关联 Skill |
|---|---|---|---|
| **战略层** | `design-director-agent` | **设计战略决策** ⭐ | sera-design-intelligence |
| 探索层 | `design-research-agent` | 发现优秀设计 | sera-browser-automation |
| 提取层 | `design-extraction-agent` | 拆解网站 | sera-design-intelligence |
| 规范层 | `design-system-agent` | 生成规范 | sera-design-studio |
| 执行层 | `design-generator-agent` | 生成页面 | sera-design-studio |
| **转化层** | `ux-conversion-agent` | **商业转化审查** ⭐ | sera-design-intelligence |
| **审查层** | `design-critic-agent` | **高级设计审查** | sera-design-intelligence |
| 质检层 | `design-review-agent` | 审查产出 | figma-review |
| 资产层 | `asset-manager-agent` | 资产管理 | sera-asset-manager |
| **知识层** | **`sera-design-intelligence`** | **设计经验沉淀** | **(本 Skill)** |

## 设计经验积累路线

```
V1.0: HTX OTC
  ✅ Landing Page（金融信任）
  ✅ Progress Hub（Dashboard）

V1.1: Knowledge Engine
  ✅ 设计知识库（原则/心理/模式）
  ✅ 设计逆向工程模板
  ✅ Style DNA Registry
  ✅ Design Critic Agent
  ✅ Style Router

V3.2: Cyber Design Intelligence Engine  ← 当前
  ✅ 商业设计知识库（business/）
  ✅ Design Benchmark 评分系统
  ✅ Design DNA Extractor
  ✅ Style Router Engine（Python）
  ✅ Design Director Agent
  ✅ UX Conversion Agent
  ✅ Design Memory 循环
  ✅ Product Factory 接口
  ✅ 完整设计流水线

V3.3: 自动化增强
  ⏳ DNA 自动提取
  ⏳ 评分自动化
  ⏳ 集成到 Product Factory 流水线

V3.4: 智能学习
  ⏳ 设计趋势分析
  ⏳ 竞品设计监控
  ⏳ 用户反馈闭环

V3.5: 全自动化
  ⏳ 端到端设计流水线
  ⏳ A/B 测试自动设计
  ⏳ 设计系统自修复
```

## 调用方式

当 Agent 需要设计新产品页面时：

1. 调用 `sera-design-intelligence` 获取设计规范
2. 读取 `awesome-design.md` 了解 Sera 视觉语言
3. 在 `case-studies/` 中查找相似项目案例
4. 参考 `component-library.md` 选择组件
5. 调用 `sera-design-studio` 执行前端开发