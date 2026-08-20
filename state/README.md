# Sera Agent OS — State（工作状态）

> 回答「**现在正在发生什么**」——短期、实时、供 Router/编排器查询。

## 目录

```
state/
├── projects/       项目状态（阶段/阻塞/下一步）
├── tasks/          任务状态（进行中/待办/完成）
└── agent-status/   Agent 运行状态（忙碌/空闲/上次任务）
```

## 示例（project 状态）

```yaml
project: TradeSpan
stage: 网站开发中
blockers:
  - Logo 未完成
next_actions:
  - 完成 Logo 设计
  - 上线产品手册
updated_at: 2026-08-21
```

## 与 Memory 的区别

| | Memory | State |
|---|---|---|
| 回答 | 我过去知道什么 | 现在正在发生什么 |
| 周期 | 长期 | 短期 |
| 更新 | 任务完成时追加 | 每步推进实时更新 |
| 消费方 | Agent 上下文加载 | Router / Orchestrator |

## 写入原则

- 由 `sera-state-manager` 驱动（各 Agent 的 memory-policy.yaml 声明 state_updates）
- 任务每完成一步即更新 stage / next_actions
- 遇阻塞写入 blockers + 推荐解阻 Skill
