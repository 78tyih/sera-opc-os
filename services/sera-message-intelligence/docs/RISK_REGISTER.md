# Risk Register

| Risk | Impact | Current mitigation |
|---|---|---|
| WeChat client version changes | Collector/key onboarding can stop working | Keep native/WCDB/key behavior behind replaceable external adapter; diagnose before changing core |
| Key-onboarding PID ambiguity | Wrong account key/environment attribution when multiple WeChat processes exist | Onboard one account at a time; multi-WeChat runtime starts only after independent environments are established |
| Native WCDB dependency | Portability / maintenance | No native imports in Message Core |
| Account risk controls | Login interruption | WeChat path is read-only; conservative polling; no SMI auto-send |
| Windows session logout | WeChat process exits and capture stops | Dedicated user-session runtime; heartbeat aging marks effective offline; avoid policies that log disconnected users off |
| Sandbox/multi-instance compatibility | Chat data or client behavior can change across WeChat releases | Windows user-session isolation is production default; sandbox strategy is experimental only |
| Multi-account isolation | Cross-account contamination | Separate Windows user, env, webot env/key, `account_id`, collector ID, spool and exact `wxid_*` pin |
| Message loss | Missing intelligence | Collector checkpoint + durable SQLite outbox |
| Duplicate delivery | Noisy reports / wrong counts | Database-enforced external-ID + fingerprint idempotency |
| Privacy | Sensitive personal/group content | Local-first raw storage, explicit downstream export policy, no secrets committed |
| LLM hallucination | Incorrect brief conclusions | Level-1 evidence IDs, fail-closed validation, validated-claim-only final citation set |
| Token cost | Expensive large-group analysis | Chunk summaries then cross-group merge |
| Platform API changes | Adapter breakage | Stable `MessageEventV1`; replace adapters only |
| Third-party licensing | Commercial restrictions | Copy only permissively licensed code; CipherTalk is design reference only |
