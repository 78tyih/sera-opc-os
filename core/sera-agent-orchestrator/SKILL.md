---
name: sera-agent-orchestrator
version: 1.1.0
author: Sera
category: core
compatible:
  - WorkBuddy
  - Codex
  - Trae
  - Claude-Code
status: active
---

# sera-agent-orchestrator

## Purpose
Sera OPC OS 的编排器：把用户请求路由到正确的 Agent + Skill 组合，规划执行步骤，检测冲突。是系统的大脑入口。**核心引擎 = `sera-agent-router`（规则引擎），本 Skill 负责执行编排链的协调**。

## When to use
- 用户请求涉及多个 Skill 的复合任务（如「做一条 PropFirm.TV 视频」需要 content-factory → video-pipeline → compute → knowledge-sync 链路）
- 需要选择用哪个 Agent / 哪个 Skill 完成任务的场景
- 需要检查多 Skill 组合的冲突或依赖顺序

## Inputs
- 用户任务描述（自然语言）
- 可用 Skill Registry 清单（core / business / creative / adapters）

## Outputs
- 任务路由计划：`[skill1 → skill2 → ...]` 有序执行链
- 每个环节的输入/输出契约
- 冲突检测结果与调整建议

## Workflow
```
1. 接收用户请求 → 调 sera-agent-router（python3 router.py "<请求>"）拿到编排链
2. 校验编排链：确认各 Skill 存在、依赖顺序正确（如 compute 在 video-pipeline 之后）
3. 依序执行：每步把上步输出作为下步输入（Agent:Skill 语法 = 指定由哪个 Agent 执行）
4. 执行中监控冲突/失败 → 需要时回退重排
5. 完成后执行 finalize（sera-knowledge-sync 归档）
6. 更新 sera-state-manager（阶段/下一步）
```

示例路由 —— 「Create PropFirm TV video」（由 router 自动生成）：
```
1. sera-content-factory（官网素材 5s B-roll）
2. sera-video-pipeline（数字人视频合成）
3. sera-asset-manager（Eagle 入库）
4. sera-compute-control（serawin 远程渲染，可选）
5. finalize: sera-knowledge-sync（归档 Obsidian）
```

## Dependencies
- `sera-agent-router`（规则引擎，编排链来源）—— **核心依赖**
- `sera-skill-registry`（技能清单）
- 5 个核心 Agent（propfirm/otc/trading/video/design）
- 各域 Skill（core/business/creative/adapters）

## Examples
- 「做一条 PropFirm.TV 视频」→ router 输出 video-agent 链 → 依序执行
- 「帮我做 TradeSpan 产品发布页」→ router 输出 multi 链（propfirm→design→video→figma-review）
- 「帮我分析今天的 PropFirm 情报」→ propfirm-intel 链
- 「把刚才的报告归档」→ knowledge-ops 链
