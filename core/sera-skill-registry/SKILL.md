---
name: sera-skill-registry
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

# sera-skill-registry

## Purpose
Sera Agent OS 的 Skill 注册表：管理所有能力（core / business / creative / adapters），统一 Skill 标准格式（name · purpose · inputs · outputs · workflow · dependencies · examples · version），供各 Agent 发现与加载。

## When to use
- 新 Agent（WorkBuddy/Codex/Trae/Claude）接入时需要注册表索引
- 编排器需要查询可用 Skill 清单
- 新增 / 更新 Skill 时遵循标准格式

## Inputs
- Skill 清单查询（按类别/关键词）
- 新 Skill 定义（符合 SKILL.md 标准）

## Outputs
- Skill Registry 索引（类别分组清单）
- 每个 Skill 的标准 SKILL.md（可被任何兼容 Agent 加载）

## Workflow
```
1. 启动/接入时：扫描仓库结构 → 建立注册索引
2. 查询：按 core/business/creative/adapters 分类列出
3. 加载：读取目标 SKILL.md → 解析 frontmatter + 正文
4. 更新：新增/修改 Skill 时按 templates/SKILL.template.md 标准
```

## 当前注册表（V1.1，22 个超级 Skill）
### core/
- `sera-agent-orchestrator` — 任务路由/执行规划
- `sera-memory-system` — 共享记忆层（Context Hub + Obsidian + Project State）
- `sera-state-manager` — 工作状态管理（当前阶段/阻塞/下一步）
- `sera-skill-registry` — 本注册表
- `sera-context-system` — 多 Agent 共享上下文（原 context-hub）
- `sera-knowledge-sync` — Obsidian 知识归档（原 obsidian-sync）
- `sera-compute-control` — 远程算力控制（原 serawin-remote）

### business/
- `sera-intelligence-monitor` — PropFirm 商业情报（原 propfirm-feed）
- `sera-content-factory` — 官网素材工厂（原 propfirm-official-site-assets）
- `trading-analysis` — 交易复盘/胜率盈亏比/策略回测/订单流解读

### creative/
- `sera-video-pipeline` — 数字人视频流水线（原 heygen-knowledge-shortvideo）
- `sera-asset-manager` — 素材资产管理（原 propfirm-eagle-import）
- `sera-design-studio` — 前端设计开发规范（原 frontend-dev）
- `figma-review` — 设计稿审查（视觉层级/品牌一致性/可交付性）

### adapters/
- `sera-lark-suite` — 飞书/Lark（原 lark-unified）
- `sera-wecom-suite` — 企业微信（原 wecom-unified）
- `sera-mail-hub` — 邮件（原 gmail）
- `sera-browser-automation` — 浏览器（原 browser-use）
- `sera-macos-ui` — macOS UI（原 peekaboo）
- `sera-crm-adapter` — CRM 适配层（客户档案/跟进/交易记录）

### agents/（5 个核心 Agent，全部 active）
- `propfirm-agent` / `otc-agent` / `trading-agent` / `video-agent` / `design-agent`

## Dependencies
- `templates/SKILL.template.md`（标准格式模板）
- `templates/workflow.yaml`（工作流模板）

## Examples
- 「这个仓库有哪些 Skill」→ 输出注册表索引
- 「装个新 Skill」→ 按 templates/SKILL.template.md 生成
- 「Codex 接入」→ 读 README 安装方式 + 本注册表
