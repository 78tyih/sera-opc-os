# Roadmap

## P0 — Message Core
- [x] MessageEventV1
- [x] PostgreSQL schema
- [x] FastAPI ingest endpoint
- [x] idempotent storage
- [x] collector interface
- [x] fake collector
- [x] unit tests
- [ ] CI workflow
- [ ] collector state persistence

## P1 — WeChat read-only collector
- [ ] isolate WCDB/native dependencies in `collectors/wechat-local`
- [ ] group discovery / allowlist
- [ ] polling + local checkpoint
- [ ] retry buffer
- [ ] heartbeat/status endpoint
- [ ] 5–10 group soak test

## P2 — Intelligence pipeline
- [ ] conversation chunking
- [ ] chunk summaries
- [ ] cross-conversation topic merge
- [ ] importance ranking
- [ ] evidence-backed Personal Intelligence Brief
- [ ] Markdown + HTML renderer

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
