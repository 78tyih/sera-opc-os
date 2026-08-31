# Meaningful Change Policy · V4.2

## Principle

Design Drift is a factual delta. Design Learning is a reviewed interpretation.

Never update Canonical Design Memory merely because a website changed.

## Weighted Dimensions

| Dimension | Weight | Default meaning |
|---|---:|---|
| `design_patterns` | 5 | semantic design language changed |
| `conversion_patterns` | 5 | conversion structure changed |
| `brand_personality` | 4 | brand voice/material posture changed |
| `typography.primary_font` | 4 | primary type identity changed |
| `typography.heading_style` | 4 | hierarchy/display behavior changed |
| `component_patterns` | 4 | component vocabulary changed |
| `motion_language` | 4 | interaction/motion language changed |
| `color_system.primary` | 3 | primary brand color changed |
| `typography.body_style` | 3 | reading density changed |
| `layout_language.*` | 3 | macro layout language changed |
| `typography.mono_font` | 3 | utility/technical voice changed |
| `color_system.secondary/background` | 2 | supporting palette changed |
| `color_system.accent` | 1 | low-signal palette change |

## Severity Gate

```text
0                     → none
1–4                   → minor
5–9                   → moderate
10+                   → major

design_patterns changed     → major
conversion_patterns changed → major
```

## Actions

### none
- save the new snapshot only if provenance/freshness changed;
- no memory review.

### minor
- archive snapshot;
- do not update Pattern Library;
- do not notify downstream creation workflows by default.

### moderate
- queue Design Analyst / Reviewer;
- compare intent, product context and measured evidence;
- update Canonical Memory only after approval.

### major
- queue semantic review;
- rerun relevant Cross-site study;
- check whether existing Canonical Patterns are superseded, weakened or strengthened;
- write an explicit Memory Decision.

## Anti-false-positive Rules

1. New extractor coverage is not drift.
2. Missing current measurement is a data-quality issue, not drift.
3. A raw token change cannot by itself prove a design strategy change.
4. Historical snapshots cannot be promoted as “current”.
5. Same-domain page variants never count as independent cross-site evidence.
6. Change frequency is not quality.
