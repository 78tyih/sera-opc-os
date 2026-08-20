---
name: sera-agent-orchestrator
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

# sera-agent-orchestrator

## Purpose
Sera Agent OS 的编排器：把用户请求路由到正确的 Agent + Skill 组合，规划执行步骤，检测冲突。是系统的大脑入口。

## When to use
- 用户请求涉及多个 Skill 的复合任务（如「做一条 PropFirm.TV 视频」需要 PM → content-factory → video-pipeline → compute → knowledge-sync 五步链路）
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
1. 解析用户意图 → 识别目标域（business/creative/core）
2. 查 Skill Registry → 匹配候选 Skill 链
3. 检查依赖顺序（如 compute 在 video-pipeline 之前）
4. 输出执行计划：skill 链 + 各环节 I/O 契约
5. 执行中监控冲突 → 需要时回退重排
```

示例路由 —— 「Create PropFirm TV video」：
```
1. sera-propfirm-product-manager（产品/内容决策）
2. sera-content-factory（官网素材）
3. sera-video-pipeline（数字人视频合成）
4. sera-compute-control（serawin 远程渲染）
5. sera-knowledge-sync（产物归档 Obsidian）
```

## Dependencies
- `sera-skill-registry`（技能清单）
- 各域 Skill（core/business/creative/adapters）

## Examples
- 「做一条 PropFirm.TV 视频」→ 路由 5 步链
- 「帮我分析今天的 PropFirm 情报」→ `sera-intelligence-monitor`
- 「把刚才的报告归档」→ `sera-knowledge-sync`
