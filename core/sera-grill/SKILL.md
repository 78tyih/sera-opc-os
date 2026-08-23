---
name: sera-grill
version: 1.0.0
author: Sera
category: core
status: active
compatible:
  - WorkBuddy
  - Codex
  - Trae
  - Claude-Code
  - Cursor
---

# sera-grill

## Purpose

Sera OPC OS 的前置决策澄清 Skill。用于在目标、范围、优先级或关键取舍尚未清楚时，通过**一次一个高杠杆问题**把模糊想法收敛成可执行的 Shared Understanding，然后再交回 Router / 下游 Skill 执行。

它不是“问卷”，也不是“把所有问题一次丢给用户”。它是一棵动态决策树：**上一题的答案决定下一题。**

## Invocation aliases

以下表达可显式触发：

- `SERA_GRILL`
- `GRILL_ME`
- `grill me`
- `grillme`
- `greenme`
- `盘问我`
- `追问我`
- `帮我想清楚`

## When to use

优先用于：

- 新产品 / 新项目 / 新架构
- 复杂工作流
- 重要技术选型
- 目标或 Scope 模糊
- 用户同时表达多个互相竞争的目标
- 存在明显 trade-off，但尚未确定优先级
- 用户说“我想做一个……”但真正 outcome 尚不清楚

## When NOT to use

不要用于：

- 简单事实查询
- 翻译 / 改写
- 单个明确修改
- 已有清晰 Spec 的执行任务
- 用户明确要求“直接执行，不要继续澄清”，且没有安全/关键阻塞信息缺失

原则：**Grill 是为了减少返工，不是为了制造对话仪式。**

## Five Iron Rules

### 1. 一次只问一个最高杠杆问题

不要预先生成 Q1–Q15。每次只处理当前最上游、最能改变后续方案的一个未决问题。

回答后重新计算决策树，再决定下一问。

### 2. 每个问题必须带推荐答案与理由

不要只问“你怎么看？”

优先使用：

```text
当前关键决策：...

问题：A / B / C 你更接近哪一个？

我的建议：B。
理由：...
```

推荐答案是可被用户推翻的建议，不是替用户做决定。

### 3. 能查到的事实自己查，只问 Judgment

Agent 负责 Research；用户负责 Judgment。

能够通过仓库、文件、配置、工具、公开资料验证的事实，不要反问用户。

只询问必须由用户决定的内容，例如：

- 哪个目标优先
- 愿意接受什么 trade-off
- 什么属于 non-goal
- 什么结果才算成功
- 哪个约束不可妥协

### 4. 每次确认都形成 Decision Checkpoint

每个回答后更新：

```text
CONFIRMED
- 已确认决策

REJECTED
- 已明确否定的方向

OPEN
- 仍未解决的关键问题
```

Checkpoint 是会话状态 / Memory Candidate，不得自动升级成 Canonical Fact；长期沉淀由 `sera-context-system` / Memory Gate 决定。

### 5. Shared Understanding 完成后立即退出

不要为了“问得更完整”继续盘问。

当剩余未知不再会改变当前下一步执行方式时，停止 Grill，生成最终收敛结果并交回 Router。

## Dialogue Loop

```text
Load known context
      ↓
Find highest-leverage unresolved decision
      ↓
Ask ONE question + recommendation + reason
      ↓
User answer
      ↓
Is answer clear and internally consistent?
  ├─ No → challenge / narrow / resolve contradiction
  └─ Yes
      ↓
Record Decision Checkpoint
      ↓
Recompute decision tree
      ↓
Does another unresolved decision change the next action?
  ├─ Yes → loop
  └─ No → Shared Understanding → handoff
```

## Challenge behavior

不要机械接受答案。发现以下情况时继续追问：

- 用户同时选择两个互斥优先级
- 回答的是 solution，但真正 goal 仍未知
- 回答与此前已确认 decision 冲突
- 用户回避必要 trade-off
- success criteria 无法判断真假

挑战时指出**具体矛盾**，不要泛泛说“还需要更多信息”。

## Exit Contract

退出 Grill 时只输出以下结构：

```text
GOAL
- 真正要实现的结果

NON-GOALS
- 当前明确不做什么

CONFIRMED DECISIONS
- 用户已经明确确认的关键决策

ASSUMPTIONS
- 当前仍依赖、但尚未完全验证的前提

TRADE-OFFS
- 已接受的取舍

OPEN QUESTIONS
- 不阻塞当前执行、但后续仍需解决的问题

SUCCESS CRITERIA
- 如何判断这一步做成

NEXT ACTION
- 当前最小、最具体的下一步
```

然后把这份 Shared Understanding 交回 `sera-agent-router` / `sera-agent-orchestrator`，进入 Research、Planning 或 Execution。

## Product workflow integration

当 `developing-products` 遇到新产品、新项目或 Scope 尚不清楚时：

```text
创始灵感
   ↓
sera-grill
   ↓
Shared Understanding
   ↓
深度调研
   ↓
交叉评审 / 失败推演
   ↓
最小验证
```

如果目标、用户、Wedge、成功标准已经明确，则可以跳过 Grill，避免重复澄清。

## Examples

### Example A — 新项目

用户：

> 我想做一个统一 AI Context 系统。

不要立刻讨论数据库、Graph、MCP。

先问：

```text
当前最上游决策：这是你自己使用的工作流，还是准备做成对外产品？

我的建议：先按“自己使用”定义，因为你现在的直接痛点是多个 Agent 上下文断裂；如果未来验证出通用需求，再决定是否产品化。
```

### Example B — 混合目标

用户：

> 我希望这个课程既赚钱，又建立行业权威。

不要直接接受两个并列目标。

追问哪个目标是第一优先级，以及为了第一目标愿意牺牲什么。

## Iron Boundaries

- 用户决定 ≠ Agent 推荐
- 事实 ≠ 假设
- 已确认 ≠ 已验证
- Decision Checkpoint ≠ Canonical Memory
- 一次只问一个问题
- 用户已明确的信息不得重复询问
- 不允许为了 Grill 而 Grill
