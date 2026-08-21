# Sera OPC OS Runtime Architecture V1.0

## AI 公司执行内核 — 从蓝图到可运行的系统

| Field | Value |
|-------|-------|
| Version | 1.0 |
| Status | Engineering Specification |
| Owner | CTO (SERA-CTO-001) |
| Analogy | Linux Kernel + K8s Scheduler + Temporal Workflow |

---

# 目录

1. [Runtime 定位](#一runtime-定位)
2. [总架构](#二总架构)
3. [Mission Engine](#三mission-engine)
4. [Agent Runtime](#四agent-runtime)
5. [Orchestration Engine](#五orchestration-engine)
6. [Workflow Engine](#六workflow-engine)
7. [Memory Engine](#七memory-engine)
8. [Event Bus](#八event-bus)
9. [Model Router](#九model-router)
10. [Evaluation Engine](#十evaluation-engine)
11. [Security & Permission](#十一security--permission)
12. [Dashboard & Monitoring](#十二dashboard--monitoring)
13. [完整执行流程](#十三完整执行流程)
14. [API 设计](#十四api-设计)
15. [数据库 Schema](#十五数据库-schema)
16. [Repository Structure](#十六repository-structure)
17. [Implementation Roadmap](#十七implementation-roadmap)

---

# 一、Runtime 定位

## 为什么需要 Runtime

前面 8.5 层设计解决的是"公司应该长什么样"。Runtime 解决的是"公司怎么运行"。

| 对比 | 蓝图层 | Runtime 层 |
|------|--------|-----------|
| 类比 | 公司组织架构图 | 公司 ERP 系统 |
| 状态 | 静态定义 | 动态运行 |
| 输入 | 设计文档 | Sarah 的一句话 |
| 输出 | 概念设计 | 可执行的任务 |
| 核心 | 定义 | 调度 |

## Runtime 的角色

```
Human Founder (Sarah)
        │ 一句话
        ▼
┌─────────────────────────────────────────────┐
│           Runtime Kernel                     │
│                                             │
│  Mission Engine  ─►  Orchestration          │
│       │                  │                  │
│  Agent Runtime     Workflow Engine          │
│       │                  │                  │
│  Memory Engine     Event Bus                │
│       │                  │                  │
│  Model Router      Evaluation Engine        │
│       │                  │                  │
│  Security Layer    Dashboard                │
└──────────────────────┬──────────────────────┘
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
     Intelligence   Commercial   Factories
        OS            OS            OS
```

---

# 二、总架构

## 系统分层

```
┌─────────────────────────────────────────────────────────────┐
│                      API Layer (HTTP/WS)                     │
│            REST API  │  WebSocket  │  CLI  │  Console        │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────┴─────────────────────────────────┐
│                    Orchestration Layer                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ Mission      │  │ Orchestrator │  │ Workflow Engine  │  │
│  │ Engine       │  │ (Scheduler)  │  │ (DAG Runner)     │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────┴─────────────────────────────────┐
│                    Execution Layer                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ Agent        │  │ Tool         │  │ Model            │  │
│  │ Runtime      │  │ Runtime      │  │ Router           │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────┴─────────────────────────────────┐
│                    Infrastructure Layer                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ Event Bus    │  │ Memory       │  │ Evaluation       │  │
│  │ (Message)    │  │ Engine       │  │ Engine           │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
│  ┌──────────────┐  ┌──────────────┐                          │
│  │ Security     │  │ Monitoring   │                          │
│  │ Layer        │  │ & Logging    │                          │
│  └──────────────┘  └──────────────┘                          │
└─────────────────────────────────────────────────────────────┘
```

## 核心数据流

```
Sarah: "推广牛牛 AI"
  │
  ▼
API Layer → POST /api/v1/missions
  │
  ▼
Mission Engine → 解析意图 → 生成 Mission Object
  │
  ▼
Orchestrator → 拆解任务 → 创建 Execution Graph
  │
  ├─ Task 1: Market Research → 分配 Market Agent
  ├─ Task 2: Landing Page   → 分配 Design Agent
  ├─ Task 3: Sales Copy     → 分配 Content Agent
  └─ Task 4: Launch         → 分配 Sales Agent
  │
  ▼
Agent Runtime → 每个 Agent 独立执行
  │
  ├─ Agent 调用 Tool → Model Router → LLM
  ├─ Agent 读写 Memory → Memory Engine
  └─ Agent 发送事件 → Event Bus
  │
  ▼
Evaluation Engine → 评分 → Learning OS
```

---

# 三、Mission Engine

## 定位

公司的"意图解析器"。把人类语言转化为可执行的 Mission Object。

## 架构

```
Human Input: "帮我推广牛牛 AI"
  │
  ▼
┌────────────────────────────────────────────┐
│            Intent Parser                     │
│  ├─ 实体提取: NiuNiu AI, 推广               │
│  ├─ 意图分类: commercial_launch              │
│  ├─ 优先级判定: P0 (has deadline)            │
│  └─ 约束提取: 30 days, budget $800          │
└──────────────────┬─────────────────────────┘
                   ▼
┌────────────────────────────────────────────┐
│          Mission Generator                   │
│  ├─ 生成 Mission ID                         │
│  ├─ 关联已存在的项目/Agent                  │
│  ├─ 设置 Success Criteria                   │
│  └─ 输出 Mission Object                     │
└──────────────────┬─────────────────────────┘
                   ▼
┌────────────────────────────────────────────┐
│          Strategy Alignment                  │
│  ├─ 检查当前 OKR 对齐                       │
│  ├─ 冲突检测                                │
│  ├─ 资源预估                                │
│  └─ 输出优先级                              │
└──────────────────┬─────────────────────────┘
                   ▼
              Mission Object → Orchestrator
```

## Mission Object Schema

```yaml
mission:
  id: "MIS-20260821-001"
  source: "human_sarah"
  raw_input: "帮我推广牛牛 AI"

  intent:
    action: "promote"
    subject: "niuniu_ai"
    category: "commercial_launch"
    priority: "P0"
    confidence: 0.95

  constraints:
    deadline: "2026-09-20"
    budget: 800
    quality: "production"

  success_criteria:
    - "100 paying customers"
    - "website conversion rate > 5%"
    - "customer activation > 80%"

  strategy:
    aligned_okr: "OKR-2026Q3-001"
    resource_estimate:
      agents: 5
      api_tokens: 50000
      duration_days: 30

  status: "pending"  # pending | approved | executing | completed | failed
  created_at: "2026-08-21T10:00:00Z"
```

## API

```yaml
POST /api/v1/missions
  request:
    input: string          # 人类语言输入
    context: object|null   # 可选上下文
  response:
    mission: MissionObject
    suggestions: string[]  # 建议的下一步

GET /api/v1/missions/:id
  response: MissionObject

GET /api/v1/missions
  query: { status, limit, offset }
  response: MissionObject[]
```

---

# 四、Agent Runtime

## 定位

AI 员工的运行环境。每个 Agent 是一个独立的执行单元。

## Agent 实例生命周期

```
Created → Idle → Assigned → Active → Completed / Failed
                              │
                         Paused (需人工介入)
```

## Agent Instance Schema

```yaml
agent_instance:
  id: "SERA-CPO-001-NIUNIU"
  agent_id: "SERA-CPO-001"
  project_id: "PRJ-20260821-001"
  status: "active"  # idle | assigned | active | paused | completed | failed

  identity:
    role: "Product Manager"
    department: "Product"
    level: "L3"

  context:
    project: "niuniu-ai"
    mission_id: "MIS-20260821-001"
    current_task: "define_product_positioning"

  memory:
    working: "当前任务上下文"
    project: "project-memory://niuniu-ai"
    organization: "company-memory://product"

  tools:
    - "github"
    - "figma"
    - "browser"
    - "claude"

  permissions:
    level: "manager"
    allowed_actions: ["read_project", "write_doc", "assign_task"]
    denied_actions: ["delete_asset", "modify_pricing"]

  metrics:
    tasks_completed: 12
    avg_quality: 0.88
    total_tokens: 45000

  started_at: "2026-08-21T10:05:00Z"
  last_active: "2026-08-21T14:30:00Z"
```

## Agent Runtime 接口

```yaml
# Agent Runtime API
POST /api/v1/agents/:id/assign
  request: { task: TaskObject }
  response: { instance: AgentInstance }

POST /api/v1/agents/:id/execute
  request: { action: string, params: object }
  response: { result: any, tokens_used: int }

POST /api/v1/agents/:id/pause
  response: { status: "paused" }

POST /api/v1/agents/:id/resume
  response: { status: "active" }

GET /api/v1/agents/:id/status
  response: AgentInstance

# Agent Registry
GET /api/v1/agents/registry
  response: AgentDefinition[]

POST /api/v1/agents/registry
  request: AgentDefinition
  response: { id: string }
```

---

# 五、Orchestration Engine

## 定位

公司的任务调度中心。类似 Kubernetes Scheduler。

## 调度算法

```yaml
orchestration:
  input:
    - mission: MissionObject
    - available_agents: AgentInstance[]
    - resource_pool: ResourcePool

  algorithm:
    step_1: "分解 Mission 为 Task DAG"
    step_2: "为每个 Task 匹配最优 Agent"
    step_3: "检查依赖关系 (拓扑排序)"
    step_4: "分配资源 (Token/Budget)"
    step_5: "提交 Task 到 Workflow Engine"
    step_6: "监控执行状态"

  matching_rules:
    skill_match: 0.4
    availability: 0.3
    performance: 0.2
    learning_opportunity: 0.1
```

## Task DAG 示例

```yaml
tasks:
  - id: "TASK-001"
    name: "Market Research"
    depends_on: []
    assigned_to: "SERA-CSO-001"
    estimated_hours: 4
    priority: 1

  - id: "TASK-002"
    name: "Product Positioning"
    depends_on: ["TASK-001"]
    assigned_to: "SERA-CPO-001"
    estimated_hours: 3
    priority: 1

  - id: "TASK-003"
    name: "Website Design"
    depends_on: ["TASK-002"]
    assigned_to: "SERA-UID-001"
    estimated_hours: 8
    priority: 2

  - id: "TASK-004"
    name: "Sales Copy"
    depends_on: ["TASK-002"]
    assigned_to: "SERA-PMA-001"
    estimated_hours: 4
    priority: 2

  - id: "TASK-005"
    name: "Launch Campaign"
    depends_on: ["TASK-003", "TASK-004"]
    assigned_to: "SERA-CRO-001"
    estimated_hours: 2
    priority: 1
```

---

# 六、Workflow Engine

## 定位

公司的流程执行引擎。类似 Temporal / Airflow。

## 支持的工作流模式

```yaml
workflow_patterns:
  sequential:
    - "Step 1 → Step 2 → Step 3"
    - "每个步骤必须完成才能继续"

  parallel:
    - "Step 1 → [Step 2a, Step 2b, Step 2c] → Step 3"
    - "多个步骤可以同时执行"

  conditional:
    - "如果 X → 走分支 A; 否则 → 走分支 B"
    - "基于条件动态路由"

  loop:
    - "重复执行直到满足条件"
    - "用于实验和优化"

  human_approval:
    - "执行到某步 → 等待人类审批 → 继续"
    - "关键决策点需要 CEO 确认"
```

## Workflow Definition Schema

```yaml
workflow:
  id: "WF-20260821-001"
  name: "product-launch"
  mission_id: "MIS-20260821-001"

  steps:
    - id: "step-1"
      name: "Market Research"
      type: "agent_task"
      agent: "SERA-CSO-001"
      input: { product: "niuniu_ai" }
      timeout_minutes: 120

    - id: "step-2"
      name: "CEO Approval"
      type: "human_approval"
      approver: "sarah"
      input: { step_id: "step-1" }
      timeout_hours: 24

    - id: "step-3"
      name: "Parallel Production"
      type: "parallel"
      branches:
        - id: "step-3a"
          name: "Website Design"
          agent: "SERA-UID-001"
        - id: "step-3b"
          name: "Sales Content"
          agent: "SERA-PMA-001"

    - id: "step-4"
      name: "Launch"
      type: "agent_task"
      agent: "SERA-CRO-001"
      depends_on: ["step-3a", "step-3b"]

  status: "running"
  created_at: "2026-08-21T10:00:00Z"
```

---

# 七、Memory Engine

## 定位

公司的记忆系统。连接 Learning OS 和所有 Agent。

## 三层记忆架构

```yaml
memory_layers:
  working_memory:
    type: "short_term"
    storage: "in-memory (Redis)"
    ttl: "24 hours"
    content: "当前任务上下文、对话历史"
    access: "当前 Agent 读写"

  project_memory:
    type: "medium_term"
    storage: "vector DB (pgvector)"
    ttl: "项目生命周期"
    content: "项目文档、决策、代码、设计"
    access: "项目成员读写"

  organization_memory:
    type: "long_term"
    storage: "vector DB + Object Store"
    ttl: "永久"
    content: "公司知识、经验、失败记录、benchmark"
    access: "所有 Agent 读, 特定 Agent 写"
```

## Memory 操作 API

```yaml
POST /api/v1/memory/write
  request:
    layer: "working | project | organization"
    key: string
    value: any
    metadata: { tags: string[], ttl: int|null }
  response: { id: string }

POST /api/v1/memory/read
  request:
    layer: string
    query: string       # 语义搜索
    filters: object|null
    limit: int
  response: { results: MemoryItem[], score: float }

POST /api/v1/memory/forget
  request:
    layer: string
    id: string
  response: { status: "deleted" }
```

---

# 八、Event Bus

## 定位

公司的神经系统。所有模块通过事件通信。

## 事件类型

```yaml
event_types:
  system:
    - "system.boot"
    - "system.shutdown"
    - "system.error"

  mission:
    - "mission.created"
    - "mission.approved"
    - "mission.completed"
    - "mission.failed"

  agent:
    - "agent.assigned"
    - "agent.task_started"
    - "agent.task_completed"
    - "agent.task_failed"
    - "agent.paused"
    - "agent.error"

  project:
    - "project.created"
    - "project.milestone"
    - "project.completed"
    - "project.blocked"

  workflow:
    - "workflow.started"
    - "workflow.step_completed"
    - "workflow.completed"
    - "workflow.failed"

  business:
    - "deal.closed"
    - "deal.lost"
    - "customer.churned"
    - "revenue.milestone"

  intelligence:
    - "signal.critical"
    - "opportunity.identified"
    - "competitor.alert"

  evaluation:
    - "agent.score_updated"
    - "okr.progress"
    - "anomaly.detected"
```

## Event Schema

```yaml
event:
  id: "EVT-20260821-001"
  type: "mission.created"
  source: "human_api"
  timestamp: "2026-08-21T10:00:00Z"

  payload:
    mission_id: "MIS-20260821-001"
    title: "推广牛牛 AI"
    priority: "P0"

  context:
    trace_id: "trace-abc123"
    user_id: "sarah"

  metadata:
    version: 1
    retry_count: 0
```

---

# 九、Model Router

## 定位

AI 算力调度器。为每个任务分配最优模型。

## 路由规则

```yaml
model_routing:
  rules:
    - task_type: "strategic_planning"
      preferred: "claude-sonnet-4"
      fallback: "gpt-5.5"
      max_tokens: 8000
      priority: "quality"

    - task_type: "coding"
      preferred: "claude-code"
      fallback: "deepseek-v3"
      max_tokens: 16000
      priority: "speed"

    - task_type: "content_writing"
      preferred: "gpt-5.5"
      fallback: "claude-sonnet-4"
      max_tokens: 4000
      priority: "quality"

    - task_type: "image_generation"
      preferred: "midjourney-6"
      fallback: "flux-pro"
      max_tokens: 0
      priority: "quality"

    - task_type: "analysis"
      preferred: "deepseek-v3"
      fallback: "claude-haiku"
      max_tokens: 32000
      priority: "cost"

  cost_optimization:
    - "如果 quality 要求 > 90% → 使用顶级模型"
    - "如果 quality 要求 < 70% → 使用低成本模型"
    - "批量任务 → 使用最快模型"
    - "重试 → 使用不同模型 (多样性)"
```

---

# 十、Evaluation Engine

## 定位

员工绩效系统。持续评估每个 Agent 的表现。

## 评分维度

```yaml
evaluation:
  dimensions:
    quality:
      weight: 0.35
      metrics:
        - "output_accuracy"      # 输出准确度
        - "requirement_match"    # 需求匹配度
        - "error_rate"           # 错误率

    speed:
      weight: 0.20
      metrics:
        - "completion_time"      # 完成时间 vs 预估
        - "response_latency"     # 响应延迟

    cost:
      weight: 0.15
      metrics:
        - "token_efficiency"     # Token 使用效率
        - "api_cost_per_task"    # 单任务成本

    impact:
      weight: 0.20
      metrics:
        - "revenue_contribution" # 收入贡献
        - "task_completion_rate" # 任务完成率

    learning:
      weight: 0.10
      metrics:
        - "improvement_rate"     # 改进速度
        - "knowledge_contribution" # 知识贡献
```

---

# 十一、Security & Permission

## 权限层级

```yaml
permission_levels:
  level_0: "human_ceo"
    - 所有权限
    - 可以修改系统配置
    - 可以删除任何数据

  level_1: "executive_agent"
    - 跨部门读权限
    - 本部门写权限
    - 可以创建项目
    - 可以分配任务

  level_2: "manager_agent"
    - 本部门读写权限
    - 可以分配子任务
    - 不可以修改系统配置

  level_3: "worker_agent"
    - 仅任务相关读写
    - 不可以访问其他项目
    - 不可以删除数据

  level_4: "readonly_agent"
    - 仅读取权限
    - 用于审计和分析
```

## 权限检查

```yaml
permission_check:
  before_action:
    - "验证 Agent 身份"
    - "检查 Action 权限"
    - "检查资源访问权限"
    - "记录审计日志"

  sensitive_actions:
    - "delete_*": "需要 Level 0 或 Level 1"
    - "modify_pricing": "需要 Level 0"
    - "deploy_production": "需要 Level 1"
    - "access_customer_data": "需要 Level 2"
    - "modify_system_config": "需要 Level 0"
```

---

# 十二、Dashboard & Monitoring

## Dashboard Schema

```yaml
dashboard:
  company_overview:
    status: "running"
    autonomy_level: "L2"
    active_missions: 2
    active_agents: 12
    pending_approvals: 2

  metrics:
    revenue_mrr: 2900
    total_customers: 102
    avg_response_time_ms: 450
    system_uptime: 0.997

  alerts:
    - level: "warning"
      message: "FTMO launched competing AI features"
      action: "expedite niuniu ai launch"
    - level: "info"
      message: "3 pending approvals"
      action: "review in console"

  recent_events:
    - "10:30 — Agent CPO-001 completed product positioning"
    - "10:15 — Signal: competitor activity detected"
    - "09:45 — Deal closed: TradeKing Capital ($99)"
```

## Health Check API

```yaml
GET /api/v1/health
  response:
    status: "healthy"
    uptime: "14d 6h 32m"
    components:
      mission_engine: "ok"
      agent_runtime: "ok"
      orchestration: "ok"
      workflow_engine: "ok"
      memory_engine: "ok"
      event_bus: "ok"
      model_router: "ok"
    metrics:
      active_agents: 12
      pending_tasks: 5
      queue_depth: 3
      avg_latency_ms: 450
```

---

# 十三、完整执行流程

## Sarah 说"推广牛牛 AI" → 系统的完整路径

```yaml
execution_flow:
  time_0s:
    system: "API Layer"
    action: "POST /api/v1/missions"
    input: "推广牛牛 AI"
    output: "mission_id: MIS-20260821-001"

  time_1s:
    system: "Mission Engine"
    action: "解析意图"
    output: "Mission Object (intent: promote, subject: niuniu_ai)"

  time_2s:
    system: "Mission Engine"
    action: "策略对齐"
    output: "aligned with OKR-2026Q3-001"

  time_3s:
    system: "CEO Agent"
    action: "审批 (自动, L2)"
    output: "approved"

  time_5s:
    system: "Orchestrator"
    action: "拆解任务"
    output: "Task DAG: 5 tasks, 4 agents"

  time_6s:
    system: "Orchestrator"
    action: "分配 Agent"
    output: "CPO-001, UID-001, PMA-001, CRO-001 assigned"

  time_7s:
    system: "Workflow Engine"
    action: "启动工作流"
    output: "workflow_id: WF-20260821-001"

  time_10s:
    system: "Agent Runtime"
    action: "CPO-001 开始市场研究"
    output: "task in progress"

  time_30m:
    system: "Agent Runtime"
    action: "CPO-001 完成市场研究"
    output: "research report"

  time_31m:
    system: "Workflow Engine"
    action: "触发下一步"
    output: "UID-001 开始设计, PMA-001 开始写文案"

  time_4h:
    system: "Workflow Engine"
    action: "设计 + 文案完成"
    output: "等待 CEO 审批"

  time_4h_1m:
    system: "Human Approval"
    action: "Sarah 审批通过"
    output: "继续执行"

  time_5h:
    system: "Workflow Engine"
    action: "启动上线"
    output: "CRO-001 执行发布"

  time_5h_30m:
    system: "Event Bus"
    action: "发布 product.launched 事件"
    output: "通知所有相关系统"

  time_5h_31m:
    system: "Commercial OS"
    action: "Revenue Engine 启动"
    output: "开始收集客户"

  time_24h:
    system: "Evaluation Engine"
    action: "评估所有 Agent 表现"
    output: "scores → Learning OS"

  time_7d:
    system: "Learning OS"
    action: "分析数据, 生成洞察"
    output: "优化建议 → 系统"
```

---

# 十四、API 设计

## REST API 总览

```yaml
base_url: "/api/v1"

endpoints:
  # Missions
  POST /missions: "创建 Mission"
  GET /missions/:id: "获取 Mission"
  GET /missions: "列表"
  PATCH /missions/:id: "更新状态"

  # Agents
  GET /agents/registry: "Agent 注册表"
  POST /agents/registry: "注册新 Agent"
  GET /agents/:id: "Agent 实例详情"
  POST /agents/:id/assign: "分配任务"
  POST /agents/:id/execute: "执行任务"
  POST /agents/:id/pause: "暂停"
  POST /agents/:id/resume: "恢复"

  # Workflows
  POST /workflows: "创建 Workflow"
  GET /workflows/:id: "获取状态"
  POST /workflows/:id/trigger: "触发执行"
  POST /workflows/:id/cancel: "取消"

  # Memory
  POST /memory/write: "写入记忆"
  POST /memory/read: "读取记忆"
  POST /memory/search: "语义搜索"

  # Events
  POST /events/publish: "发布事件"
  GET /events/subscribe: "订阅事件 (SSE)"

  # Dashboard
  GET /dashboard/overview: "公司概览"
  GET /dashboard/metrics: "指标数据"
  GET /dashboard/alerts: "告警列表"

  # Health
  GET /health: "健康检查"
  GET /health/llm: "LLM 连接检查"
```

---

# 十五、数据库 Schema

## 核心表设计

```sql
-- Missions
CREATE TABLE missions (
  id TEXT PRIMARY KEY,
  raw_input TEXT NOT NULL,
  intent JSONB NOT NULL,
  constraints JSONB,
  success_criteria JSONB,
  status TEXT NOT NULL DEFAULT 'pending',
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Agent Registry
CREATE TABLE agent_registry (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  role TEXT NOT NULL,
  department TEXT NOT NULL,
  level TEXT NOT NULL,
  skills JSONB NOT NULL,
  model_preferences JSONB,
  permissions JSONB NOT NULL,
  status TEXT NOT NULL DEFAULT 'active'
);

-- Agent Instances
CREATE TABLE agent_instances (
  id TEXT PRIMARY KEY,
  agent_id TEXT REFERENCES agent_registry(id),
  project_id TEXT,
  status TEXT NOT NULL DEFAULT 'idle',
  context JSONB,
  metrics JSONB,
  started_at TIMESTAMP,
  last_active TIMESTAMP
);

-- Tasks
CREATE TABLE tasks (
  id TEXT PRIMARY KEY,
  mission_id TEXT REFERENCES missions(id),
  workflow_id TEXT,
  name TEXT NOT NULL,
  assigned_to TEXT REFERENCES agent_instances(id),
  depends_on TEXT[],
  status TEXT NOT NULL DEFAULT 'pending',
  input JSONB,
  output JSONB,
  priority INT DEFAULT 0,
  estimated_minutes INT,
  started_at TIMESTAMP,
  completed_at TIMESTAMP
);

-- Workflows
CREATE TABLE workflows (
  id TEXT PRIMARY KEY,
  mission_id TEXT REFERENCES missions(id),
  name TEXT NOT NULL,
  definition JSONB NOT NULL,
  status TEXT NOT NULL DEFAULT 'draft',
  created_at TIMESTAMP DEFAULT NOW()
);

-- Memory
CREATE TABLE memory_items (
  id TEXT PRIMARY KEY,
  layer TEXT NOT NULL,
  key TEXT NOT NULL,
  value JSONB NOT NULL,
  embedding vector(1536),
  metadata JSONB,
  ttl INT,
  created_at TIMESTAMP DEFAULT NOW(),
  expires_at TIMESTAMP
);

-- Events
CREATE TABLE events (
  id TEXT PRIMARY KEY,
  type TEXT NOT NULL,
  source TEXT NOT NULL,
  payload JSONB NOT NULL,
  context JSONB,
  timestamp TIMESTAMP DEFAULT NOW()
);

-- Evaluations
CREATE TABLE evaluations (
  id TEXT PRIMARY KEY,
  agent_id TEXT REFERENCES agent_instances(id),
  task_id TEXT REFERENCES tasks(id),
  scores JSONB NOT NULL,
  total_score FLOAT NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);
```

---

# 十六、Repository Structure

```
runtime/
├── 01-Runtime-Architecture-Blueprint.md   # 本文档
├── 02-Runtime-MVP-Spec.md                 # MVP 工程规范
│
├── core/                                  # 核心引擎
│   ├── mission-engine/                    # 意图解析器
│   ├── orchestrator/                      # 调度器
│   └── workflow-engine/                   # 流程引擎
│
├── agent-runtime/                         # Agent 运行环境
│   ├── registry/                          # Agent 注册表
│   ├── instance-manager/                  # 实例管理
│   └── executor/                          # 执行器
│
├── memory-engine/                         # 记忆引擎
│   ├── working-memory/                    # 短期记忆
│   ├── project-memory/                    # 项目记忆
│   └── organization-memory/               # 组织记忆
│
├── event-bus/                             # 事件总线
│   ├── producer/                          # 生产者
│   ├── consumer/                          # 消费者
│   └── schemas/                           # 事件 Schema
│
├── model-router/                          # 模型路由
│   ├── router/                            # 路由规则
│   ├── providers/                         # 模型提供者
│   └── cost-optimizer/                    # 成本优化
│
├── evaluation-engine/                     # 评估引擎
│   ├── scorer/                            # 评分器
│   ├── metrics/                           # 指标定义
│   └── reporter/                          # 报告生成
│
├── security/                              # 安全层
│   ├── auth/                              # 认证
│   ├── permissions/                       # 权限
│   └── audit/                             # 审计
│
├── api/                                   # API 层
│   ├── routes/                            # 路由
│   ├── middleware/                        # 中间件
│   └── websocket/                         # WebSocket
│
├── dashboard/                             # 仪表盘
│   ├── backend/                           # 后端
│   └── frontend/                          # 前端 (CEO Console)
│
├── schemas/                               # Schema 定义
│   ├── mission.schema.yaml
│   ├── agent.schema.yaml
│   ├── task.schema.yaml
│   ├── workflow.schema.yaml
│   ├── memory.schema.yaml
│   ├── event.schema.yaml
│   └── evaluation.schema.yaml
│
├── integrations/                          # 集成
│   ├── control-plane-integration.yaml
│   ├── factory-integration.yaml
│   └── learning-os-integration.yaml
│
└── mvp/                                   # MVP 实现
    ├── MVP-ROADMAP.md
    └── phase-1/                           # Phase 1 代码
```

---

# 十七、Implementation Roadmap

## Phase 1: Core Kernel (Week 1-2)

| 模块 | 交付物 | 优先级 |
|------|--------|--------|
| Mission Engine | Intent Parser + Mission Object | P0 |
| Agent Registry | 注册表 + 实例管理 | P0 |
| API Layer | REST API + WebSocket | P0 |
| Database | Schema + Migration | P0 |

**目标**: 能接收 "推广牛牛 AI" → 生成 Mission Object

## Phase 2: Orchestration (Week 3-4)

| 模块 | 交付物 | 优先级 |
|------|--------|--------|
| Orchestrator | Task DAG + Agent 分配 | P0 |
| Workflow Engine | Sequential + Parallel | P0 |
| Event Bus | 基础事件系统 | P0 |

**目标**: Mission → Task DAG → Agent 分配 → 执行

## Phase 3: Memory & Evaluation (Week 5-6)

| 模块 | 交付物 | 优先级 |
|------|--------|--------|
| Memory Engine | 三层记忆 + 语义搜索 | P1 |
| Evaluation Engine | 评分 + 报告 | P1 |
| Model Router | 路由 + 成本优化 | P1 |

**目标**: Agent 有记忆、有评估、有模型路由

## Phase 4: Full Integration (Week 7-8)

| 模块 | 交付物 | 优先级 |
|------|--------|--------|
| Security | 权限 + 审计 | P1 |
| Dashboard | CEO Console 集成 | P1 |
| Integration | 全系统联调 | P0 |

**目标**: 端到端运行: Sarah 一句话 → 公司自动执行 → 收入