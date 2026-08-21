# Sera Memory Object Protocol (SMOP) V1

## AI 公司内存总线协议

| Field | Value |
|-------|-------|
| Version | 1.0 |
| Status | Protocol Specification |
| Owner | Sera CTO |
| Layer | Communication (Layer 1) |
| Predecessor | Sera Memory Graph Schema V1, Sera Memory Engine V1 |
| Dependencies | Sera Memory Engine V1 |
| Target | DeepSeek / Trae / Codex Direct Execution |

---

# 0. Executive Summary

## 问题

Sera OPCOS 中有 Memory Graph（存储层）和 Memory Engine（基础设施），但缺少一个**通用协议**让所有组件（Agent、Workflow、Factory、Tool）以统一方式理解和操作对象。

## 类比

| 系统 | 协议 |
|------|------|
| Linux | 文件系统协议 (VFS) |
| Web | HTTP |
| AI Agent 工具 | MCP |
| **Sera OPCOS** | **SMOP** |

## 定义

**SMOP (Sera Memory Object Protocol)** 是 Sera OPCOS 中所有对象描述、连接、查询、更新和学习的统一协议。

它不是：

- 数据库 Schema（那是 Memory Engine 的事）
- API 规范（那是实现层的事）
- 配置文件格式（那是各组件的事）

它是：

> **AI 公司内部所有"东西"如何被描述、连接、查询、更新和学习的契约。**

---

# 一、核心思想：Everything is an Object

## 1.1 第一性原理

Sera OPCOS 中，任何东西都是一个 Object。

```
人      → Person Object
项目    → Project Object
Agent  → Agent Object
技能    → Skill Object
任务    → Task Object
经验    → Experience Object
决策    → Decision Object
规则    → Rule Object
文件    → Asset Object
事件    → Event Object
对话    → Conversation Object
工作流  → Workflow Object
产品    → Product Object
公司    → Company Object
```

## 1.2 统一结构

所有 Object 共享同一个顶层结构：

```json
{
  "id": "xxx",
  "type": "Project",
  "name": "TradeSpan",
  "properties": {},
  "relations": [],
  "events": [],
  "memory": {},
  "metadata": {}
}
```

## 1.3 Why Not Just JSON?

JSON 是一种格式，不是协议。

SMOP 定义了：

```
1. 每个字段的含义和约束
2. ID 的命名规则
3. 类型的标准枚举
4. 关系的标准语义
5. 状态机的生命周期
6. 可信度评估方法
7. 上下文构建规则
8. 版本演化策略
```

---

# 二、Object Base Schema

## 2.1 基类定义

所有 SMOP Object 必须继承以下基类：

```json
{
  "id": "string (required)",
  "type": "string (required, enum)",
  "name": "string (required)",
  "description": "string (optional)",

  "status": "string (enum: active | draft | archived | deprecated | replaced)",
  "importance": "number (0.0 ~ 1.0)",
  "confidence": "number (0.0 ~ 1.0)",

  "created_at": "string (ISO 8601)",
  "updated_at": "string (ISO 8601)",
  "owner": "string (Person ID or Agent ID)",

  "source": "Source Object (optional)",
  "tags": "string[] (optional)",
  "version": "number (default: 1)"
}
```

## 2.2 字段细则

### id

全局唯一标识符。采用分层命名空间。

```
格式：{namespace}.{name}[.{subtype}]

示例：
  project.tradespan
  agent.frontend.engineer
  decision.tradespan.dark-ui
  skill.react.v18
  rule.financial.trust-first
  experience.video.factory-v2
  asset.logo.tradespan
  event.website.launch
  workflow.video.production
  product.tradespan.software
  company.sera
  person.sera
```

### type

标准类型枚举（V1 支持 12 类，可扩展）：

```json
[
  "Person",
  "Company",
  "Project",
  "Product",
  "Agent",
  "Skill",
  "Workflow",
  "Asset",
  "Decision",
  "Experience",
  "Rule",
  "Event",
  "Conversation",
  "Task"
]
```

### status

生命周期状态机：

```
                    ┌─────────┐
                    │  draft  │
                    └────┬────┘
                         │ activate
                         ▼
                    ┌─────────┐
         ┌──────────│  active │──────────┐
         │          └─────────┘          │
         │ archive            │ deprecate
         ▼                    ▼
    ┌──────────┐        ┌────────────┐
    │ archived │        │ deprecated │
    └──────────┘        └──────┬─────┘
                               │ replace
                               ▼
                          ┌───────────┐
                          │ replaced  │
                          └───────────┘
```

### importance

| 范围 | 含义 | 示例 |
|------|------|------|
| 0.9 - 1.0 | 公司战略级 | 公司方向、核心决策 |
| 0.7 - 0.9 | 项目关键级 | 项目目标、关键技能 |
| 0.4 - 0.7 | 普通级 | 一般资产、任务 |
| 0.1 - 0.4 | 参考级 | 临时对话、草案 |
| 0.0 - 0.1 | 低价值 | 已过期信息 |

### confidence

| 范围 | 来源 | 示例 |
|------|------|------|
| 1.0 | 人工确认 | 用户手动创建的 Object |
| 0.9 | 系统确认 | 规则匹配的实体 |
| 0.7 | LLM 高置信度 | LLM 明确提取的实体 |
| 0.5 | LLM 推断 | LLM 模糊匹配 |
| 0.3 | 自动猜测 | 字符串相似度匹配 |
| 0.1 | 未验证 | 新提取的原始数据 |

### source

```json
{
  "type": "obsidian | github | chat | email | manual | api | system",
  "path": "string (optional, 原始路径)",
  "url": "string (optional, 外部链接)",
  "extracted_by": "string (optional, 提取器 ID)",
  "extracted_at": "string (ISO 8601)"
}
```

---

# 三、Entity Schema 定义

## 3.1 Person Object

```json
{
  "id": "person.sera",
  "type": "Person",
  "name": "Sera",
  "description": "公司创始人",

  "status": "active",
  "importance": 1.0,
  "confidence": 1.0,

  "created_at": "2026-01-01T00:00:00Z",
  "updated_at": "2026-08-21T00:00:00Z",
  "owner": "person.sera",

  "properties": {
    "role": "Founder",
    "responsibilities": ["Product", "BD", "Strategy"],
    "contact": {
      "email": "sera@example.com",
      "slack": "@sera"
    }
  },

  "relations": [
    {"type": "owns", "target": "company.sera", "weight": 1.0},
    {"type": "manages", "target": "project.tradespan", "weight": 0.9}
  ],

  "source": {
    "type": "manual",
    "extracted_at": "2026-01-01T00:00:00Z"
  }
}
```

## 3.2 Company Object

```json
{
  "id": "company.sera",
  "type": "Company",
  "name": "Sera Company",
  "description": "AI 原生公司",

  "status": "active",
  "importance": 1.0,
  "confidence": 1.0,

  "created_at": "2026-01-01T00:00:00Z",
  "updated_at": "2026-08-21T00:00:00Z",
  "owner": "person.sera",

  "properties": {
    "industry": "Fintech + AI",
    "headquarters": "Remote",
    "founded": "2026"
  },

  "relations": [
    {"type": "owned_by", "target": "person.sera", "weight": 1.0},
    {"type": "has_project", "target": "project.tradespan", "weight": 1.0},
    {"type": "has_project", "target": "project.propfirm-tv", "weight": 1.0}
  ]
}
```

## 3.3 Project Object

```json
{
  "id": "project.tradespan",
  "type": "Project",
  "name": "TradeSpan",
  "description": "连接 ATAS 和 MT4 的交易平台",

  "status": "active",
  "importance": 0.9,
  "confidence": 1.0,

  "created_at": "2026-06-15T00:00:00Z",
  "updated_at": "2026-08-21T00:00:00Z",
  "owner": "person.sera",

  "properties": {
    "goal": "连接 ATAS 和 MT4",
    "department": "Engineering",
    "start_date": "2026-06-15",
    "target_date": "2026-12-31",
    "milestones": [
      {"name": "MVP", "date": "2026-09-01", "status": "in_progress"},
      {"name": "Beta", "date": "2026-10-15", "status": "planned"}
    ]
  },

  "relations": [
    {"type": "belongs_to", "target": "company.sera", "weight": 1.0},
    {"type": "managed_by", "target": "agent.product.manager", "weight": 0.9},
    {"type": "depends_on", "target": "skill.react.v18", "weight": 0.8},
    {"type": "depends_on", "target": "skill.nextjs", "weight": 0.7},
    {"type": "related_to", "target": "decision.tradespan.dark-ui", "weight": 0.9}
  ],

  "tags": ["fintech", "trading", "active"]
}
```

## 3.4 Agent Object

这是 Sera OPCOS 特有，也是最重要的类型之一。

```json
{
  "id": "agent.frontend.engineer",
  "type": "Agent",
  "name": "Frontend Engineer",
  "description": "负责前端开发的数字员工",

  "status": "active",
  "importance": 0.8,
  "confidence": 1.0,

  "created_at": "2026-06-01T00:00:00Z",
  "updated_at": "2026-08-21T00:00:00Z",
  "owner": "person.sera",

  "properties": {
    "role": "Frontend Developer",
    "department": "Engineering",
    "model": "Claude 3.5 Sonnet",
    "model_provider": "Anthropic",
    "skills": ["React", "Next.js", "Tailwind CSS", "GSAP"],
    "tools": ["GitHub", "Vercel", "VS Code"],
    "performance": {
      "success_rate": 0.92,
      "tasks_completed": 47,
      "avg_quality_score": 0.88
    },
    "system_prompt_hash": "sha256:abc123...",
    "version": "2.1.0"
  },

  "relations": [
    {"type": "assigned_to", "target": "project.tradespan", "weight": 0.9},
    {"type": "uses_skill", "target": "skill.react.v18", "weight": 1.0},
    {"type": "uses_skill", "target": "skill.nextjs", "weight": 0.9},
    {"type": "learned_from", "target": "experience.video.ui-failure", "weight": 0.7},
    {"type": "reports_to", "target": "agent.product.manager", "weight": 1.0}
  ],

  "tags": ["frontend", "react", "active"]
}
```

> **注意：Agent Object 不是 Prompt。**
> Agent = 数字员工档案（身份、能力、表现、归属）。
> Prompt 是 Agent 的临时配置，不属于 SMOP 协议。

## 3.5 Skill Object

```json
{
  "id": "skill.react.v18",
  "type": "Skill",
  "name": "React 18",
  "description": "React 前端框架",

  "status": "active",
  "importance": 0.8,
  "confidence": 0.95,

  "created_at": "2026-06-01T00:00:00Z",
  "updated_at": "2026-08-21T00:00:00Z",
  "owner": "system",

  "properties": {
    "category": "Frontend Framework",
    "version": "18.2.0",
    "proficiency_required": "advanced",
    "alternatives": ["Vue 3", "Svelte"],
    "dependencies": ["Node.js 18+", "npm"],
    "resources": [
      {"type": "doc", "url": "https://react.dev"},
      {"type": "tutorial", "path": "obsidian://03_Area/react-cookbook"}
    ]
  },

  "relations": [
    {"type": "used_by", "target": "agent.frontend.engineer", "weight": 1.0},
    {"type": "required_by", "target": "project.tradespan", "weight": 0.9}
  ]
}
```

## 3.6 Decision Object（组织记忆核心）

这是大多数 AI 系统缺失的类型。

**知识 ≠ 决策。**

文件写着"官网深蓝色"，AI 不知道为什么。

Decision Object 解决了这个问题。

```json
{
  "id": "decision.tradespan.dark-ui",
  "type": "Decision",
  "name": "TradeSpan 暗色金融科技 UI",
  "description": "采用暗色金融科技风格作为 TradeSpan 的设计语言",

  "status": "active",
  "importance": 0.9,
  "confidence": 1.0,

  "created_at": "2026-08-18T14:30:00Z",
  "updated_at": "2026-08-18T14:30:00Z",
  "owner": "person.sera",

  "properties": {
    "context": "TradeSpan 官网重新设计",
    "decision": "采用暗色金融科技风格 (Dark Fintech Style)",
    "reason": "增强交易者信任感，符合行业审美",
    "alternatives_considered": ["亮色商务风", "极简白"],
    "alternatives_rejected_reason": "不够可信，商务风太通用",
    "scope": ["Website", "Dashboard", "Landing Page"],
    "constraints": [
      "主黑 #05070A",
      "主题蓝 #146EFF",
      "避免大面积渐变"
    ]
  },

  "relations": [
    {"type": "applies_to", "target": "project.tradespan", "weight": 1.0},
    {"type": "supersedes", "target": "decision.tradespan.light-ui", "weight": 0.8}
  ],

  "tags": ["design", "ui", "branding"]
}
```

### supersedes 关系

这是 Decision Object 的核心能力。

```
旧决策 D1 (Light UI)
  → 新决策 D2 (Dark UI) supersedes D1

Agent 查询时：
  - 自动忽略被 supersedes 的决策
  - 返回 D2 作为当前有效决策
```

## 3.7 Experience Object（组织学习核心）

```json
{
  "id": "experience.video.ui-failure",
  "type": "Experience",
  "name": "纯 AI 视频缺乏 UI 控制",
  "description": "尝试用纯 AI 生成金融视频，结果缺乏 UI 可信度",

  "status": "active",
  "importance": 0.85,
  "confidence": 0.95,

  "created_at": "2026-08-16T10:00:00Z",
  "updated_at": "2026-08-20T00:00:00Z",
  "owner": "person.sera",

  "properties": {
    "task": "生成金融产品宣传视频",
    "attempts": 3,
    "result": "failed",
    "failure_mode": "纯 AI 生成的视频缺乏真实的 UI 界面",
    "root_cause": "AI 视频生成无法精确控制 UI 元素",
    "resolution": "改用 React + GSAP 生成前端动效 + 录屏拼接",
    "lesson": "金融产品视频必须有真实 UI 素材",
    "applies_to": ["Video Factory", "Product Demo"],
    "reusable_artifact": "Video Factory V2",
    "cost_of_failure": "3 天 + $200 API 费用"
  },

  "relations": [
    {"type": "related_to", "target": "project.propfirm-tv", "weight": 0.9},
    {"type": "learned_by", "target": "agent.video.producer", "weight": 1.0},
    {"type": "led_to", "target": "skill.video-factory-v2", "weight": 0.9},
    {"type": "led_to", "target": "decision.video.react-gsap", "weight": 0.8}
  ]
}
```

### Experience → Rule 的演化路径

```
Experience（失败经验）
  → 提取 Lesson
  → 如果 Lesson 被验证 3 次以上
  → 升级为 Rule（组织原则）
```

## 3.8 Rule Object（新增类型）

如果说 Experience 是"发生过的事"，Rule 是"应该遵守的原则"。

```json
{
  "id": "rule.financial.trust-first",
  "type": "Rule",
  "name": "金融产品可信优先原则",
  "description": "任何金融产品相关内容，必须优先考虑可信度",

  "status": "active",
  "importance": 0.95,
  "confidence": 0.9,

  "created_at": "2026-08-20T00:00:00Z",
  "updated_at": "2026-08-20T00:00:00Z",
  "owner": "person.sera",

  "properties": {
    "content": "金融产品设计中，可信度 > 炫技。始终展示真实交易界面，避免纯 AI 生成内容。",
    "scope": ["Video", "Landing Page", "Dashboard", "Marketing"],
    "priority": "high",
    "enforcement": "guideline",
    "source_experiences": [
      "experience.video.ui-failure"
    ],
    "examples": [
      {"good": "React + 真实录屏", "bad": "纯 AI 生成视频"}
    ]
  },

  "relations": [
    {"type": "derived_from", "target": "experience.video.ui-failure", "weight": 1.0},
    {"type": "applies_to", "target": "project.tradespan", "weight": 1.0},
    {"type": "applies_to", "target": "project.propfirm-tv", "weight": 1.0}
  ]
}
```

### Rule 的优先级层级

```
1. organization.rule          (公司级，所有 Agent 必须遵守)
2. department.rule            (部门级，特定 Agent 组)
3. project.rule               (项目级，仅该项目)
4. agent.rule                 (个人级，仅该 Agent)
```

## 3.9 Asset Object

```json
{
  "id": "asset.logo.tradespan",
  "type": "Asset",
  "name": "TradeSpan Logo",
  "description": "TradeSpan 品牌 Logo",

  "status": "active",
  "importance": 0.6,
  "confidence": 1.0,

  "properties": {
    "format": "SVG",
    "location": "github.com/78tyih/tradespan/assets/logo.svg",
    "local_path": "~/Projects/TradeSpan/assets/logo.svg",
    "size_bytes": 12480,
    "checksum": "sha256:def456..."
  },

  "relations": [
    {"type": "part_of", "target": "project.tradespan", "weight": 1.0},
    {"type": "used_by", "target": "asset.website.tradespan", "weight": 0.9}
  ]
}
```

## 3.10 Event Object

```json
{
  "id": "event.website.launch.20260820",
  "type": "Event",
  "name": "TradeSpan 网站上线",
  "description": "TradeSpan 官网正式上线",

  "status": "active",
  "importance": 0.7,
  "confidence": 1.0,

  "properties": {
    "event_type": "launch",
    "timestamp": "2026-08-20T18:00:00+08:00",
    "actor": "agent.frontend.engineer",
    "impact": "Production started",
    "details": {
      "url": "https://tradespan.io",
      "deployment": "Vercel",
      "duration": "2 days"
    }
  },

  "relations": [
    {"type": "related_to", "target": "project.tradespan", "weight": 1.0},
    {"type": "performed_by", "target": "agent.frontend.engineer", "weight": 1.0},
    {"type": "triggered", "target": "workflow.deployment", "weight": 0.8}
  ]
}
```

## 3.11 Workflow Object

```json
{
  "id": "workflow.video.production",
  "type": "Workflow",
  "name": "PropFirm 视频生产流程",
  "description": "从选题到发布的全流程视频生产",

  "status": "active",
  "importance": 0.8,
  "confidence": 0.9,

  "properties": {
    "trigger": "New topic assigned",
    "steps": [
      {"order": 1, "agent": "agent.research", "task": "研究选题"},
      {"order": 2, "agent": "agent.script", "task": "撰写脚本"},
      {"order": 3, "agent": "agent.visual", "task": "设计视觉"},
      {"order": 4, "agent": "agent.video", "task": "制作视频"}
    ],
    "output": "Social Video (MP4)",
    "avg_duration": "4 hours",
    "quality_check": true
  },

  "relations": [
    {"type": "managed_by", "target": "agent.video.producer", "weight": 1.0},
    {"type": "creates", "target": "asset.video.output", "weight": 1.0},
    {"type": "uses_skill", "target": "skill.video-factory-v2", "weight": 0.9}
  ]
}
```

## 3.12 Task Object

```json
{
  "id": "task.tradespan.landing-page.20260821",
  "type": "Task",
  "name": "构建 TradeSpan 着陆页",
  "description": "根据设计决策构建 TradeSpan 官网着陆页",

  "status": "active",
  "importance": 0.7,
  "confidence": 1.0,

  "properties": {
    "assigned_to": "agent.frontend.engineer",
    "priority": "high",
    "deadline": "2026-08-25",
    "status": "in_progress",
    "progress": 0.3,
    "requirements": [
      "暗色金融科技风格",
      "左右对齐布局",
      "避免过度动画"
    ],
    "deliverables": ["index.html", "styles.css", "assets/"]
  },

  "relations": [
    {"type": "part_of", "target": "project.tradespan", "weight": 1.0},
    {"type": "assigned_to", "target": "agent.frontend.engineer", "weight": 1.0},
    {"type": "follows_decision", "target": "decision.tradespan.dark-ui", "weight": 0.9},
    {"type": "follows_rule", "target": "rule.financial.trust-first", "weight": 0.8}
  ]
}
```

---

# 四、Relation Protocol

## 4.1 关系定义

所有关系使用统一格式：

```json
{
  "source": "string (Object ID)",
  "relation": "string (标准关系类型)",
  "target": "string (Object ID)",
  "weight": "number (0.0 ~ 1.0)",
  "confidence": "number (0.0 ~ 1.0, optional)",
  "metadata": "object (optional, 关系级上下文)",
  "created_at": "string (ISO 8601, optional)",
  "superseded_by": "string (Object ID, optional, 被谁替代)"
}
```

## 4.2 标准关系类型（V1 共 16 类）

### 所有权关系

| 关系 | 源 → 目标 | 含义 |
|------|----------|------|
| `owns` | Person → Company | 人拥有公司 |
| `owned_by` | Company → Person | 公司被谁拥有 |
| `belongs_to` | Project → Company | 项目属于公司 |

### 管理关系

| 关系 | 源 → 目标 | 含义 |
|------|----------|------|
| `manages` | Person/Agent → Project/Workflow | 人/Agent 管理项目/流程 |
| `managed_by` | Project/Workflow → Person/Agent | 项目/流程被谁管理 |
| `reports_to` | Agent → Agent | 汇报关系 |
| `assigned_to` | Task → Agent | 任务分配给谁 |

### 依赖关系

| 关系 | 源 → 目标 | 含义 |
|------|----------|------|
| `depends_on` | Project → Skill | 项目依赖技能 |
| `required_by` | Skill → Project | 技能被项目需要 |
| `uses_skill` | Agent → Skill | Agent 使用技能 |

### 产生关系

| 关系 | 源 → 目标 | 含义 |
|------|----------|------|
| `creates` | Workflow → Asset | 流程产生资产 |
| `part_of` | Asset → Project | 资产属于项目 |
| `led_to` | Experience → Skill/Decision | 经验导致了新技能/决策 |

### 学习关系

| 关系 | 源 → 目标 | 含义 |
|------|----------|------|
| `learned_from` | Agent → Experience | Agent 从经验学习 |
| `derived_from` | Rule → Experience | 规则从经验衍生 |

### 逻辑关系

| 关系 | 源 → 目标 | 含义 |
|------|----------|------|
| `supersedes` | Decision → Decision | 新决策替代旧决策 |
| `applies_to` | Decision/Rule → Project | 决策/规则适用于项目 |
| `follows_decision` | Task → Decision | 任务遵循决策 |
| `follows_rule` | Task → Rule | 任务遵循规则 |

### 通用关系

| 关系 | 源 → 目标 | 含义 |
|------|----------|------|
| `related_to` | Any → Any | 通用关联（兜底） |
| `triggered` | Event → Workflow | 事件触发流程 |
| `performed_by` | Event → Agent | 事件由谁执行 |
| `references` | Any → Any | 引用（弱关联） |

## 4.3 关系图可视化

```
                    ┌─────────────┐
                    │  person.sera│
                    └──────┬──────┘
                           │ owns
                           ▼
                    ┌─────────────┐
                    │ company.sera│
                    └──────┬──────┘
                           │ belongs_to
              ┌────────────┼────────────┐
              ▼            ▼            ▼
     ┌──────────────┐ ┌──────────┐ ┌──────────┐
     │project.trade │ │project.  │ │product.  │
     │ span         │ │propfirm  │ │tradespan │
     └──────┬───────┘ └──────────┘ └──────────┘
            │ depends_on
            ▼
     ┌──────────────┐
     │ skill.react  │
     └──────────────┘
            │ used_by
            ▼
     ┌──────────────────┐
     │agent.frontend.dev│
     └──────────────────┘
```

---

# 五、Context Package Protocol

## 5.1 问题

Agent 不应该直接读数据库或文件系统。

Agent 应该请求：**"我当前任务需要知道什么"**

## 5.2 Context Package 定义

Context Package 是 SMOP 最核心的交互模式。

它是一个**为特定 Agent + 特定任务"编译"的知识包**。

```json
{
  "context_id": "ctx.tradespan-landing.20260821",
  "target_agent": "agent.frontend.engineer",
  "target_task": "task.tradespan.landing-page.20260821",
  "compiled_at": "2026-08-21T09:00:00Z",
  "ttl_minutes": 120,

  "mission": {
    "summary": "构建 TradeSpan 着陆页",
    "project": "TradeSpan",
    "deadline": "2026-08-25",
    "priority": "high"
  },

  "project_context": {
    "name": "TradeSpan",
    "goal": "连接 ATAS 和 MT4",
    "status": "active",
    "department": "Engineering"
  },

  "active_decisions": [
    {
      "id": "decision.tradespan.dark-ui",
      "decision": "采用暗色金融科技风格",
      "reason": "增强交易者信任感",
      "constraints": ["主黑 #05070A", "主题蓝 #146EFF", "避免大面积渐变"]
    }
  ],

  "active_rules": [
    {
      "id": "rule.financial.trust-first",
      "content": "可信度 > 炫技。展示真实交易界面。",
      "priority": "high"
    }
  ],

  "relevant_experiences": [
    {
      "id": "experience.video.ui-failure",
      "lesson": "纯 AI 内容缺乏可信度，需要真实 UI 素材",
      "applies_to": ["Landing Page"]
    }
  ],

  "available_assets": [
    {"id": "asset.logo.tradespan", "type": "SVG", "path": "assets/logo.svg"},
    {"id": "asset.brand.guidelines", "type": "PDF", "path": "docs/brand.pdf"}
  ],

  "relevant_skills": [
    {"id": "skill.react.v18", "proficiency": "required"},
    {"id": "skill.tailwind", "proficiency": "required"}
  ],

  "stale_information": [
    {
      "id": "decision.tradespan.light-ui",
      "reason": "已被 dark-ui 决策 supersedes",
      "superseded_by": "decision.tradespan.dark-ui"
    }
  ]
}
```

## 5.3 Context Package 构建规则

```
构建算法：

1. 解析 Task Object → 获取 project 和 requirements
2. 找到 Project Object → 获取 goal, status, department
3. 找到所有 applies_to = project 的 Decision Object
   - 过滤掉被 supersedes 的
   - 按 importance 排序
4. 找到所有 applies_to = project 的 Rule Object
   - 按 priority 排序
5. 找到所有 related_to = project 的 Experience Object
   - 按 importance 排序
   - 只保留 result = failed 或 lesson 非空的
6. 找到所有 part_of = project 的 Asset Object
   - 按重要性排序
7. 找到所有 depends_on = project 的 Skill Object
   - 匹配 Agent 已拥有的 skill
8. 标记所有被 supersedes 的 Decision 为 stale
```

## 5.4 Context Package 更新

```yaml
context_package:
  ttl: 120 minutes          # 2 小时后过期
  refresh_trigger:
    - task_status_changed
    - new_decision_added
    - new_experience_added
    - agent_requested

  cache: local_memory       # 不持久化，用完即弃
```

---

# 六、Agent Memory API

## 6.1 API 端点

### POST /smop/context/build

构建 Context Package。

```json
// Request
{
  "agent": "agent.frontend.engineer",
  "task": "task.tradespan.landing-page.20260821"
}

// Response: Context Package (见第五章)
```

### GET /smop/object/{id}

获取单个 Object。

```json
// GET /smop/object/decision.tradespan.dark-ui

// Response
{
  "id": "decision.tradespan.dark-ui",
  "type": "Decision",
  "name": "TradeSpan 暗色金融科技 UI",
  "properties": { ... },
  "relations": [ ... ]
}
```

### POST /smop/search

语义搜索。

```json
// Request
{
  "query": "TradeSpan 的设计约束",
  "types": ["Decision", "Rule"],
  "top_k": 5
}
```

### POST /smop/learn

Agent 完成任务后提交经验。

```json
// Request
{
  "task": "task.tradespan.landing-page.20260821",
  "result": "success",
  "lesson": "Tailwind 的暗色模式配置需要注意 contrast 比例",
  "applies_to": ["project.tradespan"],
  "artifacts": ["asset.landing-page.source"]
}
```

### POST /smop/decision

记录决策。

```json
// Request
{
  "context": "着陆页颜色对比度",
  "decision": "使用 WCAG AA 标准的最小对比度 4.5:1",
  "reason": "确保可访问性",
  "scope": ["Landing Page", "Dashboard"],
  "owner": "agent.frontend.engineer"
}
```

### POST /smop/traverse

图遍历。

```json
// Request
{
  "start": "project.tradespan",
  "relation": "depends_on",
  "depth": 2
}
```

## 6.2 Agent 使用流程

```
Agent 启动时：
  1. POST /smop/context/build
  2. 将 Context Package 注入 System Prompt
  3. 开始工作

Agent 工作中：
  1. 需要信息 → GET /smop/object/{id} 或 POST /smop/search
  2. 做出决策 → POST /smop/decision
  3. 遇到问题 → POST /smop/learn (失败经验)

Agent 完成时：
  1. 提交经验 → POST /smop/learn
  2. 更新任务 → Task Object status = completed
```

---

# 七、SMOP 与 MCP 的关系

## 7.1 职责分离

```
              Agent
                │
        ┌───────┴───────┐
        │               │
       MCP             SMOP
        │               │
    Tools & API     Memory & Context
        │               │
    ┌───┴───┐       ┌───┴───┐
    │File   │       │Project│
    │GitHub │       │Decision│
    │Slack  │       │Experience│
    │Email  │       │Rule    │
    │Database│      │Skill  │
    └───────┘       └───────┘
```

## 7.2 对比

| 维度 | MCP | SMOP |
|------|-----|------|
| 解决问题 | Agent 如何调用工具 | Agent 如何理解组织 |
| 核心概念 | Tool + Resource + Prompt | Object + Relation + Context |
| 数据模型 | 工具输入/输出 Schema | Entity + Relation + Memory |
| 状态 | 无状态（每次调用独立） | 有状态（关系图和记忆累积） |
| 生命周期 | 请求级别 | 组织级别（持续积累） |
| 存储 | 无（仅协议） | 有（Memory Engine） |
| 典型用例 | 读文件、发消息、查数据库 | 获项目上下文、查历史决策、学经验 |

## 7.3 集成方案

Agent 同时使用 MCP 和 SMOP：

```
Agent 的 System Prompt 中：

[Memory Context]          ← SMOP 提供
- 当前项目：TradeSpan
- 设计决策：暗色金融科技
- 规则：可信度优先
- 经验：纯 AI 内容缺乏可信度

[Available Tools]         ← MCP 提供
- read_file(path)
- github_push(repo, branch)
- slack_send(channel, message)
- vercel_deploy(project)
```

**SMOP 本身也可以作为 MCP 的一个 Server 暴露：**

```
MCP Server: sera-memory

Tools:
  memory_context_build(task_id) → Context Package
  memory_object_get(id) → Object
  memory_search(query, types) → Object[]
  memory_learn(experience) → Experience ID
  memory_decision(decision) → Decision ID
```

这样，任何支持 MCP 的 Agent（Claude、Codex、Trae）都可以直接接入 Sera OPCOS 的 Memory。

---

# 八、SMOP 数据流

## 8.1 完整请求链路

```
Agent (Trae/Codex/Claude)
  │
  │  POST /smop/context/build
  ▼
Sera Memory Runtime
  │
  ├── 1. 解析请求
  │     ├── agent: agent.frontend.engineer
  │     └── task: task.tradespan.landing-page
  │
  ├── 2. 查询 Memory Engine
  │     ├── SQLite: GET Task Object
  │     ├── SQLite: GET Project Object + Relations
  │     ├── SQLite: GET Decision Objects (filter non-superseded)
  │     ├── SQLite: GET Rule Objects
  │     ├── SQLite: GET Experience Objects
  │     ├── LanceDB: 语义搜索相关上下文
  │     └── SQLite: GET Asset Objects
  │
  ├── 3. 编译 Context Package
  │     ├── 合并所有查询结果
  │     ├── 按 importance 排序
  │     ├── 标记 stale 信息
  │     └── 格式化输出
  │
  └── 4. 返回 Context Package
        │
        ▼
Agent 工作记忆
```

## 8.2 写入链路

```
Agent 完成任务
  │
  │  POST /smop/learn
  ▼
Sera Memory Runtime
  │
  ├── 1. 创建 Experience Object
  ├── 2. 建立 Relation (learned_by, related_to)
  ├── 3. 向量化 (LanceDB)
  ├── 4. 触发 Memory Builder（增量更新）
  │
  └── 5. 返回 Experience ID
```

---

# 九、SMOP V1 文档结构

## 协议文件

```
smop/
├── README.md                          # 协议概述
├── SPECIFICATION.md                   # 本文件（完整规范）
│
├── schemas/                           # JSON Schema 文件
│   ├── base-object.schema.json        # 基类 Schema
│   ├── person.schema.json
│   ├── company.schema.json
│   ├── project.schema.json
│   ├── agent.schema.json
│   ├── skill.schema.json
│   ├── decision.schema.json
│   ├── experience.schema.json
│   ├── rule.schema.json
│   ├── asset.schema.json
│   ├── event.schema.json
│   ├── workflow.schema.json
│   ├── task.schema.json
│   └── relation.schema.json
│
├── examples/                          # 示例文件
│   ├── project.tradespan.json
│   ├── agent.frontend.json
│   ├── decision.dark-ui.json
│   ├── experience.video-failure.json
│   ├── rule.trust-first.json
│   └── context-package.json
│
└── api/                               # API 规范
    └── openapi.yaml                   # OpenAPI 3.0 规范
```

---

# 十、从 Memory Engine 到 SMOP 的演进

## 之前（Memory Engine V1）

```
存储层 → 索引层 → API
```

Engine 面向**存储和检索**。

## 现在（SMOP V1）

```
Object Schema → Relation Protocol → Context Package → Agent API
```

SMOP 面向**对象语义和 Agent 交互**。

## 两者关系

```
Memory Engine V1     = 基础设施（如何存和取）
SMOP V1              = 协议层（存什么和怎么理解）

Memory Engine 实现 SMOP 的存储和检索。
SMOP 定义 Memory Engine 的数据模型和交互协议。
```

## 最终技术栈建议

```
┌──────────────────────────────────────────────┐
│                  Agent Layer                  │
│         (Trae / Codex / Claude)               │
├──────────────────────────────────────────────┤
│               SMOP Protocol                   │
│         (Object + Relation + Context)         │
├──────────────────────────────────────────────┤
│           Sera Memory Runtime                 │
│     (Context Builder + Query Planner)         │
├──────────────────┬───────────────────────────┤
│   Memory Engine  │   MCP Server              │
│   (Store+Index)  │   (Tool Access)           │
├──────────────────┴───────────────────────────┤
│               Storage Layer                   │
│       PostgreSQL + pgvector + Apache AGE      │
│           (或 SQLite + LanceDB V1)            │
└──────────────────────────────────────────────┘
```

---

# 附录 A: SMOP 与 Memory Graph Schema 的字段映射

| Memory Graph Schema | SMOP Object | 说明 |
|--------------------|-------------|------|
| Entity Identity | id | 统一 ID 命名空间 |
| Entity Type | type | 标准类型枚举 |
| Attributes | properties | 属性包 |
| Relations | relations | 关系数组 |
| History | events | 事件记录 |
| Memory | 不直接映射 | 由 Context Package 编译 |
| Actions | 不直接映射 | 由 MCP 处理 |

# 附录 B: SMOP 与 Memory Engine 的交互协议

```
Memory Engine 实现 SMOP 的存储后端：

smop/object/{id}      →  memory_engine.get_entity(id)
smop/search           →  memory_engine.hybrid_search(query, filters)
smop/traverse         →  memory_engine.graph_traverse(start, relation, depth)
smop/context/build    →  memory_engine.build_context(agent, task)
smop/learn            →  memory_engine.store_experience(data)
smop/decision         →  memory_engine.store_decision(data)
```

# 附录 C: 版本演化策略

```
SMOP V1 (当前)
  - 12 种 Entity 类型
  - 16 种标准关系类型
  - Context Package 协议
  - 基础 Agent API

SMOP V1.1 (计划)
  - 增加 Batch 操作
  - 增加订阅/通知机制
  - 增加 Object 版本历史

SMOP V2.0 (未来)
  - 支持自定义 Entity 类型
  - 支持动态关系类型
  - 多 Agent 协作协议
  - 跨 Sera 实例联邦协议
```

---

*Document Version: 1.0*
*Last Updated: 2026-08-21*
*Next: Sera Organization OS V1*