# Server Win deployment contract

Server Win is the default long-running runtime for WeChat collection. Mac is a control/development client, not the production WeChat host.

## Default topology

```text
Windows interactive session
  ├─ WeChat / Weixin identity A
  ├─ WeChat / Weixin identity B ...
  ├─ vetted webot checkout (replaceable capture dependency)
  ├─ collector process A -> spool A -> Message Core
  ├─ collector process B -> spool B -> Message Core
  ├─ SMI FastAPI Message Core :8800
  ├─ PostgreSQL (Docker, restart unless-stopped)
  └─ optional Daily Brief scheduled task

Mac
  └─ Tailscale -> Server Win future dashboard/control surface
```

The default collector gateway is `http://127.0.0.1:8800`, so raw message traffic stays on Server Win unless explicitly changed.

## Multi-account rule

**One WeChat identity = one process + one env + one webot env/key + one spool + one Scheduled Task.**

Never multiplex several identities in one Python collector process. This provides failure isolation and prevents account metadata from being mixed.

For every identity, use unique values for:

- `SMI_WECHAT_ACCOUNT_ID`
- `SMI_COLLECTOR_INSTANCE_ID`
- `SMI_WEBOT_ENV_FILE`
- `SMI_SPOOL_PATH`

When several `wxid_*` directories share a common WeChat data parent, also set:

- `SMI_WECHAT_DATA_DIR` = common parent
- `SMI_WECHAT_WXID_DIR` = exact directory name for this identity

The webot adapter replaces its "most recently modified wxid" discovery inside that collector process with an exact validated account selector. The target must contain `db_storage\session\session.db`; otherwise startup fails rather than silently attaching to another account.

Install additional identities with `scripts/install-serverwin-wechat-instance.ps1`. See `instances/README.md`.

## webot configuration isolation

SMI sets `WEBOT_APP_HOME` to `SMI_WEBOT_ROOT` before importing webot and sets `WEBOT_ENV_FILE` to the per-instance `SMI_WEBOT_ENV_FILE`. This keeps `WCDB_KEY` and client-specific native settings separate from SMI's database/API/LLM configuration.

Do not copy a WCDB key into Git or into any checked-in example file.

## Startup model

1. PostgreSQL runs in Docker with `restart: unless-stopped`.
2. Message Core runs as `Sera Message Intelligence - Core`.
3. Each WeChat identity has its own AtLogOn collector Scheduled Task.
4. Daily Brief can be installed after a clock time is explicitly chosen.

A collector does not require Core to be ready first: if Core is unavailable, messages remain in its local SQLite outbox and drain when Core returns.

## Why Task Scheduler instead of a Windows Service

WeChat is an interactive desktop application. A traditional Windows Service runs in Session 0 and is a poor lifecycle owner for a logged-in desktop WeChat session. Collectors therefore run as **AtLogOn Scheduled Tasks** with the interactive user token, automatic restart, one running instance and no execution time limit.

## Read-only guarantee

`WebotCaptureSource` registers a callback that always returns `None`. SMI never calls `send_text`.

Native WCDB/key/patch code is **not vendored into SMI**. It remains an external replaceable dependency because WeChat client internals are version-sensitive and carry compatibility/compliance risk.

## Bootstrap first identity

```powershell
powershell -ExecutionPolicy Bypass -File scripts\bootstrap-serverwin.ps1 -RepoRoot D:\Sera\sera-opc-os
```

To also install a Daily Brief schedule, explicitly choose a time with `-DailyReportAt HH:mm`. There is no hard-coded production report time.

## First live smoke test

1. Review `.env`: change ingest API key and configure LLM endpoint/model/key.
2. Create one per-account collector env from `serverwin.env.example`.
3. Create/verify that identity's separate webot env/key.
4. Pin `SMI_WECHAT_WXID_DIR` when more than one account directory is present.
5. Start with 5-10 explicit groups or `*`.
6. Ensure the corresponding WeChat identity is logged in on Server Win.
7. Start Core + the identity collector task.
8. Confirm messages appear in PostgreSQL under the expected `account_id`.
9. Stop Core for several minutes and verify only that identity's spool grows.
10. Restart Core and verify spool drain without duplicates.
11. Repeat for the second identity before scaling further.
12. Run `python scripts/generate_daily_brief.py --date YYYY-MM-DD` and inspect JSON/Markdown/HTML.
13. Reboot Server Win, log back in, and verify tasks recover.
