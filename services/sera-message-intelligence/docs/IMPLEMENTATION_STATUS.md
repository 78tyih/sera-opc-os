# Implementation Status

Updated: 2026-08-31

## Executive status

The software foundation for Message Core, Server Win collector runtime, evidence-backed message intelligence, the durable Personal Context Graph, deterministic action Radars, Graph Change History and the first evidence-gated Self Intelligence layer is implemented on branch `feat/sera-message-intelligence-p0` / PR #4.

The main remaining risk is no longer core architecture. It is **live Server Win validation of the external WeChat capture dependency, first real data flow and multi-account runtime**.

## P0 — Message Core

Status: **implemented / CI green**

Completed:
- canonical `MessageEventV1`;
- FastAPI ingest endpoint;
- PostgreSQL schema;
- external-ID and fingerprint idempotency;
- race-safe duplicate handling;
- collector heartbeat persistence;
- collector health API with stale-heartbeat effective-offline detection;
- unit tests and scoped GitHub Actions.

## P1 — Server Win WeChat

Status: **runtime foundation implemented / live-machine validation pending**

Completed:
- Server Win production runtime contract;
- external webot capture adapter;
- native/WCDB dependency isolated from core;
- capture-only callback contract;
- local SQLite outbox/checkpoint;
- retry/backoff and Core-outage recovery;
- one identity = one env/key/spool/task;
- exact `wxid_*` pin validation;
- per-instance Scheduled Task installer;
- bootstrap and health tooling;
- multi-WeChat runtime manifest + status/doctor manager;
- key-onboarding diagnostics without exposing the key.

Live validation gates:
1. make one real WeBot account reach a stable valid WCDB environment;
2. verify message capture under the expected `account_id`;
3. onboard a second account separately;
4. keep both Windows user sessions alive and verify no cross-account contamination;
5. run 5–10 groups for an extended soak;
6. reboot/log back in and verify process recovery;
7. stop Message Core, verify per-account spool growth, restore Core and verify drain without duplicates.

## P2 — Message Intelligence Pipeline

Status: **implemented / first live report pending**

Completed:
- local report-day to UTC query window;
- bounded per-conversation chunks;
- Level-1 structured claims bound to exact message IDs;
- fail-closed chunk evidence validation;
- Level-2 receives validated claims only;
- final items restricted to validated-claim IDs;
- source metadata rebuilt from database rows;
- deterministic importance scoring;
- Personal Intelligence Brief V1 schema;
- OpenAI-compatible LLM adapter;
- JSON, Markdown and standalone HTML outputs;
- Server Win daily-report task installer.

Remaining:
- run against captured live WeChat messages;
- review false negatives/false positives;
- choose production report time;
- add delivery sink abstraction.

## P3 — Multi-IM

Status: **not started**

Planned:
- OpeniLink/iLink adapter;
- Feishu adapter;
- WeCom adapter;
- search and semantic retrieval;
- delivery sinks.

## P4 — Personal Context Graph / Intelligence OS

Status: **durable graph + change history + three intelligence views implemented as foundations**

### Durable graph

Completed:
- object schemas for `ContextEvent`, `Person`, `Relationship`, `Opportunity`, `Commitment`, `Risk`, `Topic`, `ProjectContext`, `SelfSignal`;
- observation vs inference separation with evidence refs and confidence;
- bounded message extraction into Person / Event / Opportunity / Commitment candidates;
- Person identity from observed senders only;
- sender namespace = `platform + account_id + sender_id`;
- fail-closed rejection of unknown message IDs / sender refs;
- durable PostgreSQL `context_graph_objects`;
- conservative exact Opportunity and Commitment resolution;
- linked transient Opportunity ID -> durable ID remapping;
- explicit conflict inference instead of silent Commitment due-date overwrite;
- `extract_context_candidates.py --persist`.

### Opportunity / Commitment / Relationship Intelligence

Completed:
- **Opportunity Radar**: deterministic fit / urgency / probability / freshness / evidence score;
- **Commitment Tracker**: due pressure / confidence / evidence / conflict score;
- **People Radar**: active opportunities, commitments and recency dominate raw message volume;
- **Relationship Radar**: edges require explicit Opportunity or Commitment context; mere WeChat group co-presence never creates a relationship edge;
- JSON + Markdown CLI outputs.

### Graph Change History

Completed:
- append-only PostgreSQL `context_graph_changes`;
- before/after durable object snapshots;
- changed-field list;
- semantic labels such as `new_evidence`, `opportunity_stage_changed`, `commitment_status_changed`, `conflict_added`, `meaningful_interaction`;
- extraction batch IDs for traceability;
- rerunning identical evidence does **not** create history noise;
- daily query by effective-time window;
- deterministic `generate_world_change_brief.py`.

Current V2 change path:

```text
Durable Graph state
→ append-only Graph Change History
→ semantic change classification
→ World Change Brief
→ "What changed in my world today?"
```

### Self Intelligence

Completed foundation:
- model may propose only time-bounded SelfSignal candidates;
- exact graph Change IDs are mandatory evidence;
- unknown Change IDs fail closed;
- `preference / behavior_pattern / decision_style / interest_shift` require repeated evidence rather than one isolated event;
- source diversity is calculated by application code from real evidence contexts, not accepted from model output;
- L2 = evidence-backed hypothesis;
- L3 = repeated cross-source supported pattern;
- L4 = explicit user-confirmed knowledge only;
- confidence caps depend on actual evidence count/diversity;
- sensitive/clinical identity or psychiatric inference is rejected;
- durable SelfSignal persistence is time-window scoped so separate weeks do not silently collapse into a permanent personality trait;
- later model output cannot downgrade a user-confirmed SelfSignal;
- `generate_self_intelligence.py --days 7|30 --persist` produces JSON + Markdown and optionally writes validated SelfSignals into the graph.

The intended distinction is:

```text
Message summary
= what people said

Graph state
= what currently appears true

Graph history
= what changed

Self Intelligence
= what repeated evidence suggests about the user's current attention, goals, concerns, transitions and behavior patterns

User confirmation
= what may become durable self-knowledge
```

### Remaining P4 work

- real-data calibration of Radar weights and Self Intelligence thresholds;
- conservative cross-platform Person entity resolution;
- semantic/fuzzy Opportunity / Commitment resolution beyond exact signatures;
- full supersede / contradict / reject lifecycle for all graph object types;
- Risk monitor;
- Topic / Project momentum;
- user-facing SelfSignal Confirm / Reject / Supersede actions;
- polished Personal Intelligence Brief V2 that fuses World Changes + Radars + Self Intelligence;
- policy-scoped agent access and query API.

## Current blocker — WeBot key onboarding

The external webot extractor first tries an already-running WeChat process, then asks for a full exit/re-login and waits for a valid 64-character WCDB key. A long spinner generally means the hook phase is running but no valid key has been observed yet.

Before multi-account runtime is enabled, key onboarding must be performed **sequentially, one account at a time**, with all other WeChat processes closed. See `WEBOT_KEY_EXTRACTION.md`.

## Next live proof

```text
real WeChat message
→ PostgreSQL
→ Personal Intelligence Brief V1
→ context-candidates.json
→ --persist
→ durable Person / Opportunity / Commitment objects
→ Opportunity / Commitment / People Radars
→ context_graph_changes
→ World Change Brief V2
→ 7-day Self Intelligence
```

This is now the critical validation path. The next priority should be running this exact chain on real Server Win WeChat data rather than adding another architecture layer.
