# Sera Control Center MVP

> **⚠️ 开发冻结（2026-08-21 ~ 2026-08-28）**
>
> 根据 Kimi K3 审计建议，Control Center 前端开发暂时冻结。
> 等待 Kernel V0 提供真实数据后再恢复开发，避免在 mock 数据基础上构建虚假界面。
>
> 当前状态：静态原型已完成（玻璃拟态 Design Lab + SMOP 数据桥 + Context Runtime 页面）。
> 冻结期间可进行代码审查和学习，不新增页面或功能。
> 解冻条件：Kernel V0 验收通过，SQLite 三表含有真实 TradeSpan 数据。

> 版本：1.2.0
> Sera OPC OS 控制中心 — 可视化操作台

---

## 架构

```
control-center/
├── schemas/          # 数据 Schema 定义（JSON Schema）
├── backend/          # Mock API 端点
├── components/       # UI 组件说明
└── frontend/         # 前端项目链接
```

## 前端项目

前端实现在独立仓库：
**`~/sera-agent-console`**（`http://localhost:3000`）

技术栈：Next.js 15 + TypeScript + Tailwind CSS + React Flow + Framer Motion

## 页面路由

| 路由 | 页面 | 数据源 |
|------|------|--------|
| `/dashboard` | 首页概览 | registry/agents.json + portfolio/registry/projects.json |
| `/projects` | 项目管理 | portfolio/projects/*/PROJECT_PROFILE.md |
| `/agents` | Agent Registry | registry/agents.json |
| `/workflows` | 工作流画布 | core/sera-agent-router/workflows/ |
| `/department` | 组织架构 | agents/*/agent.yaml |

## 数据流

```
registry/*.json
    ↓
control-center/backend/  (Mock API)
    ↓
control-center/frontend/ (Next.js)
    ↓
用户浏览器
```

## 启动方式

```bash
cd ~/sera-agent-console
npm run dev
# 访问 http://localhost:3000
```