# Sera Creator Intelligence Acquisition Benchmark

Generated: 2026-08-31T09:40:47Z

Scope: acquisition only for the fixed 10-video sample. No intelligence analysis, scoring, Notion publishing, or backfill was run.

## Provider Summary

| Provider | Configured | Attempted | Success | Partial | Failed | Success rate | Timestamp-full | Median latency | Known units |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Supadata | 0 | 0 | 0 | 0 | 0 | n/a | n/a | n/a | n/a |
| ScrapeCreators | 10 | 10 | 0 | 0 | 10 | 0.0% | n/a | 2059 ms | 10.0 |
| Apify | 0 | 0 | 0 | 0 | 0 | n/a | n/a | n/a | n/a |
| Firecrawl transcript | 10 | 10 | 0 | 0 | 10 | 0.0% | n/a | 7386 ms | n/a |
| Jina Reader | 10 | 10 | 0 | 0 | 10 | 0.0% | n/a | 6529 ms | n/a |
| youtube-transcript-api | 10 | 10 | 0 | 0 | 10 | 0.0% | n/a | 1386 ms | n/a |
| yt-dlp captions | 10 | 10 | 0 | 0 | 10 | 0.0% | n/a | 3519 ms | n/a |
| Firecrawl audio + ASR | 10 | 10 | 9 | 0 | 1 | 90.0% | 100.0% | 125952 ms | n/a |
| Local yt-dlp audio + ASR | 10 | 10 | 10 | 0 | 0 | 100.0% | 100.0% | 95759 ms | n/a |

## Per-video Matrix

| Video ID | Supadata | ScrapeCreators | Apify | Firecrawl transcript | Jina Reader | youtube-transcript-api | yt-dlp captions | Firecrawl audio + ASR | Local yt-dlp audio + ASR |
|---|---|---|---|---|---|---|---|---|---|
| `27t1tZaNsdU` | NC | F (no_transcript) | NC | F (no_transcript) | F (no_transcript) | F (blocked) | F (no_transcript) | F (blocked) | S (688) |
| `eEp47vWKUB8` | NC | F (no_transcript) | NC | F (no_transcript) | F (no_transcript) | F (blocked) | F (no_transcript) | S (740) | S (745) |
| `KH3mi2h8vw8` | NC | F (no_transcript) | NC | F (no_transcript) | F (no_transcript) | F (blocked) | F (no_transcript) | S (716) | S (676) |
| `-vLc3qXoVBs` | NC | F (no_transcript) | NC | F (no_transcript) | F (no_transcript) | F (blocked) | F (no_transcript) | S (729) | S (653) |
| `3GmlSvWFEDE` | NC | F (no_transcript) | NC | F (no_transcript) | F (no_transcript) | F (blocked) | F (no_transcript) | S (739) | S (693) |
| `Lw-0bdr7yk0` | NC | F (no_transcript) | NC | F (no_transcript) | F (no_transcript) | F (blocked) | F (no_transcript) | S (87) | S (80) |
| `tx0JT4ie_aw` | NC | F (no_transcript) | NC | F (no_transcript) | F (no_transcript) | F (blocked) | F (no_transcript) | S (497) | S (471) |
| `hdzWq6k0xm0` | NC | F (no_transcript) | NC | F (no_transcript) | F (no_transcript) | F (blocked) | F (no_transcript) | S (266) | S (277) |
| `_tpvhmZvR0A` | NC | F (no_transcript) | NC | F (no_transcript) | F (no_transcript) | F (blocked) | F (no_transcript) | S (422) | S (455) |
| `0lzcNMe5dOk` | NC | F (no_transcript) | NC | F (no_transcript) | F (no_transcript) | F (blocked) | F (no_transcript) | S (437) | S (584) |

Legend: S = success, P = partial, F = failed, NC = not configured; parentheses show segment count or failure taxonomy.

## Failure Taxonomy

- ScrapeCreators: no_transcript: 10
- Firecrawl transcript: no_transcript: 10
- Jina Reader: no_transcript: 10
- youtube-transcript-api: blocked: 10
- yt-dlp captions: no_transcript: 10
- Firecrawl audio + ASR: blocked: 1

## Recommendation

- Primary Transcript Provider: `none qualified`
- Backup Transcript Provider: `none qualified`
- Managed Audio Fallback: `firecrawl_audio`
- Local / Residential Fallback: `local_audio_asr`
- Promotion gate: `fail`

No managed transcript provider succeeded; keep managed Primary/Backup unpromoted and use the observed local/residential fallback.

## Validation Notes

- Fixed sample IDs: 10
- Attempt records: 90 / 90
- Suspected content mismatches: 0
- Execution host: local Mac; network mode: macOS system proxy.
- ASR model: faster-whisper-base.
- Every successful normalized transcript is stored beside its sanitized raw provider artifact.
- Temporary audio and signed media URLs were deleted or redacted immediately after ASR.
