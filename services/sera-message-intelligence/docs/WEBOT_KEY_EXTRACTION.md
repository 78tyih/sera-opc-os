# WeBot WCDB Key Onboarding — Diagnosis Guide

This document explains the external WeBot onboarding state machine and how SMI diagnoses it. It does not reimplement or redistribute WeBot's native key-extraction logic.

## What the spinner means

The external WeBot flow does roughly this:

1. verify its bundled key helper DLL can load;
2. find a `Weixin.exe` / `WeChat.exe` PID;
3. try the already-running process briefly;
4. if no key is observed, ask for a full WeChat exit and re-login;
5. detect the new PID and enter a hook/poll phase;
6. accept only a 64-character hexadecimal key;
7. save the working key into the selected WeBot environment.

A UI that keeps showing **automatic key capture in progress** usually means the extraction thread is still in a waiting/hook/poll phase and has not produced a valid 64-character key yet.

## Most likely causes of a long-running capture

### 1. WeChat was not fully exited

Closing the main window is not enough if a tray/background process remains. During onboarding, confirm Task Manager no longer shows `Weixin.exe` or `WeChat.exe`, then relaunch only the target account.

### 2. More than one WeChat process is running

The external extractor finds the first matching WeChat executable PID. It has no SMI `account_id` context. During key onboarding, run **one account only**.

### 3. Startup timing was missed

The direct-running-process path can fail because the relevant database key may already have been loaded before the helper started observing the process. This is why the built-in UI asks for a complete exit and login again.

### 4. Client/helper compatibility changed

If WeChat updates, a native helper that previously worked may no longer observe the expected event. This is an adapter compatibility problem, not a Message Core problem.

### 5. Different Windows user / integrity level

Keep WeBot and the target WeChat under the same Windows user. If one is elevated and the other is not, process-level helper behavior can fail. Use the same account/session during onboarding.

### 6. Wrong environment file

A valid key can appear to be 'lost' if WeBot writes to one `.env` while the collector later reads another. SMI sets a per-identity `SMI_WEBOT_ENV_FILE`; each identity must have a unique file.

## Safe recovery sequence

For the target identity only:

1. stop/disable any other WeChat identity temporarily;
2. verify there is only one `Weixin.exe` / `WeChat.exe` process family;
3. verify the target external WeBot checkout contains `native\windows\wx_key.dll`;
4. run `scripts\diagnose-webot-key.ps1` and inspect the process/env/log findings;
5. in WeBot, trigger its built-in automatic extraction;
6. if it asks for restart, **exit WeChat from the tray**, wait until the process is gone, then reopen and log in;
7. wait for the built-in flow to report success or an explicit timeout/error;
8. after success, verify only that the selected WeBot env contains a 64-hex `WCDB_KEY` — the doctor reports presence/shape only and never prints the key;
9. configure the SMI instance's exact `SMI_WECHAT_WXID_DIR`;
10. start that account's collector and verify ingestion before onboarding the next account.

Do not paste the WCDB key into chat, GitHub issues, logs, screenshots or the shared SMI `.env`.

## Log phrases worth checking

The external WebBot log can distinguish failure stages. Look for phrases equivalent to:

- DLL load failure / missing dependency;
- WeChat process detected;
- direct extraction failed;
- waiting for WeChat exit;
- waiting for login;
- installing hook;
- hook install failed;
- waiting for data/key;
- no valid key observed before timeout;
- key captured successfully.

Run:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\diagnose-webot-key.ps1 `
  -WebotRoot D:\Sera\deps\webot `
  -ExpectedWindowsUser SeraWechat01
```

The diagnostic script intentionally does not reveal key material.
