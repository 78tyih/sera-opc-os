# Sera Learning OS — WikiSkill Upgrade V1.2

| Field | Value |
|---|---|
| Version | 1.2 |
| Status | Active architecture delta |
| Date | 2026-08-31 |
| Base | `Sera-Context-Runtime-Learning-OS-V1.md` (V1.1) |
| Reference | Google Research WikiSkill, arXiv:2608.27454 |
| Runtime | `core/sera_learning_os/learning.py` |
| Skill Contract | `core/sera-learning-os/SKILL.md` |

---

## 0. Why this upgrade exists

V1.1 already solved an important problem:

```text
Experience
 -> Root Cause Analysis
 -> Pattern Detection
 -> Hypothesis Rule
 -> Validation
 -> Organization Rule
```

That loop is still valid, but it has one structural limitation:

> Pattern knowledge is treated mostly as a transit state on the way to Rule, not as a durable first-class knowledge layer that can also improve Skills.

WikiSkill shows a more general learning architecture:

```text
Raw Experience
 -> Persistent Wiki Knowledge
 -> Skill Proposal
 -> Evaluation
 -> Skill evolution
```

Sera V1.2 therefore **does not delete the V1.1 Experience→Rule loop**. It inserts a durable Wiki in the middle and adds a second consumer: Skill Evolution.

## 1. Final Learning Architecture

```text
                         Observable Execution
                   Run / Event / Tool I/O / Result
                              / Error / Feedback
                                   |
                                   v
+----------------------------------------------------------------+
| L0 RAW EXPERIENCE                                              |
| Immutable evidence / event / trace reference                   |
+-------------------------------+--------------------------------+
                                |
                                v
                         Wiki Maintainer
                                |
                                v
+----------------------------------------------------------------+
| L1 PERSISTENT WIKI                                             |
| Patterns / Root Causes / Success Strategies / Failed Attempts  |
| Model Behavior / Tool Behavior / Experiment History            |
+----------------------+---------------------------+-------------+
                       |                           |
                       v                           v
                Rule Extraction              Skill Proposer
                       |                           |
                       v                           v
               Rule Validation              Skill Candidate
                       |                           |
                       v                           v
             Organization Rule             Evaluation Gate
                       |                     /           \
                       |                 reject         accept
                       |                    |              |
                       |              keep baseline   release/version
                       |                    |              |
                       +--------------------+--------------+
                                            |
                                            v
                              Wiki retains all outcomes
```

The Persistent Wiki is therefore a **shared organizational learning substrate**, not merely a prompt document.

## 2. Four separate objects

Sera must keep these concepts separate:

### Raw Experience

Answers:

> What observably happened?

Examples:

- tool call failed;
- a test passed;
- a generated artifact was rejected;
- human feedback said the output was too verbose;
- a workflow required three retries;
- a model produced a schema mismatch.

Raw does not require private chain-of-thought.

### Wiki Pattern

Answers:

> What recurring fact or strategy have we learned from evidence?

Examples:

- a specific model repeatedly fails on a particular output schema;
- post-action verification reduces false success;
- a certain design pattern performs better for landing pages;
- a previous attempted fix caused regressions and should not be repeated.

### Rule / Skill

Rule answers:

> What constraint or principle should govern behavior?

Skill answers:

> What executable procedure should an agent follow?

They are separate consumers of Wiki knowledge.

### Runtime Context

Answers:

> What does this agent need right now?

Runtime Context is temporary and deliberately smaller than the full Wiki.

## 3. Non-rollback knowledge rule

V1.2 adopts a strict invariant:

> **A rejected Skill patch can roll back. The knowledge that motivated and evaluated it cannot roll back.**

Example:

```text
PAT-013 says:
"Agent often reports deployment success without checking the live URL."

SEP-021 proposes:
"Always run three expensive verification checks."

Evaluation:
- success rate unchanged
- latency +40%
- cost +35%

Decision:
REJECT SEP-021
```

Result:

- production Skill remains unchanged;
- `PAT-013` remains valid;
- `skill-impact` records that the three-check fix was rejected;
- future proposers know not to repeat the same expensive solution.

This turns failed experiments into durable organizational knowledge.

## 4. What changes from V1.1

### V1.1

```text
Experience
 -> root_cause
 -> repeated pattern
 -> draft Rule
 -> validation
 -> Rule
```

### V1.2

```text
Raw Experience
 -> Wiki Pattern
       |
       +-> Rule Proposal -> Rule Validation -> Rule
       |
       +-> Skill Proposal -> Regression Eval -> Skill
       |
       +-> Workflow/Router improvement proposal
```

Pattern is now a first-class persistent object and can outlive any single Rule or Skill version.

## 5. Root Cause principle stays

V1.1's strongest rule remains:

> Do not generalize from superficial `failure_mode`; generalize from evidence-linked `root_cause`.

V1.2 expands that logic:

- failure patterns need root-cause evidence;
- success patterns need mechanism/context evidence where possible;
- model behavior must be scoped to the tested model/model family;
- tool behavior must be scoped to the tested environment/version;
- conflicting evidence moves Pattern to `contested`, not deletion.

## 6. Pattern lifecycle

```text
provisional
   |
   v
supported
   |
   v
verified
   |
   +------> contested
   |            |
   |            v
   +------> superseded
```

Suggested semantics:

- `provisional` — limited observations;
- `supported` — repeated independent evidence;
- `verified` — representative evaluation and/or high-authority confirmation;
- `contested` — meaningful contradictory evidence;
- `superseded` — a newer interpretation explains the evidence better.

This lifecycle is orthogonal to SMOP `data_state` and object `authority`.

## 7. Skill evolution lifecycle

```text
Pattern(s)
 -> Skill Evolution Proposal
 -> candidate version
 -> representative test set
 -> regression set
 -> model/environment breakdown
 -> decision
```

Decision values:

```text
accepted
rejected
revise
model_specific
insufficient_evidence
```

Production writes happen **after** evaluation and policy/authority checks.

## 8. Cross-model portability

A Skill is not automatically universal.

Every proposal must declare one portability scope:

```text
universal
model_family
model_specific
agent_shell_specific
tool_environment_specific
```

Evaluation must preserve per-model/per-environment results.

A candidate that improves average score but causes a severe regression for one important model must not be silently promoted as universal.

This is especially important in Sera because the same capability can run through Codex, Kimi, DeepSeek, Trae, WorkBuddy and future runtimes.

## 9. Runtime Context boundary

Normal Inference Agents should receive:

```text
Founder / Project Rules
Project Context
Current State
Current Task
Relevant Memory / Experience
Relevant Skills
Latest Handoff
```

They should not receive by default:

```text
all Raw traces
entire Wiki corpus
all rejected proposals
all historical Skill diffs
```

Why:

1. context budget;
2. irrelevant historical noise;
3. Wiki knowledge can mask defects in weak Skills;
4. learning/debug agents and runtime agents have different responsibilities.

Wiki access is primarily for:

- Wiki Maintainer;
- Skill Proposer;
- Evaluator;
- explicit diagnostic/research tasks.

## 10. Runtime implementation V0

Implemented at:

```text
core/sera_learning_os/learning.py
```

Tables:

```text
learning_raw_signals       append-only
wiki_patterns              current materialized Pattern state
wiki_pattern_evidence      append-only evidence links
skill_evolution_proposals  proposal materialized state
skill_evaluations          append-only eval results
learning_events            append-only audit log
```

Current operations:

```python
init_learning_schema(conn)
record_raw_signal(conn, signal)
upsert_pattern(conn, pattern)
propose_skill_change(conn, proposal)
record_evaluation(conn, evaluation)
get_pattern(conn, pattern_id)
list_patterns(conn, status=None)
```

Important: `record_evaluation()` explicitly returns `production_skill_modified=False`.

V0 records decisions; it does not auto-write production Skills.

## 11. Context Hub mapping

Canonical human/Git layer:

```text
SeraContextHub/
├── 06_Memory-Candidates/
├── 07_Raw-Experience/
├── 08_Wiki/
│   ├── patterns/
│   ├── logs.md
│   └── skill-impact.md
└── 99_System/
    ├── SERA_LEARNING_OS_V0.md
    └── templates/
        ├── PATTERN.example.md
        └── SKILL_EVOLUTION_PROPOSAL.example.md
```

Runtime DB is not a second canonical truth. The bridge must export governed durable knowledge back to the Git-auditable canonical layer through explicit sync/governance.

## 12. Daily learning review

Existing daily summary should evolve into two products:

### Daily Operations Summary

What happened yesterday?

### Daily Learning Review

What did the organization learn?

Suggested output:

```text
New provisional patterns
Patterns strengthened/contested
Repeated known failures
New Skill proposals
Skill evaluations
Rejected experiments worth remembering
Potential cross-project lessons
```

Do not automatically promote a provisional Pattern simply because it appeared in a daily report.

## 13. Metrics

The Learning OS should be judged by operational improvement, not document count.

Primary metrics:

```text
Task success rate
Repeated failure recurrence
Known-failure rediscovery count
Regression rate after Skill updates
Average retries / tool calls
Time/cost per successful task
Skill proposal acceptance rate
Cross-model portability rate
```

A system that writes many Patterns but continues making the same mistakes is not learning.

## 14. Phased rollout

### Phase A — Capture

- Raw signals
- evaluator outcomes
- human feedback

### Phase B — Compile

- Wiki Maintainer
- Pattern creation/update
- evidence linking

### Phase C — Propose

- Skill Proposer
- candidate patch generation

### Phase D — Evaluate

- baseline/candidate regression harness
- model/environment matrix

### Phase E — Controlled release

- policy/authority gate
- version Skill
- rollback support

### Phase F — Semi-autonomous learning

Only low-risk Skill classes may auto-promote after strong evidence and deterministic regression gates.

Founder Rules, security boundaries, external-action permissions and high-risk business logic remain authority-gated.

## 15. Final invariant

Sera's learning loop is now defined as:

```text
Memory gives continuity.
Wiki gives accumulated understanding.
Skills give reusable action.
Context gives task-specific focus.
Evaluation prevents self-corruption.
```

Or, operationally:

> **Raw is immutable. Wiki accumulates. Skills can roll back. Runtime Context is disposable. Every capability change must be traceable to evidence.**
