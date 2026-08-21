# Sera OPC OS Runtime MVP V1 Engineering Specification

## 从蓝图到代码 — 可运行的第一版

| Field | Value |
|-------|-------|
| Version | 1.0 |
| Status | Engineering Spec |
| Stack | Python + FastAPI + SQLite/PostgreSQL + Redis |
| Timeline | 8 周 → 4 Phase |

---

# 一、MVP 范围

## 核心原则

```
不做: 完美系统
做: 可运行的闭环

不做: 全部 8.5 层
做: 核心路径: Mission → Agent → Task → Output

不做: 所有 Agent
做: 3 个核心 Agent: CEO / CPO / CRO
```

## MVP 交付物

```yaml
mvp_deliverables:
  - "Mission Engine: 接收自然语言 → 生成 Mission"
  - "Agent Registry: 3 个 Agent 定义 + 实例管理"
  - "Orchestrator: 简单 Task DAG + 分配"
  - "Workflow Engine: 顺序执行 + 状态管理"
  - "Memory Engine: 项目记忆 (SQLite)"
  - "Event Bus: 内存事件系统"
  - "API: REST API (7 个端点)"
  - "Console: CEO 仪表盘 (HTML)"
  - "Demo: 牛牛 AI 推广流程"
```

---

# 二、技术栈

```yaml
tech_stack:
  language: "Python 3.12+"
  web_framework: "FastAPI"
  database: "SQLite (dev) / PostgreSQL (prod)"
  cache: "Redis (memory engine)"
  vector_search: "pgvector (prod phase)"
  event_bus: "Redis Pub/Sub + 内存 Fallback"
  agent_runtime: "asyncio + subprocess"
  llm_clients: "OpenAI / Anthropic / DeepSeek SDK"
  frontend: "HTML/CSS/JS (CEO Console)"
  deployment: "Docker Compose"
```

---

# 三、MVP 目录结构

```
runtime/mvp/
├── README.md
├── docker-compose.yml
├── requirements.txt
│
├── core/
│   ├── __init__.py
│   ├── config.py                    # 配置管理
│   ├── models.py                    # 数据模型 (Pydantic)
│   ├── database.py                  # 数据库连接
│   └── exceptions.py                # 异常定义
│
├── mission-engine/
│   ├── __init__.py
│   ├── parser.py                    # 意图解析器
│   ├── generator.py                 # Mission 生成器
│   └── schemas.py                   # Mission Schema
│
├── agent-runtime/
│   ├── __init__.py
│   ├── registry.py                  # Agent 注册表
│   ├── instance.py                  # Agent 实例管理
│   ├── executor.py                  # Agent 执行器
│   └── agents/                      # 预定义 Agent
│       ├── ceo-agent.py
│       ├── cpo-agent.py
│       └── cro-agent.py
│
├── orchestration/
│   ├── __init__.py
│   ├── scheduler.py                 # 任务调度器
│   ├── dag.py                       # Task DAG 构建
│   └── matcher.py                   # Agent 匹配器
│
├── workflow-engine/
│   ├── __init__.py
│   ├── engine.py                    # 工作流引擎
│   ├── steps.py                     # 步骤定义
│   └── state.py                     # 状态管理
│
├── memory-engine/
│   ├── __init__.py
│   ├── working.py                   # 短期记忆
│   ├── project.py                   # 项目记忆
│   └── store.py                     # 存储层
│
├── event-bus/
│   ├── __init__.py
│   ├── bus.py                       # 事件总线
│   └── types.py                     # 事件类型
│
├── model-router/
│   ├── __init__.py
│   ├── router.py                    # 路由规则
│   └── clients.py                   # LLM 客户端
│
├── api/
│   ├── __init__.py
│   ├── app.py                       # FastAPI 应用
│   ├── routes/
│   │   ├── missions.py
│   │   ├── agents.py
│   │   ├── workflows.py
│   │   ├── memory.py
│   │   └── dashboard.py
│   └── middleware/
│       ├── auth.py
│       └── logging.py
│
├── dashboard/
│   └── index.html                   # CEO Console
│
├── tests/
│   ├── test_mission_engine.py
│   ├── test_agent_runtime.py
│   ├── test_orchestrator.py
│   └── test_workflow.py
│
└── scripts/
    ├── seed.py                      # 种子数据
    └── demo.py                      # 演示脚本
```

---

# 四、核心数据模型 (Pydantic)

```python
# core/models.py

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime

class MissionStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"

class Mission(BaseModel):
    id: str
    raw_input: str
    intent: Dict[str, Any]
    constraints: Optional[Dict[str, Any]] = None
    success_criteria: List[str] = []
    status: MissionStatus = MissionStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class AgentStatus(str, Enum):
    IDLE = "idle"
    ASSIGNED = "assigned"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"

class AgentInstance(BaseModel):
    id: str
    agent_id: str
    project_id: Optional[str] = None
    status: AgentStatus = AgentStatus.IDLE
    context: Dict[str, Any] = {}
    tools: List[str] = []
    permissions: List[str] = []
    metrics: Dict[str, float] = {}
    started_at: Optional[datetime] = None
    last_active: Optional[datetime] = None

class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"

class Task(BaseModel):
    id: str
    mission_id: str
    workflow_id: Optional[str] = None
    name: str
    assigned_to: Optional[str] = None
    depends_on: List[str] = []
    status: TaskStatus = TaskStatus.PENDING
    input: Dict[str, Any] = {}
    output: Optional[Dict[str, Any]] = None
    priority: int = 0
    estimated_minutes: int = 60
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class Workflow(BaseModel):
    id: str
    mission_id: str
    name: str
    steps: List[Dict[str, Any]]
    status: str = "draft"
    created_at: datetime = Field(default_factory=datetime.now)
```

---

# 五、API 端点定义

```python
# api/routes/missions.py

from fastapi import APIRouter, HTTPException
from core.models import Mission, MissionStatus
from mission_engine.parser import IntentParser
from mission_engine.generator import MissionGenerator

router = APIRouter(prefix="/api/v1/missions", tags=["missions"])

@router.post("/")
async def create_mission(input: str, context: dict = None):
    """
    创建 Mission
    输入: "推广牛牛 AI"
    输出: Mission Object
    """
    parser = IntentParser()
    intent = parser.parse(input)
    generator = MissionGenerator()
    mission = generator.generate(intent, context)
    return mission

@router.get("/{mission_id}")
async def get_mission(mission_id: str):
    """获取 Mission 详情"""
    mission = await db.get_mission(mission_id)
    if not mission:
        raise HTTPException(404, "Mission not found")
    return mission

@router.get("/")
async def list_missions(status: str = None, limit: int = 20, offset: int = 0):
    """Mission 列表"""
    return await db.list_missions(status, limit, offset)
```

```python
# api/routes/agents.py

@router.post("/{agent_id}/assign")
async def assign_task(agent_id: str, task: dict):
    """分配任务给 Agent"""
    instance = await AgentManager.assign(agent_id, task)
    return instance

@router.post("/{agent_id}/execute")
async def execute_task(agent_id: str, action: str, params: dict):
    """Agent 执行任务"""
    result = await AgentExecutor.execute(agent_id, action, params)
    return result

@router.get("/registry")
async def list_registry():
    """Agent 注册表"""
    return await AgentRegistry.list_all()
```

```python
# api/routes/workflows.py

@router.post("/")
async def create_workflow(mission_id: str, steps: list):
    """创建 Workflow"""
    workflow = await WorkflowEngine.create(mission_id, steps)
    return workflow

@router.post("/{workflow_id}/trigger")
async def trigger_workflow(workflow_id: str):
    """触发 Workflow 执行"""
    result = await WorkflowEngine.execute(workflow_id)
    return result

@router.get("/{workflow_id}/status")
async def get_workflow_status(workflow_id: str):
    """获取 Workflow 状态"""
    return await WorkflowEngine.get_status(workflow_id)
```

---

# 六、Mission Engine 实现

```python
# mission_engine/parser.py

import re
from typing import Dict, Any

class IntentParser:
    """意图解析器 — 把人类语言转化为结构化 Intent"""

    def __init__(self):
        self.patterns = {
            "promote": r"(推广|宣传|营销|推|promote|market|launch)",
            "build": r"(开发|构建|做|创建|build|create|develop|make)",
            "research": r"(研究|调研|分析|research|analyze|study)",
            "sell": r"(卖|销售|sell|sale|pitch)",
            "improve": r"(优化|改进|改善|提升|improve|optimize|enhance)",
        }

        self.subject_patterns = [
            r"(牛牛 AI|niuniu|nn ai)",
            r"(prop.?firm|propfirm)",
            r"(trading|交易)",
            r"(网站|网站|landing page|landing)",
            r"(内容|content|文章|article)",
        ]

    def parse(self, input_text: str) -> Dict[str, Any]:
        """解析输入文本"""
        text = input_text.lower().strip()

        # 提取意图
        intent = self._extract_intent(text)

        # 提取主体
        subject = self._extract_subject(text)

        # 提取约束
        constraints = self._extract_constraints(text)

        # 提取时间
        deadline = self._extract_deadline(text)

        return {
            "action": intent,
            "subject": subject,
            "constraints": constraints,
            "deadline": deadline,
            "confidence": self._calculate_confidence(text, intent),
            "raw_input": input_text,
        }

    def _extract_intent(self, text: str) -> str:
        for intent, pattern in self.patterns.items():
            if re.search(pattern, text):
                return intent
        return "unknown"

    def _extract_subject(self, text: str) -> str:
        for pattern in self.subject_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        return "unknown"

    def _extract_constraints(self, text: str) -> Dict[str, Any]:
        constraints = {}
        # 提取预算
        budget_match = re.search(r"(\d+)\s*美元|budget[:\s]*\$?(\d+)", text)
        if budget_match:
            constraints["budget"] = int(budget_match.group(1) or budget_match.group(2))
        # 提取目标
        target_match = re.search(r"(\d+)\s*(个|客户|用户|customers?|users?)", text)
        if target_match:
            constraints["target_customers"] = int(target_match.group(1))
        return constraints

    def _extract_deadline(self, text: str) -> str:
        # 简单实现
        import datetime
        if "今天" in text or "today" in text:
            return datetime.date.today().isoformat()
        if "明天" in text or "tomorrow" in text:
            return (datetime.date.today() + datetime.timedelta(days=1)).isoformat()
        if "30天" in text or "30 days" in text or "一个月" in text:
            return (datetime.date.today() + datetime.timedelta(days=30)).isoformat()
        return ""

    def _calculate_confidence(self, text: str, intent: str) -> float:
        if intent == "unknown":
            return 0.3
        # 越长的输入通常信息越丰富
        base = min(len(text) / 20, 0.8)
        return min(base + 0.15, 0.95)
```

---

# 七、Agent Runtime 实现

```python
# agent_runtime/executor.py

import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
from core.models import AgentInstance, AgentStatus, Task

class AgentExecutor:
    """Agent 执行器 — 运行 Agent 完成任务"""

    def __init__(self):
        self.active_instances: Dict[str, AgentInstance] = {}
        self._llm_clients = self._init_clients()

    async def execute(self, agent_id: str, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """执行 Agent 任务"""
        instance = self.active_instances.get(agent_id)
        if not instance:
            raise ValueError(f"Agent {agent_id} not active")

        instance.status = AgentStatus.ACTIVE
        instance.last_active = datetime.now()

        try:
            # 1. 加载 Agent 上下文
            context = await self._load_context(instance)

            # 2. 选择模型
            model = await self._route_model(instance, action)

            # 3. 构建 Prompt
            prompt = self._build_prompt(instance, action, params, context)

            # 4. 调用 LLM
            response = await self._call_llm(model, prompt)

            # 5. 解析输出
            result = self._parse_output(response)

            # 6. 更新记忆
            await self._update_memory(instance, action, result)

            # 7. 记录指标
            self._record_metrics(instance, action)

            instance.status = AgentStatus.COMPLETED
            return result

        except Exception as e:
            instance.status = AgentStatus.FAILED
            raise

    async def _load_context(self, instance: AgentInstance) -> Dict[str, Any]:
        """加载 Agent 上下文 — 从 Memory Engine"""
        from memory_engine.project import ProjectMemory
        project_memory = ProjectMemory(instance.project_id)
        return await project_memory.get_context(instance.agent_id)

    async def _route_model(self, instance: AgentInstance, action: str) -> str:
        """路由模型 — 从 Model Router"""
        from model_router.router import ModelRouter
        return await ModelRouter.route(instance.agent_id, action)

    def _build_prompt(self, instance: AgentInstance, action: str, params: Dict, context: Dict) -> str:
        """构建 Agent Prompt"""
        system = f"你是 {instance.agent_id}，角色是 {instance.context.get('role', 'AI Agent')}。"
        system += f"当前项目: {instance.project_id}。\n"
        system += f"上下文: {context.get('summary', '')}"

        user = f"任务: {action}\n"
        user += f"参数: {params}\n"
        return system + "\n\n" + user
```

---

# 八、Workflow Engine 实现

```python
# workflow_engine/engine.py

import asyncio
from typing import Dict, Any, List
from datetime import datetime
from core.models import Task, TaskStatus, Workflow

class WorkflowEngine:
    """工作流引擎 — 执行 Task DAG"""

    def __init__(self):
        self.active_workflows: Dict[str, Workflow] = {}
        self.task_results: Dict[str, Dict[str, Any]] = {}

    async def create(self, mission_id: str, steps: List[Dict[str, Any]]) -> Workflow:
        """创建 Workflow"""
        workflow = Workflow(
            id=f"WF-{datetime.now().strftime('%Y%m%d')}-{len(self.active_workflows) + 1:03d}",
            mission_id=mission_id,
            name=f"Workflow for {mission_id}",
            steps=steps,
            status="draft",
        )
        self.active_workflows[workflow.id] = workflow
        return workflow

    async def execute(self, workflow_id: str) -> Dict[str, Any]:
        """执行 Workflow"""
        workflow = self.active_workflows.get(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")

        workflow.status = "running"
        results = {}

        # 拓扑排序并执行
        sorted_steps = self._topological_sort(workflow.steps)

        for step in sorted_steps:
            step_id = step["id"]
            depends_on = step.get("depends_on", [])

            # 等待依赖完成
            for dep_id in depends_on:
                while dep_id not in self.task_results:
                    await asyncio.sleep(1)

            # 执行步骤
            try:
                result = await self._execute_step(step)
                self.task_results[step_id] = result
                results[step_id] = result
            except Exception as e:
                workflow.status = "failed"
                raise

        workflow.status = "completed"
        return results

    async def _execute_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """执行单个步骤"""
        step_type = step.get("type", "agent_task")

        if step_type == "agent_task":
            from agent_runtime.executor import AgentExecutor
            executor = AgentExecutor()
            return await executor.execute(
                step["agent"],
                step.get("action", "execute"),
                step.get("input", {}),
            )

        elif step_type == "human_approval":
            # 等待人类审批
            return await self._wait_for_approval(step)

        elif step_type == "parallel":
            # 并行执行
            branches = step.get("branches", [])
            tasks = [self._execute_step(branch) for branch in branches]
            return await asyncio.gather(*tasks)

        return {"status": "unknown_step_type"}

    def _topological_sort(self, steps: List[Dict]) -> List[Dict]:
        """拓扑排序"""
        visited = set()
        result = []

        def dfs(step_id):
            if step_id in visited:
                return
            visited.add(step_id)
            step = next(s for s in steps if s["id"] == step_id)
            for dep_id in step.get("depends_on", []):
                dfs(dep_id)
            result.append(step)

        all_ids = [s["id"] for s in steps]
        for sid in all_ids:
            dfs(sid)

        return result
```

---

# 九、部署配置

## Docker Compose

```yaml
# docker-compose.yml
version: "3.8"

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///data/sera.db
      - REDIS_URL=redis://redis:6379
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY}
    volumes:
      - ./data:/app/data
    depends_on:
      - redis

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  dashboard:
    image: nginx:alpine
    ports:
      - "8080:80"
    volumes:
      - ./dashboard:/usr/share/nginx/html
```

## requirements.txt

```
fastapi==0.115.0
uvicorn==0.30.0
pydantic==2.9.0
sqlalchemy==2.0.35
aiosqlite==0.20.0
redis==5.1.0
httpx==0.27.0
openai==1.50.0
anthropic==0.40.0
python-dotenv==1.0.1
```

---

# 十、演示流程

## 牛牛 AI 推广 Demo

```python
# scripts/demo.py

async def demo_niuniu_ai_launch():
    """演示: 从 Sarah 一句话到完整公司执行"""

    # Step 1: Sarah 输入
    mission = await api.create_mission(
        input="推广牛牛 AI，30天内获得100个客户，预算$800"
    )
    print(f"✅ Mission created: {mission.id}")

    # Step 2: 解析意图
    print(f"   意图: {mission.intent['action']}")
    print(f"   主体: {mission.intent['subject']}")
    print(f"   约束: {mission.constraints}")

    # Step 3: CEO Agent 审批
    approval = await ceo_agent.approve(mission)
    print(f"✅ CEO Agent approved: {approval.status}")

    # Step 4: Orchestrator 拆解任务
    tasks = await orchestrator.decompose(mission)
    print(f"✅ Tasks created: {len(tasks)} tasks")

    for task in tasks:
        print(f"   - {task.name} → {task.assigned_to}")

    # Step 5: Workflow 执行
    workflow = await workflow_engine.create(mission.id, tasks)
    results = await workflow_engine.execute(workflow.id)
    print(f"✅ Workflow completed: {len(results)} steps")

    # Step 6: Revenue Engine 启动
    revenue = await revenue_engine.start(mission.id)
    print(f"✅ Revenue Engine started: {revenue.status}")

    # Step 7: 结果
    print(f"\n📊 Demo Complete")
    print(f"   项目: 牛牛 AI 推广")
    print(f"   时间线: 30 天")
    print(f"   目标: 100 个客户")
    print(f"   预算: $800")
```

---

# 十一、MVP 验收标准

```yaml
acceptance_criteria:
  p0_must_have:
    - "✅ 接收自然语言输入 → 生成 Mission"
    - "✅ Mission → Task DAG → Agent 分配"
    - "✅ Agent 执行任务并返回结果"
    - "✅ Workflow 管理 (顺序/并行)"
    - "✅ 数据持久化 (SQLite)"
    - "✅ CEO Console 显示状态"

  p1_should_have:
    - "🔄 记忆系统 (项目记忆)"
    - "🔄 事件总线 (模块间通信)"
    - "🔄 基础权限 (Agent 隔离)"
    - "🔄 错误处理 + 重试"

  p2_nice_to_have:
    - "🔧 Model Router (多模型)"
    - "🔧 Evaluation Engine (评分)"
    - "🔧 Learning OS 集成"
```

---

# 十二、MVP 实施路线图

```yaml
mvp_roadmap:
  week_1:
    - "搭建 FastAPI 项目骨架"
    - "实现 Mission Engine (Parser + Generator)"
    - "实现 Agent Registry + Instance Manager"
    - "数据库 Schema + Migration"
    milestone: "能创建 Mission"

  week_2:
    - "实现 Orchestrator (Task DAG + 分配)"
    - "实现 Workflow Engine (顺序执行)"
    - "实现 3 个核心 Agent (CEO/CPO/CRO)"
    - "编写单元测试"
    milestone: "Mission → Task → Agent 执行"

  week_3:
    - "实现 Memory Engine (项目记忆)"
    - "实现 Event Bus (内存版)"
    - "实现 Model Router (基础路由)"
    - "CEO Console 集成"
    milestone: "完整 API + 仪表盘"

  week_4:
    - "牛牛 AI Demo 完整流程"
    - "错误处理 + 重试机制"
    - "Docker Compose 部署"
    - "文档 + 演示视频"
    milestone: "MVP V1 可运行"
```