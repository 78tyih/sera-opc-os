# Sera Control Center — Backend Mock API

> 模拟数据端点，用于前端开发

## API 端点

| 端点 | 方法 | 返回 | 数据源 |
|------|------|------|--------|
| `/api/dashboard/stats` | GET | 统计概览 | registry/agents.json + portfolio/registry/projects.json |
| `/api/projects` | GET | 项目列表 | portfolio/projects/*/PROJECT_PROFILE.md |
| `/api/projects/:id` | GET | 项目详情 | portfolio/projects/:id/ |
| `/api/agents` | GET | Agent 列表 | registry/agents.json |
| `/api/agents/:id` | GET | Agent 详情 | agents/:id/agent.yaml |
| `/api/workflows` | GET | 工作流列表 | core/sera-agent-router/workflows/ |
| `/api/workflows/:id` | GET | 工作流详情 | core/sera-agent-router/workflows/:id |
| `/api/portfolio/stats` | GET | 项目组合统计 | portfolio/analytics/ |

## 数据映射

前端从 registry/ 和 portfolio/ 读取数据，通过 Mock API 转换为前端需要的格式。

## 集成方式

```typescript
// 前端数据获取示例
const API_BASE = '/api';

async function getDashboardStats() {
  const res = await fetch(`${API_BASE}/dashboard/stats`);
  return res.json();
}

async function getProjects() {
  const res = await fetch(`${API_BASE}/projects`);
  return res.json();
}
```