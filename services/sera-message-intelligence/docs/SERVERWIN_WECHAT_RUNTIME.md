# Server Win Multi-WeChat Runtime

## Production objective

Keep several WeChat identities online on Server Win without making the Message Core depend on a fragile client multi-open hack.

## Preferred strategy: Windows user-session isolation

Use one dedicated Windows local user profile per WeChat identity.

```text
Server Win
  Windows user SeraWechat01
    WeChat account A
    webot app/env A
    collector env/spool/task A

  Windows user SeraWechat02
    WeChat account B
    webot app/env B
    collector env/spool/task B

  Windows user SeraWechat03
    WeChat account C
    webot app/env C
    collector env/spool/task C

  Shared
    Message Core :8800
    PostgreSQL
    Daily Brief pipeline
```

Why this is preferred:

- Windows profiles naturally isolate `%USERPROFILE%`, Documents, AppData and WeChat data;
- process ownership gives an additional identity dimension;
- account onboarding is easier to reason about;
- switching users can leave the other user session running as long as it is not logged off;
- Message Core remains shared through localhost/Tailscale.

## Important limitation

The Windows client edition may limit simultaneous interactive desktop sessions. The design relies on keeping user sessions logged in, not on modifying RDP licensing or patching Windows session limits. If a machine policy logs disconnected users off, the corresponding WeChat will stop and the collector heartbeat will become effectively offline.

## Account onboarding order

Do not start with multi-open.

For account A:
1. log into Windows user A;
2. make sure no other WeChat/Weixin process is running on the machine during key onboarding;
3. complete the external WeBot onboarding for account A;
4. confirm the account-specific webot env contains a valid key without copying it to Git/chat;
5. pin the expected `wxid_*` directory in the SMI env;
6. install/start collector A;
7. verify `GET /v1/collectors` and real message ingestion.

Repeat the same process for B, C, etc. Only after each identity has a valid independent environment should the sessions be left online together.

## Why key onboarding must be single-account

The external webot key-extraction code discovers a WeChat process by executable name and returns the first matching PID. It does not bind a PID to `account_id` or a `wxid_*` directory. With several WeChat processes running, key attribution is therefore ambiguous.

SMI deliberately does not reimplement the extractor. It adds process/environment diagnostics and requires sequential onboarding.

## Runtime manifest

Copy `instances/wechat-runtime.example.json` outside Git or create a local non-secret copy. Do not place WCDB keys or passwords in the manifest.

Useful commands:

```powershell
# Overview
powershell -ExecutionPolicy Bypass -File scripts\wechat-runtime-manager.ps1 -Action status

# Validate paths/tasks/account ownership assumptions
powershell -ExecutionPolicy Bypass -File scripts\wechat-runtime-manager.ps1 -Action doctor

# Run key-onboarding diagnostics for one identity
powershell -ExecutionPolicy Bypass -File scripts\wechat-runtime-manager.ps1 -Action key-doctor -InstanceName wechat-main
```

`start-current` and `stop-current` operate only on the manifest identity owned by the **current Windows user**. They do not bypass WeChat single-instance controls or launch an app under another user's credentials.

## Experimental alternative: sandbox isolation

Sandbox/process-isolation products can run multiple application environments, but they are not the production default because WeChat 4.x compatibility and chat-data behavior have changed across releases. If evaluated, treat each sandbox as replaceable experimental infrastructure and keep the collector/message contracts unchanged.

## Recovery model

- PostgreSQL: Docker restart policy.
- Message Core: Scheduled Task.
- Collector: one AtLogOn task per Windows identity.
- WeChat itself: interactive application in that user's session.
- If a session disappears, heartbeat aging exposes the failure even if the collector cannot report `offline` cleanly.
