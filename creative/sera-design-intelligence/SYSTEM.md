# Sera Design Intelligence System

> 架构版本：3.2.0 · 2026-08-21
> 定位：Sera Agent OS 的 Cyber Design Intelligence Engine
> 目标：学习优秀设计 → 提炼 Design DNA → 自动驱动产品设计 → 持续反馈优化

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
| 知识层 | 设计为什么有效？ | Knowledge Architecture |
| 审美层 | 这个网站有多好？ | Design Benchmark |
| 资产层 | 它由什么组成？ | Asset Library |
| 规则层 | 它遵循什么规律？ | Design Skill |
| DNA层 | 它的设计基因是什么？ | DNA Engine |
| 复用层 | 怎么复用？ | Template Library |
| 决策层 | 什么产品适合什么风格？ | Style Router |
| 记忆层 | 上次怎么做？结果如何？ | Design Memory |

---

## 2. 子系统架构

```
Design Intelligence System V3.2
│
├── 01 Knowledge Architecture (V3.2)
│   ├── principles/      ← 5 个设计原则
│   ├── psychology/      ← 6 个设计心理学
│   ├── patterns/        ← 6 个 UI 模式
│   └── business/        ← 3 个商业设计框架
│
├── 02 Design Benchmark (V3.2)
│   ├── scoring-system.md       ← 6 维度评分标准
│   ├── benchmark-index.json    ← 排名榜
│   └── <category>/             ← 分类案例
│
├── 03 DNA Engine (V3.2)
│   ├── extraction-schema.json  ← 提取 Schema
│   ├── dna-template.json       ← DNA 模板
│   └── examples/               ← 示例
│
├── 04 Case Study Engine
│   ├── design-case-study-template.md  ← 标准模板
│   ├── htx-otc-v1/                    ← 已入库
│   ├── propfirm-tv/                   ← ⏳
│   └── tradespan/                     ← ⏳
│
├── 05 Asset Library
│   ├── library-index.md               ← 资产索引
│   └── <case-name>/assets/
│
├── 06 Style Registry
│   ├── registry.json                  ← 风格 DNA 注册表 V3.0
│   └── <style-name>.json              ← 单风格定义
│
├── 07 Style Router (V3.2)
│   ├── router.py                      ← 路由引擎（Python）
│   ├── rules.yaml                     ← 8 条路由规则
│   └── style-selection.json           ← 选择结果
│
├── 08 Design Memory (V3.2)
│   └── design-feedback/
│       ├── experiments/               ← 实验记录
│       ├── user-feedback/             ← 用户反馈
│       ├── conversion-results/        ← 转化数据
│       └── iteration-log.md           ← 迭代日志
│
├── 09 Design Skill
│   ├── SKILL.md                       ← 技能定义
│   ├── awesome-design.md              ← 核心视觉语言
│   ├── design-system.md               ← 设计系统规范
│   ├── component-library.md           ← 组件库
│   ├── motion-guidelines.md           ← 动效指南
│   └── references/                    ← 详细规则
│
├── 10 Template Library
│   ├── index.md                       ← 模板索引
│   ├── fintech-landing/               ← 金融着陆页模板
│   └── dashboard/                     ← Dashboard 模板
│
├── 11 Product Factory Interfaces (V3.2)
│   ├── design-input.schema.json       ← 输入接口
│   └── design-output.schema.json      ← 输出接口
│
└── 12 Design Department
    ├── Design Director Agent          ← 设计战略决策（战略层）⭐
    ├── Design Research Agent          ← 发现优秀设计
    ├── Design Extraction Agent        ← 拆解网站
    ├── Design System Agent            ← 生成规范
    ├── Design Generator Agent         ← 生成页面
    ├── UX Conversion Agent            ← 商业转化审查（转化层）⭐
    ├── Design Critic Agent            ← 高级设计审查
    ├── Design Reviewer Agent          ← 审查
    └── Asset Manager Agent            ← 资产管理
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

### 3.3 设计智能流水线（V3.2）

```
Product Input
    ↓
Design Director（确定设计方向）
    ↓
Psychology Analysis（市场心理学分析）
    ↓
Style Router（风格路由匹配）
    ↓
DNA Match（Design DNA 匹配）
    ↓
Design System Generate（设计系统生成）
    ↓
Page Generate（页面生成）
    ↓
UX Conversion Review（转化审查门禁）
    ↓
Design Critic（设计总监审查门禁）
    ↓
Asset Generation（资产生成）
    ↓
Memory Update（设计记忆更新）
    ↓
Output
```

### 3.4 设计记忆循环

```
Design → Deploy → Data Feedback → Optimization → New Rule → Knowledge Update
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

## 7. 版本记录

| 版本 | 日期 | 变更 |
|---|---|---|
| 1.0.0 | 2026-08-21 | 初始架构，基于 HTX OTC 双案例建立 |
| 1.1.0 | 2026-08-21 | Knowledge Engine：知识库 + 逆向工程 + DNA Registry |
| 3.2.0 | 2026-08-21 | Cyber Design Intelligence Engine：9 Agents + Pipeline + Memory Loop |