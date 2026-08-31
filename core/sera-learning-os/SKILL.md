---
name: sera-learning-os
version: 0.1.0
author: Sera
category: core
status: active
compatible:
  - WorkBuddy
  - Codex
  - Trae
  - Claude-Code
  - Cursor
---

# Sera Learning OS

## Purpose
把多 Agent 的执行经验持续编译成 **Persistent Wiki → 可验证 Skill Proposal → 经评估后发布/回滚的能力**，让系统通过真实任务逐步变强，而不是靠一次 Reflection 直接改 Prompt/Skill。

设计参考 Google Research WikiSkill（arXiv:2608.27454），并与 Sera Context Hub、Memory Kernel、Skill Registry、Agent Router 对齐。

## When to use

当出现以下任一情况：

- 同类任务重复成功或重复失败；
- 一个错误已经被多个 Agent 重复踩到；
- 用户指出某种做法需要固化/禁止；
- 某个 Skill 可能过时、缺步骤或存在模型兼容问题；
- 想验证“经验是否值得变成 Skill”；
- 想分析某个 Skill 的修改为什么被接受/拒绝；
- 需要做跨模型 Skill transfer / regression 测试。

普通业务 Runtime Agent 不应默认加载整个 Wiki。

## Inputs

- Observable Run / Event / Tool call / Result / Error / Human feedback
- Context Hub governed Memory / Decisions
- Existing Wiki Patterns
- Existing Skill version
- Evaluation tasks / regression probes
- Agent + Model + Tool environment metadata

## Outputs

- Raw Experience Signal / trace reference
- Wiki Pattern（provisional / supported / verified / contested / superseded）
- Skill Evolution Proposal
- Evaluation Result
- Skill Impact Record
- accepted / rejected / revise / model-specific / insufficient-evidence decision

## Workflow

```text
1. CAPTURE
   Observable Run/Event/Result/Error
        ↓
   Raw Experience Signal

2. COMPILE
   Raw evidence + existing patterns
        ↓
   Wiki Maintainer
        ↓
   Persistent Pattern

3. PROPOSE
   Relevant Patterns + Skill baseline
        ↓
   Skill Evolution Proposal

4. EVALUATE
   Baseline vs Candidate
   + regression tasks
   + model/environment matrix
        ↓
   accept / reject / revise / model-specific

5. GOVERN
   accepted → release/version Skill
   rejected → keep/rollback Skill
   BOTH → preserve Wiki + skill-impact history
```

## Four-Layer Contract

```text
L0 Raw Experience  = what observably happened
L1 Wiki Knowledge  = what we learned and why
L2 Skills/Rules    = what agents should do
L3 Runtime Context = what this agent needs now
```

**Raw 不可变，Wiki 可增长，Skill 可回滚，Runtime Context 可丢弃。**

## Dependencies

- `core/sera_memory_kernel` — Runtime Event/Object/Relation + Context Governor
- `core/sera-skill-registry` — Skill discovery/version registry
- `core/sera-agent-router` — task/agent routing
- Sera Context Hub:
  - `07_Raw-Experience/`
  - `08_Wiki/`
  - `99_System/SERA_LEARNING_OS_V0.md`

## Runtime Interface V0

Python module: `core/sera_learning_os/learning.py`

Core operations:

```python
init_learning_schema(conn)
record_raw_signal(conn, signal, actor="system")
upsert_pattern(conn, pattern, actor="wiki-maintainer")
propose_skill_change(conn, proposal, actor="skill-proposer")
record_evaluation(conn, evaluation, actor="evaluator")
get_pattern(conn, pattern_id)
list_patterns(conn, status=None, limit=100)
```

## Governance

### Wiki Maintainer
可读 Raw + Wiki；可创建/更新 Pattern；**不能直接改 production Skill**。

### Skill Proposer
可读 relevant Wiki + baseline Skill + selected evidence；只能生成 Proposal。

### Evaluator
比较 baseline / candidate；记录 regression；给出 decision。

### Production Skill Write
必须通过对应 Authority / Policy Gate。Founder / Project Rule 仍按现有更高 Authority 治理。

## Portability

每个 Skill Proposal 必须标记：

```text
universal
model_family
model_specific
agent_shell_specific
tool_environment_specific
```

不能因为平均分提升，就忽略某个模型/环境出现严重回归。

## Iron Rules

- 不因一次成功/失败直接重写 production Skill。
- 不删除被拒绝的 Skill Proposal 历史。
- Skill rollback 不等于 Wiki rollback。
- Raw Layer 不要求、不保存模型私有 chain-of-thought。
- 普通 Runtime Agent 不默认加载整个 Raw / Wiki。
- Proposer 不得充当自己的最终审批者。
- 所有 Skill change 必须可追溯到 Pattern + Evidence + Evaluation。

## Success Metrics

- repeated failure recurrence ↓
- task success rate ↑
- regression after Skill change ↓
- tool calls / time per successful task ↓
- rediscovered-known-failure count ↓
- cross-model portability ↑

目标不是生成更多 Markdown，而是让 **经验变成经过验证、可复用、可迁移的能力**。
