# Implementation Status

Updated: 2026-08-31

## Executive status

The software foundation for Message Core, the Server Win collector runtime, the evidence-backed intelligence pipeline and the first Personal Context Graph extraction layer is implemented on branch `feat/sera-message-intelligence-p0` / PR #4. The main remaining risk is no longer core architecture; it is **live Server Win validation of the external WeChat capture dependency and multi-account runtime**.

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

Status: **object model + first extraction pipeline implemented**

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
- output: `reports/YYYY-MM-DD/context-candidates.json`;
- regression tests for invalid evidence, invented identities, account isolation and cross-chunk Person merge.

Next engineering sequence:

```text
Context Candidate
→ conservative Entity Resolution
→ Temporal Merge
→ Contradiction / Supersede Check
→ Durable Graph Upsert
```

Opportunity and Commitment signals intentionally remain separate candidates until this resolution layer determines whether signals from different conversations or dates refer to the same durable object.

Planned after graph persistence:
- Opportunity Radar;
- People / Relationship Radar;
- Commitment tracker;
- Risk monitor;
- project/topic memory;
- Personal Intelligence Brief V2 based on graph changes;
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
→ Person / Opportunity / Commitment evidence review
```

After this proof, the next implementation target is durable Entity Resolution + Graph Upsert rather than adding more extraction object types.
