# WeChat instance configuration

Do not commit real instance env files or WCDB keys.

Recommended Server Win layout:

```text
D:\Sera\MessageIntelligence\instances\
  wechat-main.env
  wechat-main.webot.env
  wechat-work.env
  wechat-work.webot.env
```

Each `*.env` is an SMI collector configuration copied from `serverwin.env.example`.
Each `*.webot.env` belongs to the external webot dependency for that identity and can contain its `WCDB_KEY` / native settings.

Install each identity as a separate scheduled task:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\install-serverwin-wechat-instance.ps1 `
  -RepoRoot D:\Sera\sera-opc-os `
  -PythonExe D:\Sera\MessageIntelligence\.venv\Scripts\python.exe `
  -InstanceName wechat-main `
  -EnvFile D:\Sera\MessageIntelligence\instances\wechat-main.env
```

Use a unique `SMI_WECHAT_ACCOUNT_ID`, `SMI_COLLECTOR_INSTANCE_ID`, `SMI_WEBOT_ENV_FILE`, and `SMI_SPOOL_PATH` for every identity.

For multiple identities under a common WeChat data parent, configure both:

```text
SMI_WECHAT_DATA_DIR=D:\path\to\xwechat_files
SMI_WECHAT_WXID_DIR=wxid_exact_directory_name
```

The collector validates that the pinned directory contains `db_storage\session\session.db` before opening it. This prevents the adapter from silently choosing whichever account directory changed most recently.
