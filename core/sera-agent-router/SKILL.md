---
name: sera-agent-router
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

# sera-agent-router

## Purpose
Sera Agent OS 的 **Agent Router**：把用户自然语言请求自动解析为 Agent/Skill 编排链。输入一句话，输出「该用哪个 Agent、按什么顺序调用哪些 Skill」的执行计划。是 Agent Orchestrator 的规则引擎。

## When to use
- 任何进入 Sera Agent OS 的用户请求（编排器入口）
- 需要把任务自动路由到 5 个核心 Agent（propfirm/otc/trading/video/design）之一
- 复合任务需要多 Agent 编排（如「做产品发布页」→ 多 Agent 链）

## Inputs
- 用户自然语言请求（如「做一条 PropFirm.TV 视频」）
- 路由规则表（`routes.yaml`，同目录）

## Outputs
- 编排链 JSON：`{matched, route{id,intent,agent}, pipeline[], finalize[], query}`
- pipeline = 有序 Skill 链；finalize = 收尾归档链

## Workflow
```
1. 接收自然语言输入
2. 归一化（小写/去标点）
3. 逐路由规则匹配关键词（优先级从上到下，任一命中即停）
4. 命中 → 输出编排链；未命中 → fallback 到 orchestrator
5. 编排器按 pipeline 依序调用各 Agent/Skill
6. 完成后执行 finalize（归档/更新状态）
```

## Tools
- Bash：`python3 router.py "<用户请求>"`（规则引擎，纯 stdlib）
- 配置：`routes.yaml`（路由规则，可扩展）

## 路由规则（routes.yaml）
| route | intent | agent | pipeline |
|---|---|---|---|
| `compute` | 远程算力 | core | sera-compute-control |
| `video-produce` | 视频/素材生产 | video-agent | content-factory → video-pipeline → asset-manager → compute-control |
| `page-product-launch` | 产品发布页（多 Agent） | multi | propfirm-agent → design-agent → video-agent → figma-review |
| `propfirm-intel` | PropFirm 情报/竞品 | propfirm-agent | intelligence-monitor → browser-automation → content-factory |
| `design-produce` | 设计/品牌/UI/海报 | design-agent | design-studio → figma-review |
| `trading-research` | 交易研究/复盘 | trading-agent | trading-analysis → finance-suite → knowledge-reader |
| `otc-bd` | OTC 商务/客户 | otc-agent | crm-adapter → mail-hub → memory-system |
| `knowledge-ops` | 知识/记忆/归档 | core | context-system → state-manager → knowledge-sync |
| `fallback` | 未匹配 | orchestrator | sera-agent-orchestrator（人工/LLM 判定） |

## Examples
```bash
# 路由一个请求
python3 router.py "做一条 PropFirm.TV 视频"
# → video-agent: [sera-content-factory, sera-video-pipeline, sera-asset-manager, sera-compute-control]

# 多 Agent 复合任务
python3 router.py "帮我做 TradeSpan 产品发布页"
# → multi: [propfirm-agent, design-agent, video-agent, figma-review]

# 列出所有路由 / 跑自测
python3 router.py --list
python3 router.py --test
```

## Dependencies
- `routes.yaml`（路由规则表，本目录）
- `sera-agent-orchestrator`（执行编排链的协调者）
- 5 个核心 Agent（propfirm/otc/trading/video/design）

## Iron Rules
- 优先级从上到下：compute（serawin 强信号）> video > multi-agent > 领域 > 兜底
- 未匹配一律 fallback 到 orchestrator，不静默丢弃
- 规则可扩展：新增意图只需在 routes.yaml 加一条
