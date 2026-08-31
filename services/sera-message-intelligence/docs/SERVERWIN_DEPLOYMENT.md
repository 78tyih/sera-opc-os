# Server Win deployment contract

Server Win is the default long-running runtime for WeChat collection. Mac is a control/development client, not the production WeChat host.

## Default topology

```text
Windows interactive session
  ├─ WeChat / Weixin (logged in)
  ├─ vetted webot checkout (capture dependency, replaceable)
  ├─ SMI WeChat Collector
  │    ├─ read-only callback
  │    ├─ local SQLite durable outbox
  │    ├─ checkpoint
  │    └─ heartbeat
  ├─ SMI FastAPI Message Core :8800
  └─ PostgreSQL

Mac
  └─ Tailscale -> Server Win API / future dashboard
```

The default collector gateway is `http://127.0.0.1:8800`, so raw message traffic stays on Server Win unless explicitly changed.

## Why Task Scheduler instead of a Windows Service

WeChat is an interactive desktop application. A traditional Windows Service runs in Session 0 and is a poor lifecycle owner for a logged-in desktop WeChat session. The collector therefore uses an **AtLogOn Scheduled Task** with an interactive user token, automatic restart, one running instance and no execution time limit.

## Read-only guarantee

`WebotCaptureSource` loads a separately installed webot checkout and registers a callback that always returns `None`. SMI never calls `send_text`.

Native WCDB/key/patch code is **not vendored into SMI**. It remains an external, replaceable dependency because WeChat client internals are version-sensitive and carry compatibility/compliance risk.

## Failure semantics

1. Captured message -> `MessageEventV1`.
2. Durably enqueue into local `wechat-spool.db`.
3. Advance checkpoint only after durable local enqueue.
4. POST outbox to Message Core.
5. If Core/PostgreSQL is offline, keep the outbox on disk.
6. Resume delivery later; Message Core performs idempotent deduplication.
7. Heartbeat reports checkpoint, message counts and errors.

This gives at-least-once delivery with idempotent persistence.

## First Server Win smoke test

1. Copy `serverwin.env.example` to `serverwin.env`.
2. Set account ID, API key and `SMI_WEBOT_ROOT`.
3. Start with 5-10 explicit groups or `*`.
4. Start Message Core/PostgreSQL.
5. Install `scripts/install-serverwin-task.ps1`.
6. Start the task and run `scripts/health-check-serverwin.ps1`.
7. Confirm messages appear in PostgreSQL.
8. Stop Message Core for several minutes and verify the spool grows.
9. Restart Message Core and verify the spool drains without duplicate rows.

## Multi-account direction

Use one collector process/task/spool per WeChat identity. Do not multiplex several identities inside one collector process.
