# Sera OPC OS — Control Center V0.1

> **Sera OPC OS 的控制中心 WebUI 原型。**
> AI 公司操作台 + Agent 调度中心 + Workflow 编排系统。

## 技术栈

| 层面 | 技术 |
|------|------|
| 框架 | Next.js 15 (App Router) |
| 语言 | TypeScript |
| 样式 | Tailwind CSS |
| 图标 | Lucide React |
| 动画 | Framer Motion |
| 工作流画布 | React Flow (@xyflow/react v12) |

## 页面结构

| 路由 | 页面 | 内容 |
|------|------|------|
| `/dashboard` | **Dashboard** | 项目/Agent/Workflow 概览 + 活动时间线 |
| `/projects` | **Projects** | 项目组合管理，按类别/状态筛选 |
| `/agents` | **Agents** | Agent Registry，6 部门 × 13 Agent |
| `/workflows` | **Workflows** | React Flow 可视化工作流编排画布 |
| `/department` | **Department** | 公司组织架构，部门/团队/项目视图 |

## 设计风格

- **深色模式优先**：背景 `#0B0F19`，参考 Linear / Vercel / OpenAI
- **科技蓝 + 紫色渐变**：品牌色 `#3B82F6` + `#8B5CF6`
- **简洁、高级、未来感**：避免普通后台系统风格
- 自定义滚动条、发光效果、毛玻璃面板

## 数据结构

所有数据基于 Mock JSON，位于 `src/data/`：

- `projects.json` — 6 个示例项目（PropFirm TV, Niuniu AI, TradeSpan, Sera OPC OS, Content Factory, OTC CRM）
- `agents.json` — 13 个 Agent，分属 6 个部门
- `departments.json` — 部门定义（Product/Design/Marketing/Content/Engineering/Business）
- `workflows.json` — 3 个工作流模板（Product Launch Pipeline, Daily Intelligence Brief, Video Production Pipeline）

## 未来集成

V0.1 是纯视觉原型。未来可以连接：

- **Sera Agent Router** — `~sera-agent-os/core/sera-agent-router/router.py` 替换规则路由
- **Skill Registry** — `sera-skill-registry` 动态加载 Skill 列表
- **Project Portfolio** — `sera-state-manager` 读取项目/任务状态
- **Agent Evaluation** — `evaluation/agent-score.yaml` 展示评估分数

## 快速开始

```bash
cd ~/sera-agent-console
npm run dev
# 浏览器打开 http://localhost:3000
```

## 构建

```bash
npm run build
npm start
```