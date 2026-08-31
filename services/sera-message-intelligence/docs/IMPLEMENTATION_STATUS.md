# Implementation Status

Updated: 2026-08-31

## Executive status

The software foundation for Message Core, the Server Win collector runtime and the first evidence-backed intelligence pipeline is implemented on branch `feat/sera-message-intelligence-p0` / PR #4. The main remaining risk is no longer core architecture; it is **live Server Win validation of the external WeChat capture dependency and multi-account runtime**.

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

## P4 — Intelligence OS

Status: **not started**

Planned:
- People Radar;
- project/topic memory;
- policy-scoped agent access;
- plugin/capability API;
- long-term learning from resolved actions and decisions.

## Current blocker: WeBot key onboarding

The external webot extractor first tries an already-running WeChat process, then asks for a full exit/re-login and waits for a valid 64-character WCDB key. A long spinner generally means the hook phase is running but no valid key has been observed yet.

Before multi-account runtime is enabled, key onboarding must be performed **sequentially, one account at a time**, with all other WeChat processes closed. See `WEBOT_KEY_EXTRACTION.md`.
