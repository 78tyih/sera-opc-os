# Risk Register

| Risk | Impact | P0/P1 mitigation |
|---|---|---|
| WeChat client version changes | Collector can stop reading | Keep WCDB/native logic behind replaceable adapter |
| Native WCDB dependency | Portability / maintenance | No native imports in Message Core |
| Account risk controls | Login interruption | P0 read-only; conservative polling; no auto-send |
| Multi-account isolation | Cross-account contamination | Every event requires `account_id` and collector identity |
| Message loss | Missing intelligence | Collector checkpoint + retry buffer in P1 |
| Duplicate delivery | Noisy reports / wrong counts | Database-enforced external-ID + fingerprint idempotency |
| Privacy | Sensitive personal/group content | Local-first storage, explicit downstream export policy |
| LLM hallucination | Incorrect brief conclusions | Evidence message IDs required for report items |
| Token cost | Expensive large-group analysis | Chunk summaries then cross-group merge |
| Platform API changes | Adapter breakage | Stable `MessageEventV1`; replace adapters only |
| Third-party licensing | Commercial restrictions | Copy only permissively licensed code; CipherTalk is design reference only |
