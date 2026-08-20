---
name: sera-state-manager
version: 1.0.0
author: Sera
category: core
status: skeleton
compatible:
  - WorkBuddy
  - Codex
  - Trae
  - Claude-Code
  - Cursor
---

# sera-state-manager

## Purpose
Sera Agent OS 的**工作状态管理器**：记录「当前正在发生什么」——活动项目的当前阶段、阻塞项、下一步行动。与 Memory（过去发生什么）互补，为 Agent Router 提供实时状态输入。

> Memory 回答「我们做过什么」，State 回答「我们现在在哪、下一步去哪」。

## When to use
- Agent 恢复工作时需要知道项目停在哪、卡在哪
- 编排器需要判断某个 Skill/Agent 是否可以继续推进
- 多 Agent 接力时交接「进行中」状态（非已完成历史）

## Inputs
- 项目名 / 活动会话标识
- 状态更新：当前阶段、阻塞项、下一步行动、最近一次产出

## Outputs
- 结构化状态快照：`{project, stage, blockers[], next_actions[], last_output, updated_at}`
- 状态变更记录（可回溯）

## Workflow
```
1. SESSION START：读当前项目状态快照（阶段/阻塞/下一步）
2. 任务推进：Agent 每完成一步，更新 stage / next_actions
3. 遇阻塞：写入 blockers + 推荐解阻 Skill
4. SESSION END：状态快照落盘（与 Memory 分开存储）
5. Router 查询：按项目返回最新状态
```

## 状态示例（PropFirm TV）

```yaml
project: PropFirm TV
stage: 视频工厂测试
blockers:
  - HeyGen 动作优化
next_actions:
  - 生成 5 条 benchmark
last_output: null
updated_at: 2026-08-21
```

## 与 Memory 的关系
| 维度 | sera-memory-system | sera-state-manager |
|---|---|---|
| 回答 | 过去发生什么 | 当前正在发生什么 |
| 数据 | 决策/经验/偏好/历史 | 阶段/阻塞/下一步 |
| 更新 | SESSION END 追加 | 每步推进实时更新 |
| 消费方 | Agent 上下文加载 | Agent Router / Orchestrator |

## Dependencies
- `sera-agent-orchestrator`（路由时查询状态）
- `sera-memory-system`（长期记忆，两者互补）

## Examples
- 「PropFirm TV 项目现在卡在哪」→ 返回状态快照（stage/blockers/next）
- 「继续上次的视频工厂测试」→ 加载状态 → 解阻 → 推进 next_actions
