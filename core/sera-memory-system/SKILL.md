---
name: sera-memory-system
version: 1.0.0
author: Sera
category: core
compatible:
  - WorkBuddy
  - Codex
  - Trae
  - Claude-Code
status: skeleton
---

# sera-memory-system

## Purpose
Sera Agent OS 的共享记忆层：统一管理 Context Hub（用户偏好/系统规则/活动项目）、Obsidian 知识库（报告/文档/决策/研究）、项目状态（当前状态/下一步/历史决策）。

原则：**"Agents forget. Systems remember."**（Agent 会遗忘，系统会记住）

## When to use
- 会话开始需要加载项目上下文 / 用户偏好
- 任务完成需要归档产物、更新项目状态、记录决策
- 跨 Agent 交接需要同步记忆

## Inputs
- 会话上下文需求（项目名 / 用户 ID）
- 待归档产物（报告/文档/决策记录）
- 项目状态更新

## Outputs
- 会话开始：加载的全局 + 项目上下文
- 会话结束：更新的 CURRENT_STATE / AGENT_HANDOFF / MEMORY.jsonl 追加
- 知识归档：Obsidian 入库记录

## Workflow
```
1. SESSION START：读 Context Hub 全局 + 项目上下文
2. 执行任务（调用各域 Skill）
3. SESSION END：覆写 CURRENT_STATE → 更新 AGENT_HANDOFF → 追加 MEMORY.jsonl
4. 产物归档：sera-knowledge-sync 写入 Obsidian
5. 重大决策：写 Decision Logs（ADR）
```

## Components
| 组件 | 对应 Skill | 职责 |
|---|---|---|
| Context Hub | `sera-context-system` | 用户偏好/系统规则/活动项目，多 Agent 共享 |
| Obsidian 知识库 | `sera-knowledge-sync` | 报告/文档/决策/研究归档，去重+版本化 |
| Project Memory | 工作区 `.workbuddy/memory/` | 当前状态/下一步/历史决策 |

## Dependencies
- `sera-context-system`（Context Hub 协议）
- `sera-knowledge-sync`（Obsidian 归档）

## Examples
- 「上次在 PropFirm-TV 项目做到哪了」→ SESSION START 加载
- 「记录这个决定」→ MEMORY.jsonl 追加 decision + ADR
- 「把今天的报告归档」→ sera-knowledge-sync
