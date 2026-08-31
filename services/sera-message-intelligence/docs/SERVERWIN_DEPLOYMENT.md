# Server Win deployment contract

Server Win is the default long-running runtime for WeChat collection. Mac is a control/development client, not the production WeChat host.

## Default topology

```text
Windows interactive session
  ├─ WeChat / Weixin identities
  ├─ vetted webot checkout (replaceable capture dependency)
  ├─ one collector process/task/spool per identity
  ├─ SMI FastAPI Message Core :8800
  ├─ PostgreSQL (Docker, restart unless-stopped)
  └─ optional Daily Brief scheduled task

Mac
  └─ Tailscale -> Server Win API / future dashboard
```

## Multi-account rule

**One WeChat identity = one process + one env + one webot env/key + one spool + one Scheduled Task.**

Use `scripts/install-serverwin-wechat-instance.ps1` for additional identities. Pin `SMI_WECHAT_WXID_DIR` when multiple `wxid_*` directories exist under the configured data parent. The pin must resolve to a directory containing `db_storage\session\session.db`; startup fails rather than silently selecting another account.

## Collector observability

Collectors heartbeat to Message Core. Query:

```text
GET /v1/collectors
x-smi-api-key: <same local API key>
```

The API exposes both `reported_status` and `effective_status`. A process can die before reporting `offline`, so Message Core marks a collector effectively offline when its heartbeat is older than `SMI_COLLECTOR_STALE_SECONDS` (default 90 seconds).

On Server Win run:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\health-check-serverwin.ps1 -RepoRoot D:\Sera\sera-opc-os
```

It checks the local Core, WeChat process presence and current collector heartbeat states without printing API keys or WCDB keys.

## webot configuration isolation

SMI sets `WEBOT_APP_HOME` to `SMI_WEBOT_ROOT` and `WEBOT_ENV_FILE` to the per-instance `SMI_WEBOT_ENV_FILE` before importing webot. Do not copy WCDB keys into Git.

## Newer Weixin reader

If the bundled webot `wcdb_api.dll` is incompatible with a newer Weixin build,
use the read-only WDA native broker source instead of retrying the old DLL:

```text
SMI_WECHAT_SOURCE=wda_native
SMI_WDA_ROOT=D:\Sera\deps\wda-probe
SMI_WEBOT_ENV_FILE=D:\Sera\real-integration\.env
SMI_WECHAT_DATA_DIR=D:\wx\xwechat_files
SMI_WECHAT_WXID_DIR=wxid_<exact-directory>
```

The WDA runtime must be obtained from its pinned, checksum-verified release and
kept outside the Sera repository. `wda_native` reads only the configured
`db_storage` root, never calls WeChat send APIs, and keeps the WCDB key in the
local webot environment; the key must not be copied into Git or chat.

## Startup model

1. PostgreSQL: Docker `restart: unless-stopped`.
2. Message Core: `Sera Message Intelligence - Core` scheduled task.
3. Each WeChat identity: its own AtLogOn collector task.
4. Daily Brief: optional daily task after a clock time is explicitly chosen.

If Core is unavailable, collector messages stay in that identity's SQLite outbox and drain when Core returns.

## Read-only guarantee

`WebotCaptureSource` registers a callback that always returns `None`. SMI never calls `send_text`. Native WCDB/key/patch code is not vendored into SMI.

## Bootstrap first identity

```powershell
powershell -ExecutionPolicy Bypass -File scripts\bootstrap-serverwin.ps1 -RepoRoot D:\Sera\sera-opc-os
```

For a Daily Brief schedule pass `-DailyReportAt HH:mm`; there is no hard-coded production report time.

## First live smoke test

1. Review `.env`: API key + LLM settings.
2. Create one collector env and one separate webot env/key per identity.
3. Pin exact `wxid_*` directories when multiple identities share a data parent.
4. Start Core and first collector.
5. Run the health check and confirm effective status is `online`.
6. Confirm messages land under the expected `account_id`.
7. Stop Core; verify only that identity's spool grows; restart Core and verify drain without duplicates.
8. Add second identity and verify both independently remain online with no cross-account contamination.
9. Generate a live daily brief and inspect evidence IDs.
10. Reboot/log back in and verify task recovery.
