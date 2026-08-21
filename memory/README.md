# Sera OPC OS — Memory（长期记忆）

> 回答「**我过去知道什么**」——长期、稳定、跨会话。

## 目录

```
memory/
├── long-term/      长期事实（用户偏好、系统规则、项目背景）
├── knowledge/      知识（研究报告、领域资料、方法论）
└── preference/     偏好（设计偏好、沟通风格、工作习惯）
```

## 与 State 的区别

| | Memory | State |
|---|---|---|
| 回答 | 我过去知道什么 | 现在正在发生什么 |
| 周期 | 长期 | 短期 |
| 例子 | 「Sera 喜欢深蓝色设计」「TradeSpan 是 MT4/MT5 软件」 | 「TradeSpan 网站开发中，阻塞：Logo 未完成」 |
| 存储 | `memory/`（本目录） | `state/`（../state/） |

## 写入原则

- 只写**已验证**的事实（decision / lesson / fact / preference）
- 由 `sera-memory-system` + 各 Agent 的 `memory-policy.yaml` 驱动
- 与 SeraContextHub 双写：工作区 memory 照常写，跨项目长期内容进 Hub
