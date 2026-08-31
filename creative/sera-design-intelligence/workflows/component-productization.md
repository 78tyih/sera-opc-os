# Workflow — Component Productization

> 将真实项目里的优秀组合组件沉淀为可复用、可检索、可销售的 Sera Component Asset。

## Trigger

当一个真实项目出现以下情况时触发：

- 某一 UI 模块明显解决了重复出现的业务问题；
- 该模块可在其他行业或品牌中复用；
- 用户主动要求“把这个设计打包成模板 / Skill / 零件”；
- 同一结构已在两个以上项目中出现；
- Review 认为该模块包含值得保留的设计判断。

## Pipeline

```text
1. Identify Candidate
2. Verify Real Usage
3. Separate Primitive vs Composite
4. Extract Business Intent
5. Extract Visual / Interaction DNA
6. Remove Brand & Sensitive Data
7. Define Component Contract
8. Register Relationships
9. Build Generic Demo
10. Review
11. Promote to Ready
12. Package / Sell / Reuse
```

## Step 1 — Identify Candidate

记录：

- source project
- source screen / section
- original problem
- why it worked
- repeated use potential

不要因为视觉好看就自动抽取。必须先说明组件承担的业务任务。

## Step 2 — Primitive Gate

以下通常不进入 Sera Component Library：

- Button
- Input
- Checkbox
- Avatar
- Badge
- Tabs
- Modal

除非它们已经组成带明确业务任务的 Composite Component。

优先抽取：

- Executive Summary Card
- High-Trust Hero
- Multi-Step Lead Form
- Pipeline Board
- Dependency Map

## Step 3 — Component Contract

每个组件至少定义：

```yaml
id:
name:
category:
business_intent:
source_projects:
style_refs:
template_refs:
use_cases:
required_data:
optional_data:
visual_rules:
interaction_rules:
responsive_rules:
accessibility_rules:
anti_patterns:
status:
```

## Step 4 — De-brand / De-risk

必须删除：

- 公司专属 Logo / 商标
- 客户真实姓名 / UID / 邮箱 / 账号
- 内部目标、绩效信息、未公开财务信息
- 私有业务条款与不可公开流程

允许保留：

- 信息架构
- 组件布局
- 交互逻辑
- 视觉 Token
- 状态语义
- 通用业务字段

## Step 5 — Relationship Registration

组件必须至少关联以下对象中的两个：

```text
Style DNA
Template
Case Study
Skill
```

这样 Agent 才能回答：

- “这种风格有哪些可用组件？”
- “这个模板由哪些组件组成？”
- “这个组件来自哪个真实案例？”

## Step 6 — Demo

Generic Demo 不允许只是组件截图。

Demo 必须展示：

1. 正常状态
2. Hover / Open / Active 等关键状态
3. Light / Dark（若支持）
4. Desktop / Mobile 基本适配
5. 一段合理的假数据

## Step 7 — Review Gate

Promote 为 `ready` 之前检查：

- [ ] 真实项目验证过
- [ ] 业务意图明确
- [ ] 非低价值 primitive 重复造轮子
- [ ] 已脱敏
- [ ] 可跨品牌复用
- [ ] 数据合同明确
- [ ] 有至少一个 Demo
- [ ] Style / Template / Case 引用正确
- [ ] Agent selection rule 可表达

## Step 8 — Commercial Packaging

### Component Pack

```text
README
registry entry
component spec
reference implementation
sample data
design tokens
prompt / agent usage
```

### Solution Pack

```text
Style Pack
+ Component Pack
+ Template
+ Skill
+ Demo
+ Deployment Guide
```

## Output

```text
component-library/
├── registry.json
├── README.md
├── demo.html
└── specs/
    └── <component-id>.md
```

## Core Principle

> 不保存“长得像什么”，而保存“为什么这样设计、什么时候应该再次这样设计”。
