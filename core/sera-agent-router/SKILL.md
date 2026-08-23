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
Sera OPC OS 的 **Agent Router**：把用户自然语言请求自动解析为 Agent/Skill 编排链。输入一句话，输出「该用哪个 Agent、按什么顺序调用哪些 Skill」的执行计划。是 Agent Orchestrator 的规则引擎。

## When to use
- 任何进入 Sera OPC OS 的用户请求（编排器入口）
- 需要把任务自动路由到核心 Agent / Skill
- 复合任务需要多 Agent 编排
- 目标、Scope 或关键取舍尚未清楚时，优先路由到 `sera-grill`

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
4. 显式 Grill / 模糊需求 / 新架构 / 复杂技术选型 → sera-grill
5. 其他命中 → 输出领域编排链；未命中 → fallback 到 orchestrator
6. 编排器按 pipeline 依序调用各 Agent/Skill
7. 完成后执行 finalize（归档/更新状态）
```

## Tools
- Bash：`python3 router.py "<用户请求>"`（规则引擎，纯 stdlib）
- 配置：`routes.yaml`（路由规则，可扩展）

## 路由规则（routes.yaml）
| route | intent | agent | pipeline |
|---|---|---|---|
| `compute` | 远程算力 | core | sera-compute-control |
| `grill-clarify` | 目标/范围/决策澄清 | core | sera-grill |
| `company-product-launch` | 完整产品发布 | multi | sera-grill → CEO → Product Factory |
| `video-produce` | 视频/素材生产 | video-agent | content-factory → video-pipeline → asset-manager → compute-control |
| `propfirm-intel` | PropFirm 情报/竞品 | propfirm-agent | intelligence-monitor → browser-automation → content-factory |
| `product-init` | 产品发布/项目初始化 | product-agent | sera-grill → project-profile → market-research → ... |
| `product-factory-pipeline` | 完整产品发布流水线 | multi | sera-grill → product → design → video → review |
| `design-produce` | 设计/品牌/UI/海报 | design-agent | design-studio → figma-review |
| `trading-research` | 交易研究/复盘 | trading-agent | trading-analysis → finance-suite → knowledge-reader |
| `otc-bd` | OTC 商务/客户 | otc-agent | crm-adapter → mail-hub → memory-system |
| `knowledge-ops` | 知识/记忆/归档 | core | context-system → state-manager → knowledge-sync |
| `fallback` | 未匹配 | orchestrator | sera-agent-orchestrator（人工/LLM 判定） |

## sera-grill Preflight

`sera-grill` 是条件前置 Skill，不是所有任务的强制问答层。

优先触发：
- `grill me` / `SERA_GRILL` / `盘问我` / `帮我想清楚`
- 新架构、复杂工作流、重要技术选型
- 用户说“我想做一个……”但目标 / Scope 尚未清楚

默认跳过：
- 简单查询、翻译、单个明确修改
- 已有清晰 Spec 的执行任务
- 不存在会改变下一步执行方式的未决问题

Grill 完成后输出 Shared Understanding，再交回 Router 进入正常执行链。

## Examples
```bash
# 显式进入 Grill
python3 router.py "grill me，先帮我把需求想清楚"
# → core: [sera-grill]

# 新项目：产品流水线先过 Grill preflight
python3 router.py "启动项目，做一个新的内部工具"
# → product-agent: [sera-grill, sera-project-profile, ...]

# 普通明确任务不被 Grill 拦截
python3 router.py "做一条 PropFirm.TV 视频"
# → video-agent: [sera-content-factory, sera-video-pipeline, ...]

# 列出所有路由 / 跑自测
python3 router.py --list
python3 router.py --test
```

## Dependencies
- `routes.yaml`（路由规则表，本目录）
- `sera-agent-orchestrator`（执行编排链的协调者）
- `sera-grill`（目标/范围/决策澄清）
- 各领域 Agent / Skill

## Iron Rules
- 优先级从上到下：compute 强信号 > grill 澄清 > CEO/产品/领域 > 兜底
- `sera-grill` 只在会减少返工时触发，不允许所有任务默认盘问
- 未匹配一律 fallback 到 orchestrator，不静默丢弃
- 规则可扩展：新增意图优先在 routes.yaml 加规则，并同步 stdlib builtin fallback
