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

## P1 — WeChat read-only collector (Server Win)
- [x] Server Win as default production WeChat runtime
- [x] isolate native/WCDB dependency behind external webot capture adapter
- [x] group allowlist / `*` passthrough
- [x] polling + local durable checkpoint
- [x] SQLite retry/outbox buffer
- [x] heartbeat/status integration
- [x] Task Scheduler install/remove/health scripts
- [x] read-only callback contract
- [ ] install and validate vetted webot checkout on Server Win
- [ ] 5–10 group live soak test
- [ ] reboot/login recovery test
- [ ] Message Core outage/recovery test on Server Win

## P2 — Intelligence pipeline
- [x] conversation chunking
- [x] evidence-bound chunk claims
- [x] cross-conversation topic/intelligence merge
- [x] deterministic importance ranking
- [x] evidence-backed Personal Intelligence Brief schema
- [x] PostgreSQL daily-window query
- [x] OpenAI-compatible LLM adapter
- [x] Markdown + HTML renderer
- [x] daily-report CLI
- [ ] live LLM run on captured WeChat data
- [ ] scheduled daily report task

## P3 — Multi-IM
- [ ] OpeniLink/iLink adapter
- [ ] Feishu adapter
- [ ] WeCom adapter
- [ ] search and semantic retrieval

## P4 — Intelligence OS
- [ ] people radar
- [ ] project/topic memory
- [ ] plugin/capability API
- [ ] policy-scoped agent access
