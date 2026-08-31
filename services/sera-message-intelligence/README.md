# Sera Message Intelligence

Sera Message Intelligence is a local-first, multi-IM intelligence layer for Sera OPC OS. Its purpose is not to build another chat client. It turns high-volume conversations from WeChat and, later, Feishu/WeCom/OpeniLink and other IM sources into one evidence-backed Personal Intelligence Brief.

## What problem it solves

The target user has many active conversations and groups, but should not need to read every message stream manually. The system continuously captures allowed messages, preserves source provenance, deduplicates them, and then produces a daily cross-group brief with actions, risks, opportunities, decisions, people to reply to, resources and knowledge.

P0/P1/P2 are intentionally local-first. Raw WeChat data and collector state stay on Server Win by default; Mac is the control/development client.

## Current end-to-end shape

```text
Server Win
  WeChat identity A -> Collector A -> local SQLite outbox --+
  WeChat identity B -> Collector B -> local SQLite outbox --+--> Message Core :8800
  WeChat identity C -> Collector C -> local SQLite outbox --+          |
                                                                  PostgreSQL
                                                                      |
                                                        evidence-backed AI pipeline
                                                                      |
                                                Personal Intelligence Brief
                                                 JSON / Markdown / HTML
```

## Runtime rules

- Server Win is the production WeChat host.
- One WeChat identity = one collector process + one SMI env + one external webot env/key + one SQLite spool + one Scheduled Task.
- WeChat-native/WCDB/key logic stays behind a replaceable external adapter and never leaks into Message Core.
- SMI is capture-only for WeChat. Its webot callback always returns `None`; there is no SMI reply/send path.
- Every important brief item must trace to validated source message IDs.
- Final synthesis can cite only message IDs that survived Level-1 evidence validation.

## Current implementation status

### P0 — Message Core: implemented

- `MessageEventV1`
- FastAPI ingest
- PostgreSQL persistence
- external message ID + SHA-256 fingerprint idempotency
- collector heartbeat persistence
- `GET /v1/collectors` health view with stale-heartbeat effective-offline detection
- scoped GitHub Actions CI

### P1 — Server Win WeChat runtime: code-complete foundation, live validation pending

- durable SQLite outbox/checkpoint
- retry/backoff and Core outage recovery
- external webot capture adapter
- per-account env/key/spool isolation
- exact `wxid_*` pin validation
- per-instance Scheduled Task installer
- Server Win bootstrap/health scripts
- Windows multi-user-session Runtime Manager foundation
- WeBot key-extraction doctor

Still required: validate real accounts on Server Win, two-account isolation, 5–10 group soak, reboot/logon recovery, and Core outage/recovery on the real machine.

### P2 — Intelligence pipeline: implemented, live-data run pending

- report-day PostgreSQL query
- per-conversation chunking
- Level-1 evidence-bound claims
- fail-closed citation validation
- cross-conversation merge using only validated claims
- deterministic importance score
- JSON / Markdown / HTML rendering
- OpenAI-compatible LLM client
- parameterized Server Win Daily Brief task

Still required: first live report from captured WeChat data and selection of the production report time.

## Multi-WeChat production strategy

The preferred production model is **Windows user-session isolation**, not client patching:

```text
Windows user: SeraWechat01 -> WeChat account A -> webot env A -> Collector A
Windows user: SeraWechat02 -> WeChat account B -> webot env B -> Collector B
Windows user: SeraWechat03 -> WeChat account C -> webot env C -> Collector C
```

Each account is onboarded separately before multi-account operation. Do not perform WCDB-key onboarding while several WeChat processes are running, because the external webot extractor selects a WeChat process by PID without account identity.

Sandbox-based multi-instance execution may be evaluated later as an experimental strategy, but it is not the production default.

## Key documents

- `docs/PROJECT_OVERVIEW.md` — product introduction and system value
- `docs/IMPLEMENTATION_STATUS.md` — actual implementation state and blockers
- `docs/SERVERWIN_DEPLOYMENT.md` — Server Win deployment contract
- `docs/SERVERWIN_WECHAT_RUNTIME.md` — multi-WeChat runtime design
- `docs/WEBOT_KEY_EXTRACTION.md` — built-in key onboarding diagnostics and recovery flow
- `docs/INTELLIGENCE_PIPELINE.md` — evidence pipeline
- `docs/ROADMAP.md` — P0→P4 roadmap

## Local development

```bash
docker compose up -d postgres
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
uvicorn sera_message_intelligence.main:app --reload --port 8800
```

For Server Win use `scripts/bootstrap-serverwin.ps1` and the deployment documents instead of the local-dev commands.
