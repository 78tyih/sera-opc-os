# Self Intelligence

## Product goal

Self Intelligence is not a personality quiz and not a mental-health classifier.

Its job is to help answer:

> What does repeated evidence suggest I am actually paying attention to, trying to do, worrying about, changing, or repeatedly postponing during this period?

It is built **after** the durable graph and Graph Change History so that the model reasons over validated changes rather than isolated sentences.

```text
Raw messages
→ validated claims
→ durable objects
→ graph changes
→ repeated evidence across time / contexts
→ SelfSignal hypothesis
→ explicit user decision
```

## Allowed SelfSignal types

- `attention`
- `preference`
- `behavior_pattern`
- `goal`
- `concern`
- `transition`
- `decision_style`
- `interest_shift`

These are intentionally limited to practical, time-bounded personal context.

## Evidence ladder

### L0 — Raw evidence

A message, file, calendar event, project update, transaction fact or Agent run.

### L1 — Observation

A fact directly observable from evidence.

Example:

> Three product-related opportunities received new evidence this week.

### L2 — Hypothesis

A time-bounded interpretation supported by validated graph changes.

Example:

> During this week, product-building work appears to have captured a meaningful share of attention.

L2 is still a hypothesis. One isolated event cannot become `preference`, `behavior_pattern`, `decision_style` or `interest_shift`.

### L3 — Supported cross-source pattern

Requires repeated support plus at least two distinct source contexts calculated by application code.

The model does not get to declare its own source diversity.

Example:

> Across several independent conversations and project changes this month, attention repeatedly shifted toward building reusable AI products rather than one-off execution work.

### L4 — User-confirmed knowledge

Only an explicit user decision can create L4.

```text
status = confirmed_by_user
evidence_level = 4
user_confirmation_ref = required
```

The synthesis path cannot call the confirmation path automatically. A later model run cannot downgrade or overwrite a user-confirmed SelfSignal.

## Evidence validation

The LLM returns exact `supporting_change_ids` / `contradicting_change_ids`.

Application code then:

1. rejects any unknown Change ID;
2. derives source diversity from the referenced graph-change snapshots;
3. enforces minimum support for pattern-like signal types;
4. caps confidence according to evidence amount;
5. chooses L2 or L3;
6. never allows model output to create L4.

## Confidence caps

Current conservative defaults:

```text
1 supporting change
→ max confidence 0.55

2 supporting changes
→ max confidence 0.75

3+ supporting changes + 2+ source contexts
→ max confidence 0.90 / L3
```

These are calibration defaults, not immutable product truths. Real user feedback should tune them later.

## Sensitive / clinical boundary

Self Intelligence must not turn communication patterns into clinical or protected-attribute claims.

The model prompt and application validator reject examples such as:

- psychiatric diagnosis;
- ADHD / autism / depression claims from behavior;
- political ideology inference;
- sexual orientation inference;
- other sensitive identity inference.

The desired question is **what appears to be happening in the user's life/work context**, not **what hidden sensitive identity does the model think the user has**.

## Time-window isolation

Each SelfSignal has an explicit `window_start` / `window_end` and a window-scoped stable ID.

Therefore:

```text
Week 1 signal
≠ automatically the same as
Week 4 signal
```

Repeated similar SelfSignals across windows can later become evidence for a longer-term pattern, but that requires a separate synthesis step. This prevents temporary states from silently becoming permanent personality facts.

## Explicit user decisions

SelfSignal lifecycle decisions are separated from model synthesis:

```text
Model / evidence path
→ hypothesis / supported

Explicit user-decision path
→ confirm / reject / supersede
```

Every user decision requires a non-empty `decision_reference`. The system adds it as a `user_confirmation` evidence reference and records the before/after mutation in Graph Change History.

### Confirm

```text
confirm
→ status = confirmed_by_user
→ evidence_level = 4
→ confidence = 1.0
→ decision reference required
```

### Reject

```text
reject
→ status = rejected_by_user
→ keeps the evidence level that was actually earned
→ decision reference required
```

### Supersede

```text
supersede
→ status = superseded
→ preserves the historical statement instead of deleting it
→ decision reference required
```

A later model synthesis is not allowed to downgrade a terminal user decision. Another **explicit** user decision may reverse a prior user decision, and that reversal is itself audited in Graph Change History.

## CLI

Generate the last seven days ending yesterday:

```powershell
python scripts/generate_self_intelligence.py --days 7
```

Generate a 30-day synthesis:

```powershell
python scripts/generate_self_intelligence.py --days 30
```

Persist validated signals to the durable graph:

```powershell
python scripts/generate_self_intelligence.py --days 7 --persist
```

List durable SelfSignals:

```powershell
python scripts/manage_self_signal.py --action list
```

Explicitly confirm one signal:

```powershell
python scripts/manage_self_signal.py `
  --action confirm `
  --id self_xxx `
  --reference user-decision:confirm:2026-09-01 `
  --note "This reflects my current core focus."
```

Reject or supersede uses the same CLI with `--action reject` / `--action supersede`.

Outputs from synthesis:

```text
reports/self-intelligence/YYYY-MM-DD_to_YYYY-MM-DD/
├─ self-intelligence.json
└─ self-intelligence.md
```

## Relationship to the three product engines

```text
Opportunity Intelligence
→ What should I pursue?

Relationship Intelligence
→ Who matters now, and why?

Self Intelligence
→ What does repeated evidence suggest I am currently experiencing, prioritizing or repeatedly doing?
```

Together they transform message capture into a Personal Intelligence System rather than a group-chat summarizer.

## Next steps

- compare SelfSignals across multiple windows without collapsing them into permanent traits;
- connect Topic / Project / Calendar / GitHub / Notion / financial facts as additional evidence sources;
- calibrate thresholds from actual user corrections;
- surface only the highest-value SelfSignals in the polished Personal Intelligence Brief V2;
- later expose the same explicit decision contract through a properly authenticated UI/API, without allowing Agent auto-confirmation.
