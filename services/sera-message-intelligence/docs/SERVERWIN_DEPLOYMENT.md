# Server Win deployment contract

Server Win is the default long-running runtime for WeChat collection. Mac is a control/development client, not the production WeChat host.

## Default topology

```text
Windows interactive session
  ├─ WeChat / Weixin (logged in)
  ├─ vetted webot checkout (capture dependency, replaceable)
  │    └─ its own .env / WCDB_KEY
  ├─ SMI WeChat Collector
  │    ├─ read-only callback
  │    ├─ local SQLite durable outbox
  │    ├─ checkpoint
  │    └─ heartbeat
  ├─ SMI FastAPI Message Core :8800
  ├─ PostgreSQL (Docker, restart unless-stopped)
  └─ optional Daily Brief scheduled task

Mac
  └─ Tailscale -> Server Win future dashboard/control surface
```

The default collector gateway is `http://127.0.0.1:8800`, so raw message traffic stays on Server Win unless explicitly changed.

## webot configuration isolation

SMI sets `WEBOT_APP_HOME` to `SMI_WEBOT_ROOT` before importing webot and sets `WEBOT_ENV_FILE` to `SMI_WEBOT_ENV_FILE` (default `<webot-root>/.env`). This keeps webot's `WCDB_KEY`, client-specific native settings and its `.env` separate from SMI's database/API/LLM configuration.

Do not copy a WCDB key into Git or into `serverwin.env.example`.

## Startup model

There are independently recoverable processes:

1. PostgreSQL runs in Docker with `restart: unless-stopped`.
2. Message Core runs as the scheduled task `Sera Message Intelligence - Core`.
3. WeChat Collector runs as `Sera Message Intelligence - WeChat Collector` after interactive logon.
4. Daily Brief can be installed as a daily scheduled task after a clock time is explicitly chosen.

The collector does not require Core to be ready first: if Core is unavailable, messages remain in the local SQLite outbox and drain when Core returns.

## Why Task Scheduler instead of a Windows Service

WeChat is an interactive desktop application. A traditional Windows Service runs in Session 0 and is a poor lifecycle owner for a logged-in desktop WeChat session. The collector therefore uses an **AtLogOn Scheduled Task** with an interactive user token, automatic restart, one running instance and no execution time limit.

## Read-only guarantee

`WebotCaptureSource` loads a separately installed webot checkout and registers a callback that always returns `None`. SMI never calls `send_text`.

Native WCDB/key/patch code is **not vendored into SMI**. It remains an external, replaceable dependency because WeChat client internals are version-sensitive and carry compatibility/compliance risk.

## Bootstrap

From an elevated PowerShell inside the service directory:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\bootstrap-serverwin.ps1 -RepoRoot D:\Sera\sera-opc-os
```

To also install a Daily Brief schedule, explicitly choose the time:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\bootstrap-serverwin.ps1 -RepoRoot D:\Sera\sera-opc-os -DailyReportAt "08:30"
```

The example time above is illustrative only; there is no hard-coded daily report time.

The bootstrap creates a dedicated venv, installs SMI, starts PostgreSQL, creates `.env` / `serverwin.env` templates if missing, and registers Core + Collector scheduled tasks.

The script does **not** silently install webot by default. Either place a vetted checkout at `D:\Sera\deps\webot`, or explicitly pass `-InstallWebot`.

## Failure semantics

1. Captured message -> `MessageEventV1`.
2. Durably enqueue into local `wechat-spool.db`.
3. Advance checkpoint only after durable local enqueue.
4. POST outbox to Message Core.
5. If Core/PostgreSQL is offline, keep the outbox on disk.
6. Resume delivery later; Message Core performs idempotent deduplication.
7. Heartbeat reports checkpoint, message counts and errors.

This gives at-least-once delivery with idempotent persistence.

## First live smoke test

1. Review `.env`: change ingest API key and configure LLM endpoint/model/key.
2. Review `serverwin.env`: set `SMI_WECHAT_ACCOUNT_ID`, `SMI_WEBOT_ROOT`, and `SMI_WEBOT_ENV_FILE`.
3. Ensure the external webot `.env` has the working native/WCDB configuration required by that dependency.
4. Start with 5-10 explicit groups or `*`.
5. Ensure WeChat is logged in on Server Win.
6. Start Core and Collector tasks.
7. Run `scripts/health-check-serverwin.ps1`.
8. Confirm messages appear in PostgreSQL.
9. Stop Core for several minutes and verify the spool grows.
10. Restart Core and verify the spool drains without duplicate rows.
11. Run `python scripts/generate_daily_brief.py --date YYYY-MM-DD` and inspect JSON/Markdown/HTML.
12. Reboot Server Win, log back in, and verify Core + Collector recover.
13. Once satisfied, install the recurring Daily Brief task at the desired time.

## Multi-account direction

Use one collector process/task/spool per WeChat identity. Do not multiplex several identities inside one collector process.
