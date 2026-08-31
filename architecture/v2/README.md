# Sera OPC OS V2 Architecture Index

> Read this directory as a set of layered specs. Newer delta specs override the corresponding sections of earlier documents without erasing historical rationale.

## Core documents

| Document | Role |
|---|---|
| `Sera-OPC-OS-V2.0-Blueprint.md` | Overall V2 company/OS blueprint |
| `Sera-Memory-Object-Protocol-V1.md` | Canonical object protocol (SMOP) |
| `Sera-Memory-Engine-V1-Architecture.md` | Memory engine / storage / retrieval |
| `Sera-Context-Runtime-Learning-OS-V1.md` | Context Runtime + Learning OS V1.1 baseline |
| `Sera-Learning-OS-WikiSkill-Upgrade-V1.2.md` | **Persistent Wiki + Skill Evolution upgrade; authoritative delta for Learning OS** |
| `Sera-Organization-OS-V1.md` | Organization model |
| `Sera-Workflow-OS-V1.md` | Workflow/orchestration model |

## Learning OS reading order

Read in this order:

```text
1. Sera-Context-Runtime-Learning-OS-V1.md
   - Context Governor
   - Experience / Root Cause / Rule promotion

2. Sera-Learning-OS-WikiSkill-Upgrade-V1.2.md
   - inserts Persistent Wiki as a first-class layer
   - adds Skill Proposal + Evaluation loop
   - keeps Experience -> Rule path
   - defines non-rollback Wiki knowledge
   - defines cross-model portability
```

## Final learning model

```text
Observable Execution
   ↓
Raw Experience
   ↓
Persistent Wiki Pattern
   ├──→ Rule Proposal → Validation → Organization Rule
   ├──→ Skill Proposal → Evaluation → Release / Rollback
   └──→ Workflow / Router improvement proposals
```

Core invariant:

> **Raw is immutable. Wiki accumulates. Skills can roll back. Runtime Context is disposable.**

## Runtime implementation

```text
core/sera-learning-os/SKILL.md
core/sera_learning_os/learning.py
core/sera_learning_os/test_learning.py
```

The runtime intentionally stops before production Skill writes. Evaluation records a decision; the existing policy/authority layer performs any actual release.
