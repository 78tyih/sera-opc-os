# Sera Design Intelligence System

> 架构版本：1.0.0 · 2026-08-21
> 定位：Sera Agent OS 的设计智能子系统
> 目标：发现优秀设计 → 拆解其价值 → 提取为资产与规则 → 复用至新产品

---

## 1. 系统定位

```
Sera Agent OS
│
├── Project System       ← 项目管理
├── Agent System         ← Agent 编排
├── Skill System         ← 技能体系
├── Memory System        ← 记忆系统
└── Design Intelligence System  ← 设计智能 ⭐
```

### 解决的问题

| 层 | 问题 | 答案 |
|---|---|---|
| 审美层 | 这个网站为什么好看？ | Design Case Study |
| 资产层 | 它由什么组成？ | Asset Library |
| 规则层 | 它遵循什么规律？ | Design Skill |
| 复用层 | 怎么复用？ | Template Library |
| 决策层 | 什么产品适合什么风格？ | Style Router |

---

## 2. 子系统架构

```
Design Intelligence System
│
├── 01 Case Study Engine
│   ├── design-case-study-template.md  ← 标准模板
│   ├── htx-otc-v1/                    ← 已入库
│   ├── propfirm-tv/                   ← ⏳
│   └── tradespan/                     ← ⏳
│
├── 02 Asset Library
│   ├── library-index.md               ← 资产索引
│   └── <case-name>/assets/
│       ├── logo/                      ← Logo 资源
│       ├── colors/tokens.json         ← 色彩 Token
│       ├── icons/                     ← 图标集
│       ├── images/                    ← 截图/素材
│       ├── fonts/                     ← 字体
│       └── components/                ← 组件代码
│
├── 03 Style Registry
│   ├── registry.json                  ← 风格注册表
│   └── <style-name>.json              ← 单风格定义
│
├── 04 Design Skill
│   ├── SKILL.md                       ← 技能定义
│   ├── awesome-design.md              ← 核心视觉语言
│   ├── design-system.md               ← 设计系统规范
│   ├── component-library.md           ← 组件库
│   ├── motion-guidelines.md           ← 动效指南
│   └── references/                    ← 详细规则
│
├── 05 Template Library
│   ├── index.md                       ← 模板索引
│   ├── fintech-landing/               ← 金融着陆页模板
│   └── dashboard/                     ← Dashboard 模板
│
└── 06 Design Department
    ├── Design Research Agent          ← 发现优秀设计
    ├── Design Extraction Agent        ← 拆解网站
    ├── Design System Agent            ← 生成规范
    ├── Asset Manager Agent            ← 资产管理
    ├── Design Generator Agent         ← 生成页面
    └── Design Reviewer Agent          ← 审查
```

---

## 3. 工作流

### 3.1 发现 → 入库

```
发现优秀网站
    ↓
URL / 截图 / Figma
    ↓
Capture（截图 + 提取资源）
    ↓
Extract（颜色 + 字体 + 组件 + 动效）
    ↓
Analyze（品牌 + 布局 + 转化）
    ↓
Generate Case Study
    ↓
Create Asset Library
    ↓
Register Style
    ↓
存入 Eagle / 本地
```

### 3.2 设计 → 产出

```
产品需求
    ↓
Style Router（判断适合风格）
    ↓
Load Design Skill（读取规则）
    ↓
Load Asset Library（引用资源）
    ↓
Load Template（选择模板）
    ↓
Design Generator（生成页面）
    ↓
Design Reviewer（审查）
    ↓
产出
```

### 3.3 复用 → 新项目

```
新产品：牛牛 AI
    ↓
Router 判断：AI SaaS → 科技感 · 年轻用户
    ↓
调用：Sera AI Future Style
    +
      Sera SaaS Template
    +
      牛牛 Brand Asset
    ↓
输出官网
```

---

## 4. 与外部系统的连接

### 4.1 Eagle 资产管理

```
Sera Design Intelligence
    ↓
Asset Manager Agent
    ↓
Eagle（本地素材管理）
    ↓
Local Asset Library
```

### 4.2 Vercel 部署

```
Design Generator Agent
    ↓
HTML/CSS 产出
    ↓
Vercel API
    ↓
预览 / 部署
```

### 4.3 Figma 设计稿

```
Figma URL
    ↓
Design Extraction Agent
    ↓
颜色 / 字体 / 组件提取
    ↓
Case Study
```

---

## 5. Design Registry 注册表

### 5.1 注册表结构

```json
{
  "version": "1.0.0",
  "styles": [
    {
      "id": "sera-fintech-premium",
      "name": "Sera FinTech Premium",
      "type": "visual-style",
      "based_on": ["HTX OTC", "Stripe", "Linear"],
      "best_for": ["finance", "SaaS", "AI products"],
      "assets": "eagle://sera-fintech",
      "skill_ref": "sera-design-intelligence",
      "case_studies": ["htx-otc-v1"],
      "version": "1.0.0"
    }
  ]
}
```

### 5.2 注册字段

| 字段 | 说明 |
|---|---|
| `id` | 风格唯一标识 |
| `name` | 风格名称 |
| `type` | 类型：visual-style / layout / component-set |
| `based_on` | 参考案例 |
| `best_for` | 适用场景 |
| `assets` | 资产库路径 |
| `skill_ref` | 关联 Design Skill |
| `case_studies` | 关联案例 |
| `version` | 版本号 |

---

## 6. Design Case Study 模板

详见 `design-case-study-template.md`。

每个 Case Study 必须包含：

```
00. Metadata
01. Design Overview
02. Brand DNA
03. Visual System
04. Layout Architecture
05. Component Library
06. Motion Language
07. Copywriting Pattern
08. Reproduction Prompt
09. Assets
```

---

## 7. 设计经验积累路线

```
Phase 1: HTX OTC
  ✅ Landing Page（金融信任）
  ✅ Progress Hub（Dashboard）
  ✅ Asset Library 初始化
  ✅ Style Registry 注册

Phase 2: PropFirm TV
  ⏳ 内容平台设计模式

Phase 3: TradeSpan
  ⏳ SaaS 交易软件设计模式

Phase 4: 牛牛 AI
  ⏳ AI 产品设计模式

Phase 5: Sera Design Language V1.0
  🎯 合并所有经验，形成完整设计语言
```

---

## 8. 版本记录

| 版本 | 日期 | 变更 |
|---|---|---|
| 1.0.0 | 2026-08-21 | 初始架构，基于 HTX OTC 双案例建立 |