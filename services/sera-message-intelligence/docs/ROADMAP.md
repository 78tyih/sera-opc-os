# Roadmap

## P0 — Message Core
- [x] MessageEventV1
- [x] PostgreSQL schema
- [x] FastAPI ingest endpoint
- [x] idempotent storage
- [x] collector interface
- [x] fake collector
- [x] unit tests
- [x] CI workflow
- [x] collector state persistence
- [x] collector status API + stale-heartbeat effective-offline detection

## P1 — WeChat read-only collector (Server Win)
- [x] Server Win as default production WeChat runtime
- [x] isolate native/WCDB dependency behind external webot capture adapter
- [x] isolate webot app home / env from SMI runtime
- [x] one-process/one-env/one-spool multi-account collector model
- [x] exact `wxid_*` account pin validation
- [x] per-instance Task Scheduler installer
- [x] group allowlist / `*` passthrough
- [x] polling + local durable checkpoint
- [x] SQLite retry/outbox buffer
- [x] heartbeat/status integration
- [x] read-only callback contract
- [x] Windows multi-user-session runtime design
- [x] multi-WeChat runtime manifest + status/doctor manager
- [x] WeBot key-onboarding doctor
- [ ] complete one real WeBot key onboarding on Server Win
- [ ] validate two live WeChat identities without cross-account contamination
- [ ] 5–10 group live soak test
- [ ] reboot/login recovery test
- [ ] Message Core outage/recovery test on Server Win

## P2 — Intelligence pipeline
- [x] conversation chunking
- [x] evidence-bound chunk claims
- [x] validated-claim-only final citation set
- [x] cross-conversation topic/intelligence merge
- [x] deterministic importance ranking
- [x] evidence-backed Personal Intelligence Brief schema
- [x] PostgreSQL daily-window query
- [x] OpenAI-compatible LLM adapter
- [x] Markdown + HTML renderer
- [x] daily-report CLI
- [x] parameterized Server Win Daily Brief task installer
- [ ] live LLM run on captured WeChat data
- [ ] choose/configure production daily report time

## P3 — Multi-IM
- [ ] OpeniLink/iLink adapter
- [ ] Feishu adapter
- [ ] WeCom adapter
- [ ] search and semantic retrieval
- [ ] report delivery sink abstraction

## P4 — Personal Context Graph / Intelligence OS
- [x] define durable object model: Event / Person / Relationship / Opportunity / Commitment / Risk / Topic / Project / SelfSignal
- [x] define Opportunity Intelligence / Relationship Intelligence / Self Intelligence product contracts
- [x] define evidence ladder for self inference and user-confirmed knowledge
- [x] bounded Event / Opportunity / Commitment extraction from message chunks
- [x] deterministic Person creation from observed senders only
- [x] namespace sender identity by platform + account + sender to prevent cross-account contamination
- [x] fail-closed evidence validation for extracted candidates
- [x] runnable `extract_context_candidates.py` daily candidate CLI
- [x] conservative exact Opportunity resolution by normalized title + related people
- [x] conservative exact Commitment resolution by owner + beneficiaries + normalized summary
- [x] durable `context_graph_objects` PostgreSQL object store
- [x] candidate ID -> durable object ID remapping before linked Commitment upsert
- [x] preserve conflicting Commitment due dates as explicit inference instead of silent overwrite
- [x] optional `--persist` path from daily extraction CLI into durable graph upsert
- [x] deterministic Opportunity Radar with fit / urgency / probability / freshness / evidence scoring
- [x] deterministic Commitment Tracker with due pressure / confidence / evidence / conflict scoring
- [x] `generate_context_radar.py` JSON + Markdown output
- [x] People Radar prioritizes opportunity / commitment / recency over raw interaction volume
- [x] Relationship Radar creates edges only from explicit shared Opportunity or Commitment context, never mere group co-presence
- [x] `generate_people_radar.py` JSON + Markdown output
- [x] append-only `context_graph_changes` history with before/after snapshots, semantic change labels and batch IDs
- [x] idempotent graph-change classification: rerunning identical evidence creates no history noise
- [x] deterministic Personal Intelligence Brief V2 / World Change Brief from graph changes
- [x] `generate_world_change_brief.py` JSON + Markdown output
- [x] evidence-gated Self Intelligence synthesis from validated graph changes
- [x] SelfSignal evidence levels L2/L3 derived by application code; L4 reserved for explicit user confirmation
- [x] reject unknown Change IDs, insufficient pattern evidence and sensitive/clinical identity inference
- [x] durable SelfSignal persistence without cross-window personality collapse
- [x] protect user-confirmed SelfSignals from later model downgrade
- [x] `generate_self_intelligence.py` 7/30-day style window + optional durable persistence
- [ ] conservative cross-platform Person entity resolution
- [ ] semantic/fuzzy Opportunity / Commitment resolution beyond exact signatures
- [ ] full temporal supersede / contradict / rejected lifecycle semantics for all graph object types
- [ ] Risk monitor
- [ ] Topic momentum / project-context updates
- [ ] user-facing confirm / reject / supersede actions for SelfSignals
- [ ] Personal Intelligence Brief V2 fusion of World Changes + Radars + Self Intelligence into one polished delivery artifact
- [ ] plugin/capability API
- [ ] policy-scoped agent access

## P5 — Multi-source Personal Context Layer
- [ ] GitHub / project facts
- [ ] Notion tables and project state
- [ ] Calendar and meeting events
- [ ] Email
- [ ] documents / research artifacts
- [ ] financial account / transaction facts through authorized sources
- [ ] agent runs / decisions / outputs
- [ ] unified graph query API for agents
