# Acquisition Benchmark — 一个狠人 10-Video Sample

Purpose: choose the actual Source Acquisition stack before any 755-item backfill.

This benchmark tests acquisition only. It does **not** require Creator Intelligence analysis, scoring or Notion publishing.

## Sample

Use exactly these 10 public videos:

1. `27t1tZaNsdU`
2. `eEp47vWKUB8`
3. `KH3mi2h8vw8`
4. `-vLc3qXoVBs`
5. `3GmlSvWFEDE`
6. `Lw-0bdr7yk0`
7. `tx0JT4ie_aw`
8. `hdzWq6k0xm0`
9. `_tpvhmZvR0A`
10. `0lzcNMe5dOk`

Exclude subscriber-only `7mvtItF_hTs`.

## Providers Under Test

Test only providers for which credentials/runtime access are actually available.

Candidate matrix:

- Supadata
- ScrapeCreators
- Apify transcript Actor
- Firecrawl transcript/page extraction
- Jina Reader transcript DOM extraction
- Firecrawl audio + ASR
- Local/Residential native caption/yt-dlp fallback
- Local/Residential temporary audio + ASR fallback

A missing API key is `not_configured`, not a provider failure.

## Output

Write:

```text
benchmark/
├── acquisition-results.json
├── acquisition-results.csv
├── provider-summary.json
├── PROVIDER_BENCHMARK_REPORT.md
└── raw/
    └── <provider>/<video_id>.*
```

The benchmark must not overwrite canonical production transcripts.

## Per Attempt Fields

For each `video × provider` attempt record:

- video_id
- provider
- source_kind
- status
- http_status if available
- latency_ms
- cost_units/credits if knowable
- language
- segment_count
- text_length
- timestamp_coverage
- estimated_content_coverage
- suspected_mismatch
- error_class
- error_message
- retrieved_at

## Success Definition

`success` requires:

- correct Video ID/source;
- non-empty transcript;
- no strong mismatch signal;
- language usable for analysis;
- provenance recorded.

A transcript without timestamps can still succeed for summarization, but it receives lower timestamp-quality score and cannot be treated as equivalent to native timestamped output.

## Mismatch Detection

For every successful transcript, verify at least two of:

- provider-returned Video ID equals requested ID;
- title/channel metadata matches known catalog metadata;
- transcript contains expected language/topic signals without obvious unrelated content;
- duration/timestamp range is plausible for known video duration.

If mismatch is suspected, classify `content_mismatch` and exclude that transcript from provider success rate.

## Provider Metrics

Calculate per provider:

```text
configured videos
attempted videos
successful videos
partial videos
failed videos
success rate
content mismatch rate
timestamp-full rate
median latency
mean latency
known credits/cost
native transcript count
ASR count
```

## Selection Score

Recommended evaluation score /100:

| Dimension | Weight |
|---|---:|
| Success rate | 35 |
| Content correctness / mismatch safety | 20 |
| Timestamp quality | 15 |
| Transcript coverage/quality | 15 |
| Cost efficiency | 10 |
| Latency | 5 |

Do not use the score mechanically if a provider has a material mismatch risk.

## Selection Result

Final report must choose:

```text
Primary Transcript Provider
Backup Transcript Provider
Managed Audio Fallback
Local / Residential Fallback
```

Example decision shape:

```json
{
  "primary": "supadata",
  "backup": "scrapecreators",
  "managed_audio": "firecrawl",
  "local_fallback": "mac-or-serawin",
  "reason": "..."
}
```

This example is illustrative only; use observed benchmark data.

## Stop Rule

After the 10-video acquisition benchmark:

STOP.

Do not:

- analyze all 10 with LLM unless separately requested;
- run full 755-item backfill;
- promote a provider without showing benchmark evidence.

## Promotion Gate

A source stack may move to production only after:

1. at least one transcript provider succeeds on a meaningful portion of the 10-video sample;
2. no unresolved content-mismatch issue exists for the selected Primary;
3. an independent Backup or Local fallback exists;
4. transcript JSON can be normalized to `schemas/transcript-acquisition.schema.json`.
