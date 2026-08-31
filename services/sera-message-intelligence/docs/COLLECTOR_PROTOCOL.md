# Collector Protocol

A collector is a replaceable platform adapter.

P0 interface: `collector_instance_id`, `platform`, `poll()`, `checkpoint()`, `heartbeat()`.

Expected runtime states: starting, online, degraded, offline, error.

## WeChat local collector requirements

The upcoming `wechat-local` adapter must be read-only in P0, support group allowlists and `*` mode, maintain a local checkpoint/retry buffer, back off on repeated errors, survive API restarts, reinitialize after WeChat restarts, and never expose native WCDB dependencies to core packages.
