# Implementation Status

Updated: 2026-08-31

## Executive status

The software foundation for Message Core, the Server Win collector runtime, the evidence-backed intelligence pipeline, the durable Personal Context Graph and the first deterministic action Radars is implemented on branch `feat/sera-message-intelligence-p0` / PR #4. The main remaining risk is no longer core architecture; it is **live Server Win validation of the external WeChat capture dependency and multi-account runtime**.

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

## P2 — Intelligence Pipeline

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
- Personal Intelligence Brief schema;
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

Status: **object model + extraction + durable upsert + action Radars implemented**

Completed:
- durable object schemas for `ContextEvent`, `Person`, `Relationship`, `Opportunity`, `Commitment`, `Risk`, `Topic`, `ProjectContext`, `SelfSignal`;
- observation vs inference separation with evidence references and confidence;
- Self Intelligence evidence ladder and user-confirmation invariants;
- bounded message-chunk extraction into Person / Event / Opportunity / Commitment candidates;
- deterministic Person creation from observed senders only;
- sender identity namespaced by `platform + account_id + sender_id`, preventing two WeChat accounts from silently merging the same sender ID;
- fail-closed rejection when model output cites unknown message IDs or unknown sender refs;
- model-derived Event / Opportunity / Commitment output stays `hypothesis` rather than becoming confirmed memory;
- deterministic Person evidence merge across conversation chunks;
- daily CLI: `scripts/extract_context_candidates.py`;
- durable PostgreSQL `context_graph_objects` store;
- conservative exact Opportunity resolution by normalized title + related people;
- conservative exact Commitment resolution by owner + beneficiaries + normalized summary;
- candidate Opportunity IDs remapped to durable IDs before linked Commitments are persisted;
- conflicting Commitment due dates preserved as explicit conflict inference rather than silently overwritten;
- `--persist` CLI path for extraction -> resolution -> durable graph upsert;
- **Opportunity Radar** with deterministic fit / urgency / probability / freshness / evidence scoring;
- **Commitment Tracker** with deterministic due-pressure / confidence / evidence / conflict attention scoring;
- **People Radar** where active opportunity / commitment / recency signals dominate raw interaction volume;
- **Relationship Radar** where an edge requires an explicit shared active Opportunity or owner↔beneficiary Commitment context; group co-presence alone is not sufficient;
- JSON + Markdown CLI outputs for Context Radar and People / Relationship Radar;
- regression tests across extraction, persistence, conflict preservation, opportunity ranking, commitment ranking and evidence-grounded relationship edges.

Current operational path:

```text
PostgreSQL messages
→ bounded Context Extraction
→ context-candidates.json
→ conservative exact resolution
→ temporal merge
→ context_graph_objects
→ Opportunity Radar / Commitment Tracker / People & Relationship Radar
```

The resolver intentionally favors false negatives over false-positive merges. Cross-platform Person resolution and fuzzy semantic Opportunity/Commitment resolution are still deferred.

Current deterministic read models:

```text
Opportunity Radar
→ What should I pursue now?

Commitment Tracker
→ What must not be forgotten?

People / Relationship Radar
→ Who deserves attention now, and what concrete context connects us?
```

Next P4 target:

```text
Graph Change History
→ Created / Updated / Conflict / Superseded / Resolved
→ "What changed in my world today?"
→ Personal Intelligence Brief V2
```

Planned after that:
- Risk monitor;
- project/topic momentum;
- conservative cross-platform Person resolution;
- explicit supersede / contradict / rejected lifecycle semantics;
- evidence-gated weekly Self Intelligence;
- policy-scoped agent access;
- plugin/capability API;
- long-term learning from resolved actions and decisions.

## Current blocker: WeBot key onboarding

The external webot extractor first tries an already-running WeChat process, then asks for a full exit/re-login and waits for a valid 64-character WCDB key. A long spinner generally means the hook phase is running but no valid key has been observed yet.

Before multi-account runtime is enabled, key onboarding must be performed **sequentially, one account at a time**, with all other WeChat processes closed. See `WEBOT_KEY_EXTRACTION.md`.

## Next live proof

```text
real WeChat message
→ PostgreSQL
→ Personal Intelligence Brief
→ context-candidates.json
→ --persist
→ durable Person / Opportunity / Commitment objects
→ Context Radar
→ People / Relationship Radar
```

After this proof, the next architectural layer should be Graph Change History / Brief V2 rather than another rewrite of ingestion, extraction or ranking.
