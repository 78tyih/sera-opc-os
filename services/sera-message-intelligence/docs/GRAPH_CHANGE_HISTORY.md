# Graph Change History / World Change Brief

## Why this layer exists

A durable context graph answers **what appears true now**. It does not, by itself, answer the more useful daily question:

> What changed in my world today?

Sera Message Intelligence therefore keeps an append-only change history beside the current graph state.

```text
Messages / other evidence
→ Context Extraction
→ Durable Graph Upsert
→ Graph Change History
→ semantic change classification
→ World Change Brief
```

## Storage

`context_graph_changes` is append-only. Each meaningful mutation records:

- durable `object_id` and `object_type`;
- `created` or `updated` change kind;
- top-level changed fields;
- semantic change labels;
- newly added evidence IDs;
- before snapshot;
- after snapshot;
- extraction/synthesis `batch_id`;
- evidence-effective timestamp;
- record timestamp.

The current-state table remains `context_graph_objects`. History is not reconstructed by diffing the current table later; it is captured when the mutation happens.

## No history noise on rerun

A critical invariant is:

> Reprocessing the same durable evidence must not look like a new life event.

`created_at` / `updated_at` transport metadata does not by itself create a graph-change record. A repeat run with the same durable state records zero changes.

## Semantic labels

Examples include:

```text
new_evidence
meaningful_interaction
identity_label_changed
person_context_changed
opportunity_stage_changed
opportunity_signal_changed
next_actions_changed
opportunity_context_changed
commitment_status_changed
commitment_deadline_changed
commitment_context_changed
conflict_added
self_signal_status_changed
self_signal_evidence_strength_changed
self_signal_user_confirmation_changed
```

The raw before/after snapshots remain available even when a new label is added later.

## World Change Brief

`generate_world_change_brief.py` reads one local-day window from Graph Change History and produces:

```text
reports/YYYY-MM-DD/world-changes.json
reports/YYYY-MM-DD/world-changes.md
```

It groups changes into:

- New Opportunities;
- Opportunity Changes;
- Commitments;
- People / Relationships;
- Self Intelligence;
- Other Events.

Ranking is deterministic. The LLM does not decide which graph mutation is allowed to exist or which evidence IDs are valid.

## Relationship to Personal Intelligence Brief V1

```text
PIB V1
raw messages → validated claims → daily summary

PIB V2 foundation
persistent context state → graph changes → daily change brief
```

V1 is still useful for understanding a day's conversations. V2 is more useful for long-term cognition because it compares the world against its previous state.

## Examples

### Opportunity

```text
Yesterday
stage = qualified
probability = 0.40

Today
stage = negotiating
probability = 0.70

History
→ opportunity_stage_changed
→ opportunity_signal_changed
→ new_evidence
```

### Commitment conflict

```text
Existing due date: Sep 1
New evidence says: Sep 2

Durable object
→ keeps Sep 1 rather than silently replacing it
→ adds explicit conflict inference

History
→ conflict_added
→ new_evidence
```

### Person

A user posting another message in a shared group is not automatically a relationship change. A new evidence-backed meaningful interaction can produce `meaningful_interaction`; relationship significance is handled by People / Relationship Radar.

## Current boundary

The current implementation covers Person, Event, Opportunity, Commitment and SelfSignal changes. Risk / Topic / Project lifecycle changes will use the same history contract when those objects enter the durable store.
