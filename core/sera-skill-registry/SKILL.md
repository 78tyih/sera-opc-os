---
name: sera-skill-registry
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

# sera-skill-registry

## Purpose
Sera OPC OS 的 Skill 注册表：管理所有能力（core / business / creative / adapters），统一 Skill 标准格式（name · purpose · inputs · outputs · workflow · dependencies · examples · version），供各 Agent 发现与加载。

## When to use
- 新 Agent（WorkBuddy/Codex/Trae/Claude）接入时需要注册表索引
- 编排器需要查询可用 Skill 清单
- 新增 / 更新 Skill 时遵循标准格式
- Learning OS 需要定位 Skill baseline / candidate / portability / version

## Inputs
- Skill 清单查询（按类别/关键词）
- 新 Skill 定义（符合 SKILL.md 标准）
- Skill evolution proposal / evaluation result

## Outputs
- Skill Registry 索引（类别分组清单）
- 每个 Skill 的标准 SKILL.md（可被任何兼容 Agent 加载）
- Learning OS 可引用的 canonical Skill path / version

## Workflow
```
1. 启动/接入时：扫描仓库结构 → 建立注册索引
2. 查询：按 core/business/creative/adapters 分类列出
3. 加载：读取目标 SKILL.md → 解析 frontmatter + 正文
4. 更新：新增/修改 Skill 时按 templates/SKILL.template.md 标准
5. 演化：Learning OS 只能提交 Proposal；Evaluation + Authority Gate 通过后才更新 production Skill
```

## 当前注册表（V1.2）
### core/
- `sera-agent-orchestrator` — 任务路由/执行规划（引擎=router）
- `sera-agent-router` — **Agent Router 三层规划**（Intent→Agent→Execution）
- `sera-agent-registry` — **Agent 注册表**（Agent Contract 登记/查询）
- `sera-memory-system` — 共享记忆层（Context Hub + Obsidian + Project State）
- `sera-learning-os` — **经验→Persistent Wiki→Skill Proposal→Evaluation→Release/Rollback 的学习闭环**
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

### workflows/（预设编排工作流）
- `propfirm-video.yaml`（video-agent 端到端）
- `product-launch-page.yaml`（多 Agent 发布页）

## Learning OS Integration

Skill Registry 与 Learning OS 的边界：

```text
Skill Registry = 生产 Skill 的发现、版本、兼容性入口
Learning OS    = 经验、Wiki Pattern、Proposal、Evaluation、Skill impact history
```

Learning OS 不得静默修改 Registry 或 production Skill。

Proposal 必须记录 portability：

- `universal`
- `model_family`
- `model_specific`
- `agent_shell_specific`
- `tool_environment_specific`

## Dependencies
- `templates/SKILL.template.md`（标准格式模板）
- `templates/workflow.yaml`（工作流模板）
- `core/sera-learning-os/SKILL.md`
- `core/sera_learning_os/learning.py`

## Examples
- 「这个仓库有哪些 Skill」→ 输出注册表索引
- 「装个新 Skill」→ 按 templates/SKILL.template.md 生成
- 「Codex 接入」→ 读 README 安装方式 + 本注册表
- 「这个 Skill 为什么要改」→ 查 Learning OS Pattern + Skill impact + Evaluation evidence
