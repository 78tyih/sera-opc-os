# Context Radar

The Context Radar is the first user-facing read model built on top of the durable Personal Context Graph.

It intentionally uses deterministic application-side scoring rather than asking an LLM to decide what deserves attention. The goal is inspectability: every ranking can be explained, tuned and regression-tested.

## Opportunity Radar

Input: durable `Opportunity` objects from `context_graph_objects`.

Current score:

```text
Opportunity Score =
  30% Fit
+ 25% Urgency
+ 20% Probability
+ 15% Freshness
+ 10% Evidence Strength
```

### Freshness

Freshness uses a simple 30-day linear decay:

```text
freshness = max(0, 1 - days_since_last_signal / 30)
```

This is deliberately easy to inspect. It is not a learned model.

### Evidence strength

The first version saturates at five distinct evidence references:

```text
evidence_strength = min(1, evidence_count / 5)
```

### Active vs terminal opportunities

Active:
- signal
- qualified
- exploring
- negotiating

Terminal / archived:
- won
- lost
- parked

Terminal opportunities remain visible for history but are sorted behind active opportunities regardless of their raw score.

### Explainability tags

Radar output adds deterministic reasons such as:
- `high_fit`
- `high_urgency`
- `high_probability`
- `fresh_signal`
- `stale_signal`
- `repeated_evidence`
- `has_next_action`

These tags are display explanations, not additional hidden scoring features.

## Commitment Tracker

Input: durable `Commitment` objects from `context_graph_objects`.

For active commitments, attention score is:

```text
Attention Score =
  45% Due Pressure
+ 25% Confidence
+ 15% Evidence Strength
+ 15% Conflict Signal
```

Terminal commitments have an attention score of zero.

### Due pressure

Current deterministic bands:

| Due state | Due pressure |
| --- | ---: |
| overdue | 1.00 |
| within 1 day | 0.95 |
| within 3 days | 0.85 |
| within 7 days | 0.70 |
| within 14 days | 0.50 |
| later / no due date | 0.30 |

No due date is intentionally still visible: an open promise without a date can itself be a follow-up risk.

### Conflict signal

If durable merge detects conflicting due dates, the commitment carries an explicit inference beginning with:

```text
Conflicting commitment due dates observed
```

The tracker surfaces this as `has_conflict` and raises attention rather than silently choosing one date.

## CLI

```bash
python scripts/generate_context_radar.py
```

Default outputs:

```text
reports/context-radar/
├── radar.json
└── radar.md
```

The CLI does not call an LLM. It reads the current durable graph and computes the same deterministic scores every time for the same graph state and reference time.

## Product interpretation

The Radar should answer two operational questions before more advanced graph views are built:

1. **Which opportunities deserve attention now?**
2. **What promises are due, overdue, conflicted or easy to forget?**

The scoring weights are provisional product defaults. They should be tuned from real usage after live WeChat data is flowing, not treated as permanent truth.
