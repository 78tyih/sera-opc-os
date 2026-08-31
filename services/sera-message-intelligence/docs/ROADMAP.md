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
- [ ] Event extraction pipeline from validated messages
- [ ] conservative person/entity resolution
- [ ] temporal object merge + supersede/contradict semantics
- [ ] Opportunity Radar
- [ ] People / Relationship Radar
- [ ] Commitment tracker
- [ ] Risk monitor
- [ ] Topic momentum / project-context updates
- [ ] Self Intelligence weekly synthesis
- [ ] Personal Intelligence Brief V2 built from graph changes rather than message summaries
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
