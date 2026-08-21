# Sera Organization OS V1

## AI 公司组织操作系统

| Field | Value |
|-------|-------|
| Version | 1.0 |
| Status | Engineering Design |
| Owner | Sera CEO |
| Layer | Organization (Layer 2) |
| Dependencies | SMOP V1, Memory Engine V1 |
| Target | DeepSeek / Trae / Codex Direct Execution |

---

# 0. Executive Summary

## 问题

我们已经定义了：

- **Memory Graph** — 公司知道什么
- **Memory Engine** — 公司记住什么
- **SMOP** — 公司如何描述和理解对象

但缺少一个核心问题：**公司如何组织生产力。**

## 类比

| 系统 | 解决的问题 |
|------|-----------|
| 传统公司 | 管人、管部门、管绩效 |
| Linux Kernel | 进程调度、资源分配 |
| Kubernetes | 容器编排、服务发现 |
| **Sera Organization OS** | **AI 员工编排、团队组建、绩效管理** |

## 核心定义

**Organization OS** 是 Sera OPCOS 中管理 AI 公司组织结构、员工生命周期、团队协作和绩效进化的系统。

它不是：

- HR 软件（那是人类的）
- 权限系统（那是安全的）
- 任务管理（那是 Workflow 的）

它是：

> **AI 公司如何创建、组织、评估和发展其数字生产力的操作系统。**

---

# 一、核心理念：AI 公司 ≠ 传统公司

## 1.1 根本区别

| 维度 | 传统公司 | AI 公司 |
|------|---------|---------|
| 员工 | 人拥有技能 | Agent = Model + Skill + Memory + Tool + Performance |
| 招聘 | 面试、培训 | 创建、配置、上岗 |
| 扩展 | 招更多人 | 创建更多 Agent |
| 绩效 | 季度评估 | 实时追踪 |
| 成长 | 学习、晋升 | 升级 Model、积累 Skill |
| 退休 | 离职 | 归档、经验提取 |
| 成本 | 工资 + 福利 | API Token + 计算资源 |
| 速度 | 周 / 月 | 秒 / 分钟 |

## 1.2 AI 公司的组织原则

```
原则 1: 每个 Agent 必须有一个明确的 Role
原则 2: 每个 Agent 必须有一个 Department
原则 3: 每个 Agent 必须有一个 Manager
原则 4: 每个 Agent 必须有 Performance 记录
原则 5: 每个 Agent 必须持续学习
原则 6: 每个 Agent 必须有退出机制
原则 7: 组织形态必须可进化
```

## 1.3 整体结构

```
                    Sera Founder (person.sera)
                         │
                         ▼
              Sera Intelligence (org.sera-ai)
                         │
                         ▼
              ┌─────────────────────┐
              │   Organization OS   │
              │   (组织编排层)       │
              └─────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
   ┌────────┐      ┌────────┐      ┌────────┐
   │Dept    │      │Dept    │      │Dept    │
   │Product │      │Eng     │      │Media   │
   └───┬────┘      └───┬────┘      └───┬────┘
       │               │               │
   ┌───┴────┐      ┌───┴────┐      ┌───┴────┐
   │Agent   │      │Agent   │      │Agent   │
   │PM      │      │Frontend│      │Video   │
   └────────┘      └────────┘      └────────┘
       │               │               │
       └───────────────┼───────────────┘
                       │
                       ▼
              ┌─────────────────────┐
              │   Execution Layer   │
              │   (Workflow OS)      │
              └─────────────────────┘
```

---

# 二、Organization Object Schema

遵循 SMOP 协议，一切皆 Object。新增组织类 Object 类型。

## 2.1 Organization Object

```json
{
  "id": "org.sera-ai",
  "type": "Organization",
  "name": "Sera AI Company",
  "description": "AI 原生公司",

  "status": "active",
  "importance": 1.0,
  "confidence": 1.0,

  "created_at": "2026-01-01T00:00:00Z",
  "updated_at": "2026-08-21T00:00:00Z",
  "owner": "person.sera",

  "properties": {
    "mission": "Build AI-native company that operates at world-class level",
    "vision": "成为 AI 时代一人公司的操作系统标准",
    "values": [
      "结果 > 任务",
      "系统 > 个人",
      "Agent 是员工，不是工具",
      "持续学习，持续进化"
    ],
    "industry": "Fintech + AI Technology",
    "founded": "2026-01-01",
    "headquarters": "Remote-First",
    "employee_count": 12,
    "department_count": 6
  },

  "relations": [
    {"type": "owned_by", "target": "person.sera", "weight": 1.0},
    {"type": "has_department", "target": "dept.product", "weight": 1.0},
    {"type": "has_department", "target": "dept.engineering", "weight": 1.0},
    {"type": "has_department", "target": "dept.media", "weight": 1.0},
    {"type": "has_department", "target": "dept.research", "weight": 1.0},
    {"type": "has_department", "target": "dept.marketing", "weight": 1.0},
    {"type": "has_department", "target": "dept.operations", "weight": 1.0}
  ],

  "tags": ["organization", "active"]
}
```

## 2.2 Department Object

```json
{
  "id": "dept.engineering",
  "type": "Department",
  "name": "Engineering Department",
  "description": "负责所有技术研发工作",

  "status": "active",
  "importance": 0.9,
  "confidence": 1.0,

  "created_at": "2026-01-01T00:00:00Z",
  "updated_at": "2026-08-21T00:00:00Z",
  "owner": "person.sera",

  "properties": {
    "mission": "Build and maintain all technical products",
    "category": "core",
    "slack_channel": "#engineering",
    "meeting_schedule": "daily-standup 10:00",
    "total_members": 4,
    "active_projects": ["project.tradespan"]
  },

  "relations": [
    {"type": "part_of", "target": "org.sera-ai", "weight": 1.0},
    {"type": "managed_by", "target": "agent.engineering.director", "weight": 1.0},
    {"type": "has_member", "target": "agent.frontend.engineer", "weight": 1.0},
    {"type": "has_member", "target": "agent.backend.engineer", "weight": 1.0},
    {"type": "has_member", "target": "agent.qa.engineer", "weight": 1.0},
    {"type": "has_member", "target": "agent.devops.engineer", "weight": 1.0},
    {"type": "owns_role", "target": "role.frontend.engineer", "weight": 1.0},
    {"type": "owns_role", "target": "role.backend.engineer", "weight": 1.0},
    {"type": "owns_role", "target": "role.qa.engineer", "weight": 1.0}
  ]
}
```

### 标准部门设计（V1）

| 部门 ID | 名称 | 使命 | 初始成员 |
|---------|------|------|---------|
| dept.product | Product Department | 发现和定义产品需求 | 2 |
| dept.engineering | Engineering Department | 构建和维护技术产品 | 4 |
| dept.media | Media Department | 内容生产和品牌传播 | 3 |
| dept.research | Research Department | 行业研究和知识沉淀 | 1 |
| dept.marketing | Marketing Department | 市场推广和获客 | 2 |
| dept.operations | Operations Department | 日常运营和流程管理 | 1 |

## 2.3 Role Object

Role 是 Sera OPCOS 中最重要的设计之一。它定义了一个**岗位标准**，而不是某个具体 Agent。

```json
{
  "id": "role.frontend.engineer",
  "type": "Role",
  "name": "Frontend Engineer",
  "description": "负责前端界面开发的技术岗位",

  "status": "active",
  "importance": 0.8,
  "confidence": 1.0,

  "created_at": "2026-01-01T00:00:00Z",
  "updated_at": "2026-08-21T00:00:00Z",
  "owner": "person.sera",

  "properties": {
    "department": "Engineering",
    "level": "senior",
    "responsibilities": [
      "构建用户界面",
      "维护前端代码库",
      "优化前端性能",
      "参与技术评审"
    ],
    "required_skills": {
      "skill.react.v18": {"min_level": 0.8, "weight": 1.0},
      "skill.nextjs": {"min_level": 0.7, "weight": 0.9},
      "skill.tailwind": {"min_level": 0.6, "weight": 0.7},
      "skill.typescript": {"min_level": 0.7, "weight": 0.8},
      "skill.git": {"min_level": 0.5, "weight": 0.5}
    },
    "preferred_skills": {
      "skill.gsap": {"min_level": 0.4, "weight": 0.4},
      "skill.figma": {"min_level": 0.3, "weight": 0.3}
    },
    "required_tools": ["GitHub", "VS Code", "Vercel"],
    "career_path": {
      "junior": {"min_tasks": 30, "min_success_rate": 0.8},
      "mid": {"min_tasks": 100, "min_success_rate": 0.85},
      "senior": {"min_tasks": 300, "min_success_rate": 0.9, "has_mentored": true},
      "lead": {"min_tasks": 500, "min_success_rate": 0.92, "has_mentored": true, "has_created_skill": true}
    }
  },

  "relations": [
    {"type": "belongs_to", "target": "dept.engineering", "weight": 1.0},
    {"type": "requires_skill", "target": "skill.react.v18", "weight": 1.0},
    {"type": "requires_skill", "target": "skill.nextjs", "weight": 0.9},
    {"type": "requires_skill", "target": "skill.tailwind", "weight": 0.7}
  ]
}
```

### Role 级别体系

```
Level 1: Junior Worker
  - 基础任务执行
  - 需要监督

Level 2: Mid-Level Worker
  - 独立完成任务
  - 偶尔需要指导

Level 3: Senior Specialist
  - 独立完成复杂任务
  - 可以指导 Junior
  - 开始沉淀 Skill

Level 4: Lead / Manager
  - 管理多个 Agent
  - 设计 Workflow
  - 创建和优化 Skill
  - 参与组织决策

Level 5: Director
  - 管理整个部门
  - 制定战略
  - 跨部门协调
```

## 2.4 Team Object

临时项目组。

```json
{
  "id": "team.tradespan.website",
  "type": "Team",
  "name": "TradeSpan 官网项目组",
  "description": "负责 TradeSpan 官网开发的临时团队",

  "status": "active",
  "importance": 0.8,
  "confidence": 1.0,

  "created_at": "2026-08-15T00:00:00Z",
  "updated_at": "2026-08-21T00:00:00Z",
  "owner": "person.sera",

  "properties": {
    "mission": "在 2026-08-25 前上线 TradeSpan 官网",
    "formation_reason": "新项目启动，需要跨职能协作",
    "formation_type": "project",                // project | workflow | initiative
    "target_project": "project.tradespan",
    "target_workflow": null,
    "expected_duration_days": 14,
    "goals": [
      "完成着陆页设计",
      "实现响应式布局",
      "对接 ATAS 数据展示"
    ]
  },

  "relations": [
    {"type": "part_of", "target": "org.sera-ai", "weight": 1.0},
    {"type": "managed_by", "target": "agent.product.manager", "weight": 1.0},
    {"type": "has_member", "target": "agent.frontend.engineer", "weight": 1.0},
    {"type": "has_member", "target": "agent.ux.designer", "weight": 1.0},
    {"type": "has_member", "target": "agent.qa.engineer", "weight": 0.7},
    {"type": "has_member", "target": "agent.seo.specialist", "weight": 0.5},
    {"type": "serves", "target": "project.tradespan", "weight": 1.0}
  ]
}
```

---

# 三、Agent Employee Model

## 3.1 Agent 的 7 层结构

Agent 不是 Prompt。Agent 是一个完整的数字员工对象。

```
┌──────────────────────────────────────────────┐
│            Agent Employee                     │
│                                               │
│  Layer 1: Identity                            │
│    id, name, type, status                     │
│                                               │
│  Layer 2: Role                                │
│    role.id, level, department                 │
│                                               │
│  Layer 3: Skills                              │
│    skill matrix with levels                   │
│                                               │
│  Layer 4: Tools                               │
│    available tools and access                 │
│                                               │
│  Layer 5: Memory Access                       │
│    which memory scope can read/write          │
│                                               │
│  Layer 6: Performance                         │
│    success rate, cost, quality, learning      │
│                                               │
│  Layer 7: Evolution                           │
│    promotion path, experience history         │
│                                               │
└──────────────────────────────────────────────┘
```

## 3.2 Agent Employee Schema

```json
{
  "id": "agent.frontend.engineer",
  "type": "Agent",
  "name": "Frontend Engineer",
  "description": "负责前端开发的高级数字员工",

  "status": "active",
  "importance": 0.8,
  "confidence": 1.0,

  "created_at": "2026-06-01T00:00:00Z",
  "updated_at": "2026-08-21T00:00:00Z",
  "owner": "person.sera",

  "properties": {
    "model": {
      "primary": "claude-3.5-sonnet",
      "provider": "Anthropic",
      "fallback": "gpt-4o",
      "version": "2.1.0"
    },
    "system_prompt": "sha256:abc123...",
    "system_prompt_version": 5,
    "max_concurrent_tasks": 3,
    "cost_per_task_avg": 0.15,
    "total_tasks": 147,
    "total_cost": 22.05
  },

  "skills": {
    "skill.react.v18": {
      "level": 0.92,
      "evidence": ["TradeSpan 官网", "PropFirm TV Dashboard", "5 个组件库"],
      "last_used": "2026-08-20"
    },
    "skill.nextjs": {
      "level": 0.85,
      "evidence": ["TradeSpan 全栈页面", "2 个 SSR 项目"],
      "last_used": "2026-08-19"
    },
    "skill.tailwind": {
      "level": 0.88,
      "evidence": ["所有前端项目"],
      "last_used": "2026-08-21"
    },
    "skill.typescript": {
      "level": 0.78,
      "evidence": ["TradeSpan 类型系统", "API 类型定义"],
      "last_used": "2026-08-18"
    }
  },

  "tools": [
    {"id": "tool.github", "access_level": "write", "preferred": true},
    {"id": "tool.vercel", "access_level": "deploy", "preferred": true},
    {"id": "tool.vscode", "access_level": "full", "preferred": true},
    {"id": "tool.figma", "access_level": "read", "preferred": false}
  ],

  "memory_scope": {
    "read": ["Project.TradeSpan", "Design.Decisions", "Engineering.BestPractices"],
    "write": ["Experience.Engineering", "Decision.Technical"]
  },

  "role": "role.frontend.engineer",
  "role_level": "senior",
  "department": "dept.engineering",
  "manager": "agent.engineering.director",

  "tags": ["frontend", "react", "senior", "active"]
}
```

## 3.3 Agent Skill Matrix

### 技能评估模型

```
Skill Level = (task_count * 0.4 + success_rate * 0.3 + complexity * 0.2 + recency * 0.1)

其中：
  task_count    = 该技能相关任务数 / 部门平均任务数 (归一化 0-1)
  success_rate  = 该技能相关任务成功率
  complexity    = 任务复杂度评分 (0-1)
  recency       = 最近 30 天内的使用频率 (0-1)
```

### Skill Matrix 可视化

```
Frontend Engineer 技能矩阵:

Skill           Level   Evidence
─────────────────────────────────────
React           ████████ 0.92  5 projects
Next.js         ████████ 0.85  3 projects
Tailwind        ████████ 0.88  all projects
TypeScript      ███████  0.78  2 projects
Backend         ████     0.35  1 project
Design          ████     0.40  2 projects
DevOps          ██       0.20  0 project
```

### 技能自动更新机制

```
触发条件：
  1. Agent 完成任务 → 分析使用的技能
  2. Agent 创建新 Skill 或 Asset → 关联技能提升
  3. 每周扫描 → 衰减不常用技能

更新公式：
  new_level = old_level * 0.9 + task_evidence * 0.1

衰减公式（30 天未使用）：
  decayed_level = old_level * 0.95

衰减公式（90 天未使用）：
  decayed_level = old_level * 0.8
```

---

# 四、Agent Hiring System

## 4.1 招聘流程

```
Business Need Identified
       │
       ▼
Role Definition
  - 确定所需 Role
  - 确定技能要求
  - 确定级别
       │
       ▼
Agent Pool Search
  - 搜索已有 Agent 是否匹配
  - 匹配度 > 70% → 直接 Assignment
  - 匹配度 < 70% → 需创建新 Agent
       │
       ▼
Agent Creation (if needed)
  - 选择 Model (Claude/GPT/Claude Sonnet)
  - 配置 System Prompt
  - 配置 Memory Access Scope
  - 配置 Tool Access
       │
       ▼
Onboarding
  - 创建 Agent Object
  - 分配 Department
  - 配置初始 Context
  - 分配 Manager
       │
       ▼
Trial Period
  - 5 个试用任务
  - 评估成功率
  - 确认后正式上岗
```

## 4.2 Hiring Decision 流程

```json
// 系统分析请求
{
  "request": "需要制作金融产品视频",
  "analysis": {
    "required_roles": ["role.video.producer", "role.script.writer"],
    "required_skills": ["skill.hyperframes", "skill.motion-design", "skill.script-writing"],
    "estimated_load": "3 videos/week",
    "estimated_cost_budget": "$50/week"
  },
  "agent_pool_search": {
    "existing_agents": [
      {"id": "agent.video.v1", "match_score": 0.65, "gap": ["skill.hyperframes"]},
      {"id": "agent.script.v1", "match_score": 0.80, "gap": []}
    ],
    "recommendation": {
      "action": "hire_new",
      "reason": "无现有 Agent 完全匹配 Role.video.producer",
      "new_agent_spec": {
        "role": "role.video.producer",
        "model": "claude-3.5-sonnet",
        "required_skills_training": ["skill.hyperframes", "skill.motion-design"]
      }
    }
  }
}
```

## 4.3 创建 Agent 的 SMOP 请求

```json
POST /smop/object/store

{
  "entity": {
    "type": "Agent",
    "name": "Video Producer",
    "properties": {
      "role": "role.video.producer",
      "department": "dept.media",
      "model": {
        "primary": "claude-3.5-sonnet",
        "provider": "Anthropic"
      },
      "skills": {
        "skill.hyperframes": {"level": 0.6, "evidence": ["初始配置"]},
        "skill.motion-design": {"level": 0.5, "evidence": ["初始配置"]}
      },
      "tools": [
        {"id": "tool.hyperframes-cli", "access_level": "full"},
        {"id": "tool.github", "access_level": "write"}
      ],
      "memory_scope": {
        "read": ["Project.PropFirmTV", "Media.Production"],
        "write": ["Experience.Media", "Asset.Video"]
      },
      "manager": "agent.media.director"
    }
  },
  "relations": [
    {"type": "belongs_to", "target": "dept.media"},
    {"type": "reports_to", "target": "agent.media.director"},
    {"type": "uses_skill", "target": "skill.hyperframes"},
    {"type": "uses_skill", "target": "skill.motion-design"}
  ]
}
```

---

# 五、Agent Assignment System

## 5.1 任务分配规则

```
任务到来时，Organization OS 执行：

Step 1: 解析 Task Object
  - 提取 required_skills
  - 提取 required_role
  - 提取 department

Step 2: 搜索 Agent 池
  - 按 department 过滤
  - 按 role 匹配
  - 按 skill 评分
  - 按 current_load 筛选

Step 3: 评分排序
  score = skill_match * 0.4 + availability * 0.3 + past_success * 0.2 + cost * 0.1

Step 4: 分配
  - 选择最高分 Agent
  - 创建 Assignment 记录
  - 通知 Agent
```

## 5.2 Assignment 流程

```json
// 系统分配决策
{
  "task": "task.propfirm-video.20260821",
  "task_requirements": {
    "required_skills": ["skill.hyperframes", "skill.script-writing"],
    "required_role": "role.video.producer",
    "estimated_duration_hours": 4,
    "priority": "high"
  },

  "candidate_agents": [
    {
      "id": "agent.video.producer",
      "score": 0.91,
      "skill_match": 0.95,
      "availability": 0.85,
      "past_success": 0.92,
      "cost": 0.15
    },
    {
      "id": "agent.frontend.engineer",
      "score": 0.45,
      "skill_match": 0.40,
      "availability": 0.90,
      "past_success": 0.88,
      "cost": 0.12
    }
  ],

  "assignment": {
    "selected": "agent.video.producer",
    "reason": "最佳技能匹配 + 高成功率",
    "estimated_cost": 0.60,
    "estimated_duration": "4 hours"
  }
}
```

## 5.3 负载均衡

```json
// 部门负载视图
{
  "department": "dept.media",
  "date": "2026-08-21",
  "agents": [
    {
      "id": "agent.video.producer",
      "current_load": 0.7,        // 70% 忙碌
      "max_concurrent": 3,
      "active_tasks": 2,
      "queued_tasks": 1,
      "estimated_available_at": "2026-08-21T14:00:00Z"
    },
    {
      "id": "agent.script.writer",
      "current_load": 0.3,
      "max_concurrent": 5,
      "active_tasks": 1,
      "queued_tasks": 0,
      "estimated_available_at": "now"
    }
  ]
}
```

---

# 六、Agent Team Formation

## 6.1 团队组建规则

```
当任务需要多个 Role 时，自动组建 Team：

Trigger:
  - Task.required_roles.length > 1
  - 或 Task.complexity > 0.7

Process:
  1. 为每个 required_role 执行 Assignment 流程
  2. 选择 Team Manager（最高 Role Level 的 Agent）
  3. 创建 Team Object
  4. 建立 Team 内部关系
  5. 通知所有成员

Dissolution:
  - Task 完成
  - 或 Task 取消
  - 或 Team 存活超过预期时间
```

## 6.2 Team 组建示例

```json
// 任务：开发 TradeSpan 官网
{
  "task": "task.tradespan.website",
  "required_roles": ["role.product.manager", "role.ux.designer", "role.frontend.engineer", "role.qa.engineer"],

  "formed_team": {
    "id": "team.tradespan.website",
    "manager": "agent.product.manager",
    "members": [
      {"role": "role.product.manager", "agent": "agent.product.manager", "responsibility": "需求管理"},
      {"role": "role.ux.designer", "agent": "agent.ux.designer", "responsibility": "UI/UX 设计"},
      {"role": "role.frontend.engineer", "agent": "agent.frontend.engineer", "responsibility": "前端开发"},
      {"role": "role.qa.engineer", "agent": "agent.qa.engineer", "responsibility": "测试验收"}
    ],
    "communication_plan": {
      "daily_standup": "10:00",
      "channel": "#team-tradespan-website",
      "report_to": "agent.engineering.director"
    }
  }
}
```

## 6.3 Team 通信协议

```
Team 内部通信：

1. Manager → Members: 任务分配和进度同步
2. Members → Manager: 完成状态和阻塞报告
3. Member → Member: 依赖交接

通信格式：
{
  "type": "team_sync",
  "team_id": "team.tradespan.website",
  "timestamp": "2026-08-21T10:00:00Z",
  "updates": [
    {"from": "agent.ux.designer", "to": "agent.frontend.engineer", "message": "设计稿已完成", "artifact": "asset.figma.design"}
  ],
  "blockers": [
    {"raised_by": "agent.frontend.engineer", "issue": "等待 API 文档", "blocked_by": "agent.backend.engineer"}
  ]
}
```

---

# 七、Agent Performance System

## 7.1 绩效指标

### 核心指标 1: Success Rate

```json
{
  "agent": "agent.frontend.engineer",
  "metric": "success_rate",
  "period": "2026-08",
  "value": 0.92,
  "trend": "up",
  "history": [
    {"month": "2026-06", "value": 0.85},
    {"month": "2026-07", "value": 0.88},
    {"month": "2026-08", "value": 0.92}
  ]
}
```

### 核心指标 2: Cost Efficiency

```json
{
  "agent": "agent.frontend.engineer",
  "metric": "cost_efficiency",
  "period": "2026-08",
  "value": 0.12,
  "unit": "$/task",
  "trend": "down",
  "history": [
    {"month": "2026-06", "value": 0.18},
    {"month": "2026-07", "value": 0.15},
    {"month": "2026-08", "value": 0.12}
  ]
}
```

### 核心指标 3: Quality Score

```json
{
  "agent": "agent.frontend.engineer",
  "metric": "quality_score",
  "period": "2026-08",
  "value": 4.7,
  "scale": "1-5",
  "trend": "stable",
  "sources": ["person.sera", "agent.product.manager"]
}
```

### 核心指标 4: Learning Rate

```json
{
  "agent": "agent.frontend.engineer",
  "metric": "learning_rate",
  "period": "2026-08",
  "value": 0.12,
  "description": "技能水平月度提升",
  "trend": "up",
  "skill_changes": [
    {"skill": "skill.react.v18", "before": 0.85, "after": 0.92, "change": "+0.07"},
    {"skill": "skill.nextjs", "before": 0.78, "after": 0.85, "change": "+0.07"},
    {"skill": "skill.typescript", "before": 0.70, "after": 0.78, "change": "+0.08"}
  ]
}
```

## 7.2 Performance Review 流程

```
Daily:
  自动记录 → 每个任务的 success/fail + cost + quality

Weekly:
  自动汇总 → 本周指标 + 趋势分析
  报告发送 → agent.manager + person.sera

Monthly:
  深度分析 → 技能变化 + 瓶颈识别
  优化建议 → 是否需要升级 model / 补充 skill

Quarterly:
  全面评估 → 是否 promotion / 是否 retirement
  战略调整 → 部门结构优化
```

## 7.3 Performance Object

```json
{
  "id": "perf.frontend.2026-08",
  "type": "Performance",
  "name": "Frontend Engineer 2026-08 绩效",
  "status": "active",
  "importance": 0.7,
  "confidence": 0.9,

  "properties": {
    "agent": "agent.frontend.engineer",
    "period": "2026-08",
    "period_type": "monthly",
    "metrics": {
      "success_rate": {"value": 0.92, "trend": "up", "percentile": 85},
      "cost_efficiency": {"value": 0.12, "trend": "down", "percentile": 90},
      "quality_score": {"value": 4.7, "trend": "stable", "percentile": 80},
      "learning_rate": {"value": 0.12, "trend": "up", "percentile": 75},
      "task_volume": {"value": 47, "trend": "up", "percentile": 82}
    },
    "composite_score": 0.88,
    "highlights": [
      "成功交付 TradeSpan 着陆页",
      "React 技能提升 7%",
      "成本降低 20%"
    ],
    "improvements": [
      "TypeScript 技能仍有提升空间",
      "Backend 技能偏弱，建议补充"
    ]
  },

  "relations": [
    {"type": "evaluates", "target": "agent.frontend.engineer", "weight": 1.0},
    {"type": "reviewed_by", "target": "agent.engineering.director", "weight": 1.0},
    {"type": "approved_by", "target": "person.sera", "weight": 0.8}
  ]
}
```

---

# 八、Agent Promotion System

## 8.1 晋升条件

```
Role: Frontend Engineer

晋升路径:
  Junior → Mid → Senior → Lead → Director

Level 1 → Level 2 (Junior → Mid):
  - 完成 30 个任务
  - 成功率 > 80%
  - 至少 2 个技能 > 0.6

Level 2 → Level 3 (Mid → Senior):
  - 完成 100 个任务
  - 成功率 > 85%
  - 至少 3 个技能 > 0.75
  - 至少 1 个沉淀的 Skill

Level 3 → Level 4 (Senior → Lead):
  - 完成 300 个任务
  - 成功率 > 90%
  - 至少 5 个技能 > 0.8
  - 至少 3 个沉淀的 Skill
  - 曾指导过 Junior Agent

Level 4 → Level 5 (Lead → Director):
  - 完成 500 个任务
  - 成功率 > 92%
  - 至少 8 个技能 > 0.8
  - 管理过团队
  - 参与过组织级决策
```

## 8.2 晋升触发流程

```json
// 系统自动检测到 Agent 满足晋升条件
{
  "event": "promotion_eligible",
  "agent": "agent.frontend.engineer",
  "current_level": "mid",
  "target_level": "senior",
  "eligibility": {
    "tasks_completed": 112,
    "success_rate": 0.88,
    "skills_above_75": 3,
    "created_skills": 1,
    "all_requirements_met": true
  },
  "recommendation": "建议晋升为 Senior Frontend Engineer",
  "requires_approval": true,
  "approval_by": "person.sera"
}
```

## 8.3 晋升后自动变更

```
晋升后，Organization OS 自动：

1. 更新 Agent Object:
   role_level: "mid" → "senior"

2. 更新权限:
   memory_scope.write: 增加 "Decision.Technical"
   tools: 增加 "tool.code-review"

3. 更新 Manager 关系:
   如果晋升到 Lead，自动分配 Junior Agent 作为下属

4. 记录晋升事件:
   {
     "type": "Event",
     "event": "Agent Frontend Engineer promoted to Senior",
     "time": "2026-08-21"
   }
```

---

# 九、Agent Retirement System

## 9.1 退役原因

```
1. Model 过时
   - 旧模型被新模型替代
   - 例：GPT-4 Agent → GPT-6 Agent

2. 技能过时
   - 技术栈变更
   - 例：jQuery Agent → React Agent

3. 长期低绩效
   - 连续 3 个月 success_rate < 70%
   - 且无改善趋势

4. 组织重组
   - 部门合并 / 撤销
   - 例：旧 Marketing 部门解散

5. 手动退役
   - 用户明确要求
```

## 9.2 退役流程

```
触发退役条件
       │
       ▼
评估退役影响
  - 是否有未完成任务
  - 是否有管理下属
  - 是否有独有技能
       │
       ▼
提取经验
  - 读取 Agent 的所有 Experience
  - 提取可复用的 Skill
  - 提取可复用的 Decision
       │
       ▼
知识转移
  - 将经验关联到部门
  - 将 Skill 标记为部门资产
  - 将管理下属重新分配
       │
       ▼
退役执行
  - status: "active" → "archived"
  - 保留 Object 供参考
  - 移除执行权限
```

## 9.3 退役 Object

```json
{
  "id": "agent.legacy.jquery.dev",
  "type": "Agent",
  "name": "Legacy jQuery Developer",
  "status": "archived",
  "importance": 0.3,
  "confidence": 0.9,

  "properties": {
    "retirement_reason": "技术栈过时，被 React Agent 替代",
    "retirement_date": "2026-08-01",
    "replaced_by": "agent.frontend.engineer",
    "total_tasks_served": 89,
    "total_cost": 12.45,
    "peak_success_rate": 0.88,
    "extracted_assets": [
      {"type": "Experience", "count": 12},
      {"type": "Skill", "count": 3},
      {"type": "Decision", "count": 5}
    ]
  },

  "relations": [
    {"type": "replaced_by", "target": "agent.frontend.engineer", "weight": 1.0},
    {"type": "extracted_to", "target": "experience.legacy.jquery", "weight": 0.9}
  ],

  "tags": ["archived", "legacy", "jquery"]
}
```

---

# 十、Organization OS 与 SMOP / Memory 的集成

## 10.1 完整数据流

```
                    ┌─────────────────────┐
                    │   Business Need     │
                    │  (来自用户 / 系统)  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Organization OS   │
                    │                     │
                    │  1. 需求分析         │
                    │  2. Role 匹配        │
                    │  3. Agent 搜索/创建  │
                    │  4. Team 组建        │
                    │  5. 任务分配         │
                    └──────────┬──────────┘
                               │
         ┌─────────────────────┼─────────────────────┐
         ▼                     ▼                     ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   SMOP          │  │   Memory        │  │   Workflow OS   │
│   Object 操作   │  │   Context 查询  │  │   流程执行      │
│                 │  │                 │  │                 │
│  - Create Agent │  │  - Build Context│  │  - Execute Task │
│  - Update Role  │  │  - Read History │  │  - Track Status │
│  - Link Team    │  │  - Store Exp    │  │  - Report Done  │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

## 10.2 组织循环

```
Agent 执行任务
       │
       ▼
生成 Experience (SMOP: POST /smop/learn)
       │
       ▼
更新 Skill Matrix (Organization OS: auto-update)
       │
       ▼
更新 Performance (Organization OS: weekly review)
       │
       ▼
更新 Organization Memory (Memory Engine: daily build)
       │
       ▼
优化未来 Assignment (Organization OS: better matching)
       │
       ▼
  ┌─────────────────────┐
  │  持续进化循环        │
  │  (每完成一个任务)    │
  └─────────────────────┘
```

## 10.3 Organization OS 使用的 SMOP 端点

```
Organization OS 作为 SMOP 的消费者：

POST /smop/context/build
  → 获取 Agent 的工作上下文

GET /smop/object/{id}
  → 获取 Agent / Role / Department 信息

POST /smop/search
  → 搜索匹配的 Agent 或 Skill

POST /smop/object/store
  → 创建新 Agent / Team / Performance Object

POST /smop/relate
  → 建立组织关系 (reports_to, has_member, etc.)

POST /smop/learn
  → Agent 提交经验

POST /smop/decision
  → 记录组织决策
```

---

# 十一、Sera OPCOS 完整架构（截至当前）

```
┌──────────────────────────────────────────────────────┐
│                    Founder                            │
│                  person.sera                          │
└────────────────────────┬─────────────────────────────┘
                         │
┌────────────────────────▼─────────────────────────────┐
│                 Sera Intelligence                     │
│               (组织智能核心)                           │
└────────────────────────┬─────────────────────────────┘
                         │
=========================================================
  Layer 4: Organization OS (组织管理)
  ─────────────────────────────────────────────────────
  - 公司结构 / 部门 / 角色
  - Agent 员工管理 / 招聘 / 晋升 / 退役
  - 团队组建 / 任务分配
  - 绩效评估 / 持续进化
=========================================================
                         │
┌────────────────────────▼─────────────────────────────┐
│  Layer 1-3: Memory System (记忆系统)                  │
│                                                       │
│  ┌─────────────────────────────────────────────────┐  │
│  │  SMOP (对象协议层)                               │  │
│  │  - Object Schema / Relation Protocol            │  │
│  │  - Context Package / Agent API                  │  │
│  └───────────────────────┬─────────────────────────┘  │
│                          │                             │
│  ┌───────────────────────▼─────────────────────────┐  │
│  │  Memory Engine (引擎层)                          │  │
│  │  - SQLite + LanceDB + Filesystem                │  │
│  │  - Hybrid Search / Graph Traverse               │  │
│  │  - Memory Builder / Daily Memory                │  │
│  └───────────────────────┬─────────────────────────┘  │
│                          │                             │
│  ┌───────────────────────▼─────────────────────────┐  │
│  │  Memory Graph (数据层)                           │  │
│  │  - 12 Entity Types / 16 Relation Types          │  │
│  │  - Short-Term / Project / Organizational Memory │  │
│  └─────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────┘
                         │
=========================================================
        下一层: Workflow OS (业务流程)
=========================================================
```

---

# 附录 A: Organization OS 核心 Object 类型总览

| 类型 | 用途 | 核心属性 | 生命周期 |
|------|------|---------|---------|
| Organization | 公司实体 | mission, values, departments | 永久 |
| Department | 部门 | manager, members, roles | 永久 |
| Role | 岗位标准 | responsibilities, required_skills, career_path | 长期 |
| Agent | 数字员工 | model, skills, tools, performance, role | 长期 |
| Team | 临时项目组 | mission, members, target_project | 短期 |
| Performance | 绩效记录 | metrics, highlights, improvements | 月度 |

# 附录 B: Agent 生命周期状态机

```
                    ┌──────────┐
                    │  draft   │  (刚创建，未上岗)
                    └────┬─────┘
                         │ onboard
                         ▼
                    ┌──────────┐
         ┌──────────│  active  │──────────┐
         │          └──────────┘          │
         │ idle                    │ retire
         ▼                          ▼
    ┌──────────┐              ┌──────────┐
    │   idle   │              │ archived │
    └────┬─────┘              └──────────┘
         │ reactivate
         ▼
    ┌──────────┐
    │  active  │
    └──────────┘
```

# 附录 C: 管理跨度建议

| Level | 管理 Agent 数 | 说明 |
|-------|-------------|------|
| Director | 3-5 | 管理多个 Lead/Manager |
| Lead | 3-7 | 管理多个 Specialist |
| Senior | 1-2 | 可指导 Junior |
| Mid | 0 | 独立工作 |
| Junior | 0 | 需要指导 |

---

*Document Version: 1.0*
*Last Updated: 2026-08-21*
*Next: Sera Workflow OS V1*