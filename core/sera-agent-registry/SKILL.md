---
name: sera-agent-registry
version: 1.1.0
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

# sera-agent-registry

## Purpose
Sera OPC OS 的 **Agent 注册表**：登记所有 Agent 的身份、角色、Skill 组合与模型偏好，供 Router / Planner / 各平台查询。每个 Agent 是一份完整 Agent Contract（5 文件）。

## When to use
- Router 需要知道有哪些 Agent 可用（Agent Planner 查询）
- 新 Agent 接入时注册（Agent Contract 标准化）
- 评估某 Agent 表现（evaluation.yaml）
- 跨平台加载 Agent 定义

## Inputs
- Agent 注册查询（按名称/领域）
- 新 Agent Contract（agent.yaml + system.md + memory-policy.yaml + skill-map.yaml + evaluation.yaml）

## Outputs
- Agent 注册索引（名称/领域/Skill 组合/模型偏好）
- 各 Agent 的完整 Contract 路径

## Workflow
```
1. 扫描 agents/ 目录 → 解析每个 agent 的 agent.yaml
2. 建索引：{name, role, goal, skills[], memory{read,write}, model_preference}
3. 查询：按名称/领域返回 Agent 详情
4. 接入：新 Agent 按 templates/agent.yaml 模板创建 → 注册
5. Router 的 Agent Planner 通过本注册表选择 Agent
```

## 当前注册（5 个核心 Agent）
| Agent | 领域 | 核心 Skill 组合 |
|---|---|---|
| `propfirm-agent` | business | intelligence-monitor, content-factory, browser-automation, design-studio |
| `otc-agent` | business | crm-adapter, mail-hub, memory-system |
| `trading-agent` | business | trading-analysis, finance-suite, knowledge-reader |
| `video-agent` | creative | content-factory, video-pipeline, asset-manager, compute-control |
| `design-agent` | creative | design-studio, figma-review |

## Dependencies
- `agents/*/agent.yaml`（Agent Contract 主文件）
- `templates/agent.yaml`（Agent 创建模板）
- `sera-agent-router`（Agent Planner 消费本注册表）

## Examples
- 「有哪些 Agent」→ 列出注册表
- 「video-agent 用什么模型」→ 读 agent.yaml 的 model_preference
- 「新加一个 marketing-agent」→ 按模板创建 Contract 并注册

## Iron Rules
- 每个 Agent 必须 5 文件齐全（agent.yaml/system.md/memory-policy.yaml/skill-map.yaml/evaluation.yaml）才算注册完成
- agent.yaml 是唯一权威（SKILL.md 是给人看的角色卡，agent.yaml 是给系统读的契约）
- 多 Agent 共享 Skill 允许，但 skill-map.yaml 需声明主从关系避免冲突
