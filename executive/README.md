# Executive

> 高管智能体 — Executive Council 的 8 名核心成员。

## 当前状态

从 `sera-agent-os` 迁移中。现有 `agents/executive/sera-ceo-agent/` 已就位。

## 需要补充的高管

| Agent | ID | 状态 |
|-------|-----|------|
| CEO Agent | SERA-CEO-001 | ✅ 已存在 |
| CSO Agent | SERA-CSO-001 | ❌ 待创建 |
| CPO Agent | SERA-CPO-001 | ❌ 待创建 |
| CTO Agent | SERA-CTO-001 | ❌ 待创建 |
| CAIO Agent | SERA-CAI-001 | ❌ 待创建 |
| COO Agent | SERA-COO-001 | ❌ 待创建 |
| CMO Agent | SERA-CMO-001 | ❌ 待创建 |
| CRO Agent | SERA-CRO-001 | ❌ 待创建 |

## 标准 Contract

每个高管 Agent 必须包含 7 文件标准：

```
agent-name/
├── identity.yaml
├── system.md
├── mission.md
├── skill-map.yaml
├── workflow.yaml
├── memory-policy.yaml
└── evaluation.yaml
```