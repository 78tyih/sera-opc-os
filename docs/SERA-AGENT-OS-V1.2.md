# Sera Agent OS V1.2

> Executive Layer + Project Portfolio + Control Center MVP
> 生成时间：2026-08-21

---

## 1. 整体架构

```
                    Sera Agent OS V1.2
                    ─────────────────
                           │
                    Executive Layer
                    sera-ceo-agent
                    ─────────────────
                           │
              ┌────────────┼────────────┐
              │            │            │
         Product      Design      Content
         Agent        Agent        Agent
              │            │            │
              └────────────┼────────────┘
                           │
                    Product Factory
                    ─────────────────
                    Project Portfolio
                    ─────────────────
                    Control Center
                    ─────────────────
                    Model Router
                    ─────────────────
                    Memory / State
```

## 2. 层级说明

| 层级 | 组件 | 职责 |
|------|------|------|
| **Executive** | sera-ceo-agent | 商业决策、资源分配、优先级管理 |
| **Agent** | 7 个 Agent | 领域执行（产品/设计/视频/PropFirm/OTC/交易） |
| **Factory** | Product Factory | 产品从想法到发布的完整流水线 |
| **Portfolio** | portfolio/ | 项目组合管理、资产追踪 |
| **Control Center** | control-center/ | WebUI 可视化操作台 |
| **Router** | model-router/ | 模型路由与 AI 团队分配 |

## 3. Agent 组织结构

```
Sera Agent OS
    │
    ├── Executive
    │   └── sera-ceo-agent          ← 新增
    │
    ├── Product Department
    │   └── product-agent           ← 新增
    │
    ├── Design Department
    │   ├── design-agent
    │   ├── design-research-agent
    │   ├── design-extraction-agent
    │   ├── design-generator-agent
    │   ├── design-system-agent
    │   ├── design-review-agent
    │   └── asset-manager-agent
    │
    ├── Content Department
    │   └── video-agent
    │
    ├── Business Department
    │   ├── propfirm-agent
    │   ├── otc-agent
    │   └── trading-agent
    │
    └── Core Infrastructure
        ├── sera-agent-orchestrator
        ├── sera-agent-router
        ├── sera-agent-registry
        ├── sera-memory-system
        ├── sera-state-manager
        ├── sera-skill-registry
        ├── sera-context-system
        ├── sera-knowledge-sync
        └── sera-compute-control
```

## 4. Project Portfolio

```
portfolio/
├── README.md                   组合管理总览
├── templates/                  项目模板
│   ├── PROJECT_PROFILE.md      项目档案模板
│   └── PROJECT_DECISION.md     决策文档模板
├── projects/                   项目目录
│   ├── niuniu-ai/              牛牛 AI
│   │   ├── PROJECT_PROFILE.md
│   │   ├── assets.yaml
│   │   └── agent-plan.yaml
│   ├── tradespan/              TradeSpan
│   │   ├── PROJECT_PROFILE.md
│   │   ├── assets.yaml
│   │   └── agent-plan.yaml
│   ├── propfirm-tv/            PropFirm TV
│   │   ├── PROJECT_PROFILE.md
│   │   ├── assets.yaml
│   │   └── agent-plan.yaml
│   ├── htx-otc/                HTX OTC
│   │   ├── PROJECT_PROFILE.md
│   │   ├── assets.yaml
│   │   └── agent-plan.yaml
│   └── deltapex/               Deltapex / 德湃
│       ├── PROJECT_PROFILE.md
│       ├── assets.yaml
│       └── agent-plan.yaml
├── registry/                   项目注册表
├── archive/                    已归档项目
└── analytics/                  项目分析
```

## 5. Control Center

```
control-center/
├── README.md               总览
├── schemas/                数据 Schema
│   ├── dashboard.json
│   ├── workflow-node.json
│   ├── agent-monitor.json
│   └── project-view.json
├── backend/                Mock API
└── frontend/               前端项目链接

前端：~/sera-agent-console (Next.js, http://localhost:3000)
页面：/dashboard, /projects, /agents, /workflows, /department
```

## 6. 完整工作流

```
User Idea
    │
    ▼
[CEO Agent] — 商业评估（6 维度）
    │
    ├── GO ──→ [Product Factory]
    │              │
    │              ├── Product Agent (7 steps)
    │              ├── Design Agent (brand + visual)
    │              ├── Video Agent (script + storyboard)
    │              └── Knowledge Sync (memory + context)
    │
    ├── HOLD ──→ 记录条件，等待触发
    │
    └── STOP ──→ 记录原因，归档

    ▼
[Project Portfolio] — 资产 + 状态更新
    ▼
[Control Center] — 可视化
```

## 7. 文件清单

### 新增文件

| 文件 | 说明 |
|------|------|
| `agents/executive/sera-ceo-agent/agent.yaml` | CEO Agent 配置 |
| `agents/executive/sera-ceo-agent/system.md` | CEO Agent 系统提示 |
| `agents/executive/sera-ceo-agent/SKILL.md` | CEO Agent Skill 描述 |
| `agents/executive/sera-ceo-agent/memory-policy.yaml` | 记忆策略 |
| `agents/executive/sera-ceo-agent/skill-map.yaml` | Skill 映射 |
| `agents/executive/sera-ceo-agent/evaluation.yaml` | 评估体系 |
| `agents/executive/sera-ceo-agent/decision-framework.md` | 决策框架 |
| `agents/executive/sera-ceo-agent/priority-engine.md` | 优先级引擎 |
| `portfolio/README.md` | 组合管理总览 |
| `portfolio/templates/PROJECT_PROFILE.md` | 项目档案模板 |
| `portfolio/templates/PROJECT_DECISION.md` | 决策文档模板 |
| `portfolio/analytics/README.md` | 分析报告 |
| `portfolio/projects/niuniu-ai/PROJECT_PROFILE.md` | 牛牛 AI 项目档案 |
| `portfolio/projects/niuniu-ai/assets.yaml` | 牛牛 AI 资产注册 |
| `portfolio/projects/niuniu-ai/agent-plan.yaml` | 牛牛 AI Agent 计划 |
| `portfolio/projects/tradespan/PROJECT_PROFILE.md` | TradeSpan 项目档案 |
| `portfolio/projects/tradespan/assets.yaml` | TradeSpan 资产注册 |
| `portfolio/projects/tradespan/agent-plan.yaml` | TradeSpan Agent 计划 |
| `portfolio/projects/propfirm-tv/PROJECT_PROFILE.md` | PropFirm TV 项目档案 |
| `portfolio/projects/propfirm-tv/assets.yaml` | PropFirm TV 资产注册 |
| `portfolio/projects/propfirm-tv/agent-plan.yaml` | PropFirm TV Agent 计划 |
| `portfolio/projects/htx-otc/PROJECT_PROFILE.md` | HTX OTC 项目档案 |
| `portfolio/projects/htx-otc/assets.yaml` | HTX OTC 资产注册 |
| `portfolio/projects/htx-otc/agent-plan.yaml` | HTX OTC Agent 计划 |
| `portfolio/projects/deltapex/PROJECT_PROFILE.md` | Deltapex 项目档案 |
| `portfolio/projects/deltapex/assets.yaml` | Deltapex 资产注册 |
| `portfolio/projects/deltapex/agent-plan.yaml` | Deltapex Agent 计划 |
| `control-center/README.md` | 控制中心总览 |
| `control-center/schemas/dashboard.json` | Dashboard Schema |
| `control-center/schemas/workflow-node.json` | Workflow Node Schema |
| `control-center/schemas/agent-monitor.json` | Agent Monitor Schema |
| `control-center/schemas/project-view.json` | Project View Schema |
| `control-center/backend/README.md` | Mock API 文档 |
| `model-router/routing-policy.yaml` | 模型路由策略 |
| `core/sera-agent-router/workflows/company-product-launch.yaml` | 完整产品发布工作流 |

### 更新文件

| 文件 | 变更 |
|------|------|
| `core/sera-agent-router/routes.yaml` | 新增 CEO 路由 + 完整发布流水线 |
| `core/sera-agent-router/router.py` | 新增内置 CEO 路由 + 14/14 测试 |

## 8. 新增统计

| 维度 | 数量 |
|------|------|
| 新增 Agent | 1 (sera-ceo-agent) |
| 新增文件 | 35 |
| 新增工作流 | 1 (company-product-launch) |
| 更新路由 | 2 (ceo-decision, company-product-launch) |
| 新增项目 | 5 (niuniu-ai, tradespan, propfirm-tv, htx-otc, deltapex) |
| 项目文件 | 15 (5 × 3 文件) |
| 测试通过 | 14/14 |

## 9. 下一阶段建议

### 短期（V1.3）
1. **Growth Agent 建立** — SEO + 社媒 + 社区运营
2. **Control Center 完整集成** — 连接 portfolio/registry/ 数据到前端
3. **Evaluation 实际运行** — 按 evaluation.yaml 维度打分

### 中期（V2.0）
1. **Skill 生命周期管理** — active/deprecated/archived 状态
2. **Agent 改名** — propfirm→business, video→content, design→director
3. **Git submodule 集成** — kimi-design-refer, htx-design-refer, video-factory

### 长期
1. **多模型对比** — 同一 Agent 用不同模型跑，记录到 evaluation/
2. **自动化测试** — 每个 Agent 的完整 E2E 测试
3. **社区版** — 开源 Sera Agent OS 核心