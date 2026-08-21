# Sera OPC OS V2.0

## GitHub Repository Specification

Version: 2.0
Status: Engineering Specification
Target: DeepSeek / Trae / Codex Direct Execution

---

## Repository Name

| Field | Value |
|-------|-------|
| **Name** | `sera-opc-os` |
| **GitHub** | `github.com/78tyih/sera-opc-os` |
| **Legacy** | `sera-agent-os` → 保留为 `core-engine` 或 `legacy-agent-kernel` |

---

# 一、Repository 总体结构

```
sera-opc-os/
│
├── README.md
├── LICENSE
├── CHANGELOG.md
│
├──===============================================
├──             公司大脑层 (Company Brain)
├──===============================================
├── constitution/
├── vision/
├── strategy/
│
├──===============================================
├──             组织管理层 (Organization)
├──===============================================
├── organization/
├── executive/
├── departments/
│
├──===============================================
├──             AI 员工层 (AI Workforce)
├──===============================================
├── agents/
├── skills/
├── workflows/
│
├──===============================================
├──             生产制造层 (Factories)
├──===============================================
├── factories/
│
├──===============================================
├──             商业变现层 (Revenue)
├──===============================================
├── revenue/
│
├──===============================================
├──             技术基础设施 (Infrastructure)
├──===============================================
├── core/
├── runtime/
├── router/
├── models/
├── adapters/
│
├──===============================================
├──             学习进化层 (Evolution)
├──===============================================
├── memory/
├── evaluation/
├── evolution/
│
├──===============================================
├──             项目资产 (Portfolio)
├──===============================================
├── portfolio/
│
├──===============================================
├──             文档 (Docs)
├──===============================================
└── docs/
```

---

# 二、constitution（公司宪法）

## 目录结构

```
constitution/
├── README.md
├── company-constitution.md
├── ai-employee-rules.md
├── decision-framework.md
├── ethics.md
└── operating-principles.md
```

## company-constitution.md 规范

定义 Sera OPC OS 为什么存在。

```yaml
company:
  name: Sera AI Company

  mission:
    create:
      - AI leverage
      - human creativity
      - autonomous execution

  principle:
    - outcome_first
    - build_system_not_tasks
    - learn_from_world_class
```

---

# 三、vision（战略愿景）

## 目录结构

```
vision/
├── README.md
├── world-model.md
├── benchmark-library.md
├── roadmap.md
├── market-map.md
└── opportunity-engine.md
```

## benchmark-library.md 规范

每个部门绑定世界级组织：

```yaml
department:
  product:
    benchmark:
      - Apple
      - OpenAI
  engineering:
    benchmark:
      - Google
      - Meta
  operation:
    benchmark:
      - Toyota
  sales:
    benchmark:
      - Salesforce
```

---

# 四、organization（组织系统）

## 目录结构

```
organization/
├── company-map.yaml
├── department-map.yaml
├── reporting-line.yaml
└── responsibility-matrix.md
```

## company-map.yaml 规范

```
CEO
 |
Executive Council
 |
Departments
 |
Agents
```

```yaml
CEO:
  name: Sarah

executive:
  - CSO
  - CTO
  - CPO
  - COO
  - CMO
  - CRO
  - CAIO
```

## 部门定义

```
departments/
├── strategy/
├── product/
├── engineering/
├── design/
├── marketing/
├── sales/
├── operation/
├── finance/
└── ai-research/
```

---

# 五、Executive Agent（高管智能体）

## 目录结构

```
agents/executive/
├── ceo-agent/
├── cso-agent/
├── cpo-agent/
├── cto-agent/
├── coo-agent/
├── cmo-agent/
├── cro-agent/
└── caio-agent/
```

## Agent 标准 Contract（7 文件）

每个 Agent 必须包含：

```
agent-name/
├── identity.yaml      # 身份定义
├── system.md          # 系统提示词
├── mission.md         # 使命与职责
├── skill-map.yaml     # 技能映射
├── workflow.yaml      # 工作流定义
├── memory-policy.yaml # 记忆策略
└── evaluation.yaml    # 评估标准
```

### identity.yaml 规范

```yaml
agent:
  id: SERA-CEO-001
  role: Chief Executive Officer
  reports_to: Human CEO
  personality:
    - strategic
    - decisive
    - long_term
```

### mission.md 规范

```markdown
# Mission

## Objective
[一句话使命]

## Responsibilities
- [职责 1]
- [职责 2]

## Decision Rights
- [决策权 1]

## Forbidden Actions
- [禁止事项 1]

## Output Format
[预期输出格式]
```

---

# 六、Factories（生产工厂 — 核心）

## 目录结构

```
factories/
├── research-factory/
├── product-factory/
├── design-factory/
├── engineering-factory/
├── marketing-factory/
├── content-factory/
├── sales-factory/
└── growth-factory/
```

## 工厂标准结构

每个工厂：

```
factory-name/
├── agents/          # 工厂内部 Agent
├── workflows/       # 生产流水线
├── templates/       # 输出模板
├── quality/         # 质量标准
└── examples/        # 案例
```

## Product Factory 生产流水线

```
Idea
  ↓
Market Research Agent
  ↓
Product Strategy Agent
  ↓
UX Agent
  ↓
Engineering Agent
  ↓
QA Agent
  ↓
Marketing Agent
  ↓
Sales Agent
  ↓
Revenue
```

---

# 七、Revenue System（商业变现）

## 目录结构

```
revenue/
├── crm/
├── sales/
├── affiliate/
├── growth/
├── customer-success/
└── analytics/
```

## CRM Agent 流水线

```
Lead
  ↓
Qualification
  ↓
Follow Up
  ↓
Conversion
```

---

# 八、Core Engine（核心引擎）

保留原 Sera Agent OS 核心：

```
core/
├── agent-runtime/       # Agent 运行时
├── task-engine/         # 任务引擎
├── permission/          # 权限系统
├── context-manager/     # 上下文管理
└── event-system/        # 事件系统
```

---

# 九、Router（调度大脑）

## 目录结构

```
router/
├── intent-parser/       # 意图解析
├── department-router/   # 部门路由
├── workflow-planner/    # 工作流规划
└── execution-manager/   # 执行管理
```

## 路由规范

输入：自然语言

输出：结构化任务分配

```yaml
# 示例: "做牛牛 AI 产品"
tasks:
  strategy:  CSO
  product:   CPO
  website:   Design
  code:      CTO
  marketing: CMO
  sales:     CRO
```

---

# 十、Memory（公司记忆）

## 目录结构

```
memory/
├── company-memory/      # 公司级记忆
├── project-memory/      # 项目级记忆
├── decision-memory/     # 决策记忆
├── failure-memory/      # 失败记忆
├── customer-memory/     # 客户记忆
├── agent-memory/        # 智能体记忆
└── world-model/         # 世界模型
```

---

# 十一、Evaluation（智能体评估）

## 目录结构

```
evaluation/
├── agent-score.yaml      # 评分标准
├── benchmark.yaml        # 基准对比
├── quality-check.md      # 质量检查
└── improvement-loop.yaml # 改进循环
```

## 评分权重

```yaml
agent_score:
  quality:         30%
  speed:           20%
  cost:            10%
  business-impact: 30%
  learning:        10%
```

---

# 十二、Evolution System（进化系统）

## 目录结构

```
evolution/
├── self-review/         # 自我审查
├── skill-discovery/     # 技能发现
├── failure-analysis/    # 失败分析
├── upgrade-proposal/    # 升级提案
└── experiment/          # 实验
```

## 每日自省机制

每天公司自动问：

```
昨天哪里失败？
哪个 Agent 效率低？
哪里可以自动化？
应该学习哪个公司？
```

---

# 十三、Portfolio（项目资产）

## 目录结构

```
portfolio/
├── niuniu-ai/
├── propfirm-tv/
├── traders-bank/
├── tradespan/
└── htx-otc/
```

## 项目标准结构

```
project/
├── business-plan.md    # 商业计划
├── product.md          # 产品定义
├── metrics.yaml        # 核心指标
├── agents.yaml         # 分配 Agent
└── revenue.md          # 收入模型
```

---

# 十四、DeepSeek 执行模式

所有执行使用 **Sera OPC OS Builder Mode**：

```
你现在是 Sera OPC OS Engineering Team。

你的目标不是完成代码任务。
你的目标是建设一个世界级 AI 公司的操作系统。

执行原则：
1. 先理解组织架构。
2. 所有代码必须符合 Repository Specification。
3. 所有 Agent 必须有完整 Contract。
4. 所有新能力必须注册 Registry。
5. 所有经验必须进入 Memory。
6. 所有项目必须最终连接 Revenue。

你的最高目标：
帮助 Sarah CEO 建立一个由 AI 员工组成的世界级公司。

开始执行。
```

---

# 十五、迁移路线

## Phase 1: GitHub 基础升级

```
sera-agent-os  →  sera-opc-os
```

加入：constitution / vision / organization

## Phase 2: Agent 公司化

加入：Executive Council / Departments / Agent Contract

## Phase 3: Factory 化

加入：Product Factory / Marketing Factory / Sales Factory

## Phase 4: 商业化

第一个验证：**牛牛 AI**

```
Research → Product → Website → Marketing → Sales → Revenue
```

## Phase 5: Autonomous Company

```
Sarah → CEO Agent → Executive Council → AI Employees
  → Factories → Revenue → Learning → Evolution
```

---

# 附录：文件清单

## 顶层文件

| 文件 | 说明 |
|------|------|
| `README.md` | 项目总览 |
| `LICENSE` | 开源协议 |
| `CHANGELOG.md` | 变更日志 |

## constitution/ (6 文件)

| 文件 | 说明 |
|------|------|
| `README.md` | 宪法概述 |
| `company-constitution.md` | 公司宪法 |
| `ai-employee-rules.md` | AI 员工规则 |
| `decision-framework.md` | 决策框架 |
| `ethics.md` | 伦理准则 |
| `operating-principles.md` | 运营原则 |

## vision/ (6 文件)

| 文件 | 说明 |
|------|------|
| `README.md` | 愿景概述 |
| `world-model.md` | 世界模型 |
| `benchmark-library.md` | 基准库 |
| `roadmap.md` | 路线图 |
| `market-map.md` | 市场地图 |
| `opportunity-engine.md` | 机会引擎 |

## organization/ (4 文件)

| 文件 | 说明 |
|------|------|
| `company-map.yaml` | 公司地图 |
| `department-map.yaml` | 部门映射 |
| `reporting-line.yaml` | 汇报线 |
| `responsibility-matrix.md` | 责任矩阵 |

## agents/executive/ (8 高管 × 7 文件 = 56 文件)

| Agent | ID |
|-------|-----|
| ceo-agent | SERA-CEO-001 |
| cso-agent | SERA-CSO-001 |
| cpo-agent | SERA-CPO-001 |
| cto-agent | SERA-CTO-001 |
| coo-agent | SERA-COO-001 |
| cmo-agent | SERA-CMO-001 |
| cro-agent | SERA-CRO-001 |
| caio-agent | SERA-CAIO-001 |

## 注册清单

所有新 Agent、Skill、Workflow 必须注册到对应 Registry，确保组织可发现、可调度、可评估。