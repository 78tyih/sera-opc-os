# Source Execution Router — Sera Creator Intelligence

## Why this exists

The first real `一个狠人` smoke test on 2026-08-31 proved that YouTube source acquisition cannot depend on public-cloud runners alone.

Observed on GitHub Actions / Azure IPs:

- public transcript endpoint → HTTP 403;
- `youtube-transcript-api` → `RequestBlocked` for cloud-provider IP;
- `yt-dlp` captions → no usable caption files;
- BgUtils PO Token Provider started successfully, but audio requests via `mweb`, `web_safari`, `android_vr`, `web_embedded`, and `tv` all returned `Sign in to confirm you’re not a bot`;
- ASR itself was never the blocker: source audio could not be acquired.

Therefore **Cloud is a convenience execution target, not the authority for YouTube acquisition**.

---

## Routing order

```text
Metadata / Inventory
  ↓
YouTube human/auto caption
  ↓ unavailable or IP-blocked
Trusted indexed transcript / summary source
  ↓ insufficient
Cloud audio acquisition
  ↓ bot/login/IP gate
Local / Residential Runner
  ↓
Ephemeral audio → ASR
  ↓
Validated Transcript
  ↓
Video Intelligence
```

### Execution targets

1. `cloud` — GitHub Actions / generic public cloud. Good for metadata, validation, rendering, aggregation. Best-effort only for YouTube media.
2. `local-mac` — user Mac on a normal residential/consumer network. Preferred fallback for YouTube source acquisition.
3. `serawin` — Windows workstation through the existing Sera compute/control plane when it has normal YouTube access.
4. `other-residential` — an explicitly authorized residential execution target.
5. `web-fallback` — public indexed transcript/summary pages when provenance and coverage are sufficient.

---

## Hard safety rules

- Never commit YouTube/Google cookies, tokens, passwords, browser profiles, or authentication exports to Git.
- Do not inject a user account cookie into GitHub Actions merely to bypass `Sign in to confirm you’re not a bot`.
- If an authenticated local browser is required, keep authentication local and use the minimum necessary scope.
- Temporary audio is deleted immediately after ASR. Raw video is not retained by default.
- A blocked source is a valid pipeline outcome. Do not hallucinate Main Thesis / Claims / Evidence to make the run look successful.

---

## Router states

Suggested machine-readable acquisition states:

```text
metadata_ready
caption_available
caption_blocked
web_fallback_available
web_fallback_insufficient
cloud_audio_available
cloud_ip_blocked
local_runner_required
asr_ready
transcript_validated
source_failed
```

Recommended error classification:

- `youtube_cloud_ip_blocked`
- `youtube_login_gate`
- `caption_unavailable`
- `member_only`
- `private_or_deleted`
- `asr_failed`
- `web_fallback_low_coverage`

---

## Retry policy

Do not repeatedly retry the same execution target after a deterministic provider/IP gate.

Example:

```text
RequestBlocked on cloud provider IP
→ mark cloud_ip_blocked
→ route to local/residential
→ do not burn retries on alternate cloud clients
```

PO Token errors may justify one provider/client retry. A consistent `Sign in to confirm you’re not a bot` across multiple clients is an execution-target failure, not an ASR failure.

---

## Completion semantics

A Creator Intelligence run can complete as:

- `success` — requested content analyzed with grounded source coverage;
- `partial` — some items analyzed, others explicitly failed;
- `source_blocked` — inventory/metadata exists but source acquisition gate prevented analysis;
- `failed` — pipeline/system failure unrelated to normal source availability.

Never convert `source_blocked` into `success` by scoring title/description-only content as if it were a transcript-backed analysis.

---

## First benchmark evidence

`一个狠人` 10-item smoke set:

- metadata: 10/10 acquired;
- cloud transcript: 0/10;
- cloud audio: 0/10;
- Notion records: 10/10 created with `Status = failed` and no fabricated scores;
- correct next route: local/residential source acquisition.

This benchmark should remain a regression test for the Execution Router.