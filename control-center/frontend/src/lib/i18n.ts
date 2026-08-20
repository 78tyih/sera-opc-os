const dict: Record<string, { zh: string; en: string }> = {
  // Navigation
  "nav.dashboard": { zh: "控制台", en: "Dashboard" },
  "nav.projects": { zh: "项目", en: "Projects" },
  "nav.agents": { zh: "智能体", en: "Agents" },
  "nav.workflows": { zh: "工作流", en: "Workflows" },
  "nav.department": { zh: "组织", en: "Department" },
  "nav.all-operational": { zh: "系统正常", en: "All operational" },
  "nav.search": { zh: "搜索...", en: "Search..." },

  // Dashboard
  "dashboard.title": { zh: "控制台", en: "Dashboard" },
  "dashboard.subtitle": { zh: "控制中心概览", en: "Control Center" },
  "dashboard.active-projects": { zh: "活跃项目", en: "Active Projects" },
  "dashboard.running-agents": { zh: "运行中", en: "Running" },
  "dashboard.today-output": { zh: "今日产出", en: "Today" },
  "dashboard.system-uptime": { zh: "系统运行", en: "Uptime" },
  "dashboard.active-agents": { zh: "活跃智能体", en: "Active Agents" },
  "dashboard.running-workflows": { zh: "运行中工作流", en: "Running Workflows" },
  "dashboard.activity": { zh: "动态", en: "Activity" },
  "dashboard.view-all": { zh: "查看全部", en: "View all" },

  // Projects
  "projects.title": { zh: "项目", en: "Projects" },
  "projects.new": { zh: "新建项目", en: "New Project" },
  "projects.no-match": { zh: "暂无匹配项目", en: "No matching projects" },

  // Agents
  "agents.title": { zh: "智能体", en: "Agents" },
  "agents.subtitle": { zh: "部门化 AI 团队", en: "Departmental Agent Team" },
  "agents.active": { zh: "活跃", en: "Active" },
  "agents.idle": { zh: "闲置", en: "Idle" },

  // Workflows
  "workflows.title": { zh: "工作流", en: "Workflows" },
  "workflows.subtitle": { zh: "工作流编排", en: "Workflow Orchestration" },
  "workflows.run": { zh: "运行", en: "Run" },
  "workflows.pause": { zh: "暂停", en: "Pause" },
  "workflows.last-run": { zh: "上次运行", en: "Last run" },
  "workflows.completed": { zh: "已完成", en: "Completed" },
  "workflows.running": { zh: "运行中", en: "Running" },
  "workflows.pending": { zh: "待处理", en: "Pending" },

  // Department
  "department.title": { zh: "组织架构", en: "Department" },
  "department.subtitle": { zh: "组织结构", en: "Organizational Structure" },
  "department.team-members": { zh: "团队成员", en: "Team Members" },
  "department.active-projects": { zh: "活跃项目", en: "Active Projects" },
  "department.ceo": { zh: "首席执行官", en: "CEO" },

  // Status
  "status.active": { zh: "活跃", en: "Active" },
  "status.idle": { zh: "闲置", en: "Idle" },
  "status.running": { zh: "运行中", en: "Running" },
  "status.pending": { zh: "待处理", en: "Pending" },
  "status.completed": { zh: "已完成", en: "Completed" },
  "status.planning": { zh: "规划中", en: "Planning" },

  // Categories
  "cat.all": { zh: "全部", en: "All" },
  "cat.product": { zh: "产品", en: "Product" },
  "cat.content": { zh: "内容", en: "Content" },
  "cat.infrastructure": { zh: "基础设施", en: "Infrastructure" },
  "cat.business": { zh: "商务", en: "Business" },

  // Departments
  "dept.product": { zh: "产品部", en: "Product" },
  "dept.design": { zh: "设计部", en: "Design" },
  "dept.marketing": { zh: "市场部", en: "Marketing" },
  "dept.content": { zh: "内容部", en: "Content" },
  "dept.engineering": { zh: "工程部", en: "Engineering" },
  "dept.business": { zh: "商务部", en: "Business" },

  // Misc
  "misc.agents": { zh: "个智能体", en: " agents" },
  "misc.projects": { zh: "个项目", en: " projects" },
}

export function t(key: string, lang: "zh" | "en"): string {
  return dict[key]?.[lang] ?? key
}

export function tz(key: string): { zh: string; en: string } {
  return dict[key] ?? { zh: key, en: key }
}