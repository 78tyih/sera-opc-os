# Sera Component Library

> 把经过真实项目验证的优秀 UI 零件，从项目源码中抽离、脱敏、标准化，并变成 Agent 与人都能直接复用的组件资产。

## 1. 定位

Sera Component Library 不是通用 UI Framework，也不试图替代 shadcn/ui、Radix 或 Ant Design。

它保存的是 **“具有明确业务意图的高价值组件”**：

- 不是一个普通 Card，而是 `Executive Summary Card`
- 不是一个普通 Stepper，而是 `Process Stepper`
- 不是一个普通 Sidebar，而是 `Command Sidebar`
- 不是一个普通 Form，而是 `Multi-Step Lead Form`

每个组件都必须说明：

1. 它解决什么业务问题；
2. 哪个真实项目验证过；
3. 适合什么场景；
4. 应该与什么 Style / Template 搭配；
5. Agent 在什么条件下应该选择它。

## 2. 四级资产关系

```text
Real Project
   ↓
Case Study
   ↓
Design DNA / Style
   ↓
Component
   ↓
Template
   ↓
Skill / Agent Generation
```

组件处于 Design DNA 与 Template 之间：

- Style 定义“长什么样、感觉如何”；
- Component 定义“这个零件解决什么问题”；
- Template 定义“如何组合成完整解决方案”；
- Skill 定义“Agent 什么时候、如何使用这些资产”。

## 3. 首批组件

### Foundation / Navigation
- Aurora Background
- Floating Glass Navigation
- Command Sidebar

### Trust / Conversion
- High-Trust Hero
- Trust / Compliance Card
- Process Stepper
- Multi-Step Lead Form

### Management / Data
- Executive Summary Card
- KPI Metric Card
- Workstream Progress Card
- Status Pipeline Board
- Timeline / Gantt
- Dependency Map

完整机器可读索引见 `registry.json`。

## 4. 商品化方式

### Component Pack
适合设计师、开发者、AI Builder。

包含：
- 组件说明
- Design Tokens
- HTML / CSS / React 实现参考
- Dark / Light 规则
- Responsive 规则
- Prompt / Skill 触发规则

### Template Pack
多个组件已经组合成完整页面。

例如：
- Regulated Deal Desk
- Execution Command Center

### Solution Pack
面向非设计用户交付：

```text
Design System
+ Components
+ Template
+ Sample Data
+ Agent Skill
+ Deployment Guide
```

## 5. 组件进入资产库的门槛

一个组件至少满足 4 条才注册：

- 已在真实项目使用；
- 有明确、重复出现的业务任务；
- 更换品牌 / 数据后仍有价值；
- 能被单独描述和调用；
- 与普通 UI primitive 有显著区别；
- 可以形成可测试的使用规则。

禁止为了数量把 Button、Input、Badge 等所有 primitive 都注册成“设计资产”。基础 primitive 应依赖成熟 UI Library，本库只保存具有 Sera 设计判断和业务经验的组合组件。

## 6. Agent 选择逻辑

当 Agent 生成页面时，顺序应为：

```text
Intent
→ Audience
→ Trust / Information Density
→ Style DNA
→ Component Selection
→ Template Composition
→ Content/Data Binding
→ Review
```

示例：

- 高信任金融服务：`High-Trust Hero + Trust Compliance Card + Process Stepper + Multi-Step Lead Form`
- CEO 周报：`Executive Summary Card + KPI Metric Card + Workstream Progress + Blockers`
- 复杂项目：再增加 `Timeline / Gantt + Dependency Map + Command Sidebar`

## 7. 来源与安全

组件可以来源于真实商业项目，但进入公共/通用资产库之前必须：

- 删除公司专属 Logo 与商标；
- 删除客户、金额、邮箱、账户等敏感数据；
- 删除内部 KPI / PIP / 合规材料；
- 将业务文案替换为通用示例；
- 保留结构、交互、布局与设计经验。

**复用设计规律，不复制敏感业务内容。**
