# Changelog

## V2.1 Learning OS Upgrade (2026-08-31)

### 🧠 Persistent Learning Architecture
- 引入 WikiSkill-inspired 三阶段学习链：`Raw Experience → Persistent Wiki → Skill Evolution`。
- 保留原有 `Experience → Root Cause → Rule` 路径，并把 Persistent Wiki 升级为 Rule / Skill / Workflow 改进的共享知识层。
- 新增核心不变量：**Raw 不可变，Wiki 可增长，Skill 可回滚，Runtime Context 可丢弃。**
- 普通 Runtime Agent 默认不加载整个 Raw / Wiki；Wiki 主要供 Maintainer / Proposer / Evaluator 使用。

### 🧩 Core Skill / Runtime
- 新增 `core/sera-learning-os/SKILL.md`。
- 新增 `core/sera_learning_os/learning.py`：Raw Signal、Wiki Pattern、Skill Proposal、Evaluation 最小运行时。
- 新增 `core/sera_learning_os/test_learning.py` 单元测试。
- `record_evaluation()` 只记录 proposal decision，不直接修改 production Skill。
- 明确拒绝持久化显式 `chain_of_thought` / private reasoning 字段。

### 📚 Architecture
- 新增 `architecture/v2/Sera-Learning-OS-WikiSkill-Upgrade-V1.2.md`。
- 新增 `architecture/v2/README.md`，定义 V1.1 baseline + V1.2 learning delta 的阅读顺序。
- `core/sera-skill-registry/SKILL.md` 注册 `sera-learning-os` 并加入 portability / evaluation governance。

### ✅ Verification status
- 已提交针对 append-only Raw、private-CoT rejection、Pattern evidence accumulation、Skill Proposal evaluation/rollback boundary 的测试代码。
- 当前 ChatGPT 执行容器因 DNS 无法访问 GitHub，未能在本会话 clone 仓库执行测试；不得视为测试已通过。应由本地/CI 下一次运行验证。

## V2.0 (2026-08-21)

### 🏗️ 架构升级
- 从 `sera-agent-os` V1.1 升级为 `sera-opc-os` V2.0
- 引入六层架构：Constitution → Organization → Factory → Employee → Learning → Autonomous
- 新增 12 个顶层目录：constitution/, vision/, strategy/, organization/, executive/, departments/, skills/, workflows/, factories/, revenue/, router/, evolution/

### 📄 蓝图文档
- 01-Blueprint.md — 公司级设计规范
- 02-Repo-Spec.md — GitHub 工程规范
- 03-Factory-Blueprint.md — 生产系统设计
- 04-Employee-Blueprint.md — 首批 50 名员工目录

### 🧠 公司宪法
- 新增 company-constitution.md
- 新增 operating-principles.md
- 新增 decision-framework.md

### 🏛️ 组织系统
- 新增 company-map.yaml
- 新增 benchmark-library.md
- 新增 Executive Council 定义

### 🔄 保留内容
- 保留 `sera-agent-os` 全部现有代码和配置
- 保留 `core/`, `runtime/`, `adapters/`, `portfolio/`, `registry/`, `memory/`, `evaluation/`
- 保留 `agents/`, `business/`, `creative/`, `product/`, `control-center/`, `platforms/`
