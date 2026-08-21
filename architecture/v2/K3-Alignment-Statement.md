# K3 对齐声明

| Field | Value |
|-------|-------|
| Version | 1.0 |
| Status | Active |
| Source | Kimi K3 审计点评 + 对抗式审查 |
| Canonical | [Sera Context Runtime & Learning OS V1.1](Sera-Context-Runtime-Learning-OS-V1.md) |
| Date | 2026-08-21 |

---

## A. 砍什么

| 砍掉/冻结 | 理由 |
|-----------|------|
| 30+ 纯文档目录（autonomous-os/, commercial-os/, intelligence-os/, business/, revenue/, evolution/, creative/ 等） | 它们是蓝图，不是代码。核心价值在 `core/sera_memory_kernel/`。冻结不再扩展。 |
| README 中的"六层架构"叙事（Layer 0-5） | V1.1 已修正为 4 纵向 + 1 横向底座 + 1 反馈环。六层版本与 canonical doc 冲突。 |
| "Agent = 员工" 比喻 | 一个有好记忆的 Agent 胜过五个患失忆的 Agent。Agent 数量由真实并发度决定，不由组织架构图决定。 |
| Registry JSON 作为"独立注册表" | `agents.json` / `workflows.json` / `projects.json` / `styles.json` / `skills.json` 手工维护，与 Kernel objects 表不同步。Kernel 数据库本身就是注册表。 |
| 5 个平台适配器的新增投入 | 6 个 adapters/ 目录（每目录仅一个 SKILL.md）冻结。只维护 Trae 一个平台的深度集成。 |

---

## B. 深什么

| 深化 | 理由 |
|------|------|
| `root_cause` 系统 | 这是 Sera 最锋利的差异化：禁止从 failure_mode 聚类，只从 root_cause 聚类。市面上没有任何 Agent 框架做到。扩展黑名单、加审计日志、加遥测。 |
| `health_check()` 表面 | 一个记忆系统如果没有运行时度量，就等于一个没有仪表盘的引擎。必须能回答：注入命中率？根因重复率？规则成熟度？ |
| 产品定位 | 从 "World-Class AI Company Operating System" → "Organizational memory for one-person companies"。不卖操作系统，卖复利。 |

---

## C. 度量标准

| 指标 | 定义 | 目标 |
|------|------|------|
| `injection_hit_rate` | 有 root_cause 的 Experience 被 build_context 访问过的比例 | > 80%（Phase 3） |
| `root_cause_repeat_rate` | 同一 root_cause 跨不同任务出现的次数 | 逐月下降趋势 |
| `rule_maturity_days` | 活跃 Rule 从创建至今的平均天数 | 至少一条 Rule > 30 天 |
| `promotion_rate` | 每 N 条 Experience 中晋升为 Rule 的数量 | ≥ 1/20 |

**元原则：每加一个机制，先问"我怎么知道它在工作"。**

---

## D. 产品定位

**旧：** World-Class AI Company Operating System —— 一个由人类 CEO 驱动、AI 员工执行、持续学习进化的 AI 原生公司操作系统。

**新：** Organizational memory for one-person companies —— 一个人经营公司的记忆内核。把每一次失败变成下一次的上下文。

**为什么改：** "Agent OS" 这个词已经通胀了（LangGraph、CrewAI、AutoGen 都在讲）。Sera 的真实差异不是"让 AI 干活"，而是"让 AI 长记性"——每次失败归因、归因聚类成规则、规则强制注入下一次任务。这是一个**复利叙事**：第 N+1 个项目站在前 N 个的根因库上。

**一句话定位：** 不要卖操作系统，卖复利。

---

*Document Version: 1.0*
*Canonical Reference: [Sera Context Runtime & Learning OS V1.1](Sera-Context-Runtime-Learning-OS-V1.md)*