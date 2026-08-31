# Source Acquisition V2 — Sera Creator Intelligence

This document defines the provider-agnostic acquisition layer for `sera-creator-intelligence`.

The purpose is to reliably obtain a timestamped transcript or, if necessary, temporary audio from a creator source without coupling downstream intelligence logic to one scraper, one network, or one vendor.

## Core Principle

Downstream analysis MUST NOT depend on provider-specific response shapes.

Every acquisition attempt is normalized into one `Transcript Acquisition Result` and one failure taxonomy.

```text
Source URL
   ↓
Acquisition Router
   ↓
Provider Adapter(s)
   ↓
Transcript / Audio
   ↓
Normalize
   ↓
Transcript Acquisition Result
   ↓
Creator Intelligence
```

## Provider Strategy

### Tier P0 — Managed transcript/audio providers

1. **Firecrawl**
   - Use transcript/page extraction when it can expose YouTube transcript content.
   - Use `audio` extraction as the preferred managed audio fallback when a transcript is unavailable.
   - Audio URLs are temporary; download immediately when ASR is required, then delete temporary media after transcription.

2. **Supadata**
   - Primary structured transcript candidate.
   - Prefer timestamped transcript responses.
   - Treat provider-generated ASR as a distinct provenance source from native captions.

### Tier P1 — Managed transcript fallbacks

3. **ScrapeCreators**
   - Dedicated YouTube transcript endpoint.
   - Good fallback when direct YouTube/IP-based methods fail.
   - Preserve provider response language and timestamps.

4. **Apify**
   - Use a transcript-focused Actor with timestamped output and explicit per-video status.
   - Actor identity/version must be recorded because Actors can change independently.

5. **Jina Reader**
   - Browser/DOM extraction fallback.
   - Intended for videos where YouTube exposes `Show transcript` in the rendered UI.
   - Treat DOM text as web transcript provenance, not official API provenance.

### Final fallback — Local / Residential Runner

6. **Mac / SeraWin / residential network**
   - Run `youtube-transcript-api`, `yt-dlp`, or browser automation from a non-datacenter network.
   - If no usable caption exists, acquire temporary audio and run ASR.
   - This fallback exists specifically because cloud/VPS IPs are frequently blocked by YouTube anti-bot systems.

## Default Routing Order

The router should prefer the least expensive, highest-fidelity source first.

```text
A. Native/managed timestamped transcript
   1. Supadata
   2. ScrapeCreators
   3. Apify transcript Actor
   4. Firecrawl/Jina rendered transcript

B. Managed audio fallback
   5. Firecrawl audio → ASR

C. Local/residential fallback
   6. Local native captions / yt-dlp
   7. Local temporary audio → ASR
```

The exact order may be changed by benchmark results. Provider priority is configuration, not hardcoded business logic.

## Transcript Acquisition Result

All providers MUST normalize to this shape before downstream processing:

```json
{
  "schema_version": "1.0",
  "content_id": "youtube-video-id",
  "canonical_url": "https://www.youtube.com/watch?v=...",
  "status": "success|partial|failed",
  "source_kind": "manual_caption|auto_caption|provider_transcript|web_transcript|provider_asr|local_asr",
  "provider": "supadata|scrapecreators|apify|firecrawl|jina|local",
  "provider_version": "optional",
  "language": "zh|en|...",
  "segments": [
    {
      "start": 0.0,
      "end": 3.2,
      "text": "..."
    }
  ],
  "full_text": "...",
  "timestamp_coverage": 1.0,
  "retrieved_at": "ISO-8601",
  "audio": {
    "used": false,
    "temporary": true,
    "provider": null,
    "asr_model": null
  },
  "quality": {
    "coverage": 0.0,
    "language_match": true,
    "timestamp_quality": "full|partial|none",
    "suspected_mismatch": false
  },
  "provenance": {
    "provider_response_id": null,
    "notes": []
  },
  "attempts": []
}
```

## Provider Attempt Record

Every provider attempt must be recorded, even when another provider later succeeds.

```json
{
  "provider": "supadata",
  "started_at": "ISO-8601",
  "finished_at": "ISO-8601",
  "status": "success|empty|blocked|rate_limited|auth_error|provider_error|mismatch|timeout",
  "http_status": 200,
  "latency_ms": 1234,
  "cost_units": 1,
  "error_code": null,
  "error_message": null
}
```

## Failure Taxonomy

Normalize provider-specific errors into:

- `bad_request` — malformed/obsolete endpoint or invalid parameters.
- `auth_error` — invalid/missing API credentials.
- `blocked` — YouTube/provider bot challenge, IP restriction, 403, `RequestBlocked`, login challenge.
- `rate_limited` — 429/provider quota/rate limiting.
- `not_found` — video no longer exists or provider cannot resolve it.
- `no_transcript` — video exists but no transcript/caption returned.
- `audio_unavailable` — transcript absent and provider cannot obtain audio.
- `timeout` — provider exceeded runtime budget.
- `provider_error` — 5xx/unknown provider failure.
- `content_mismatch` — returned transcript does not match requested video.
- `language_mismatch` — transcript exists but does not match requested/known language.
- `partial` — usable content exists but coverage/timestamps are incomplete.

`content_mismatch` is a hard gate: never pass mismatched text into Creator Intelligence.

## Quality Gates

A transcript is acceptable for full Argument Intelligence only if:

1. Requested Video ID / canonical URL matches returned content.
2. Transcript is non-empty.
3. Language is known or reasonably detected.
4. Coverage is sufficient for the intended task.
5. Timestamp coverage is recorded.
6. Provenance identifies provider and source type.

If coverage is incomplete, mark `status=partial` and restrict downstream claims accordingly.

## Anti-Hallucination Rule

Title, description, comments, search snippets, public mirrors and external summaries may help with metadata enrichment and acquisition diagnostics, but they MUST NOT silently replace a missing transcript.

If no acceptable transcript exists:

- keep `Video Intelligence` blocked;
- do not fabricate Main Thesis;
- do not calculate Knowledge Score;
- do not produce Watch Verdict;
- publish acquisition status/failure only.

## Audio Rules

- Audio is a transport fallback, not a permanent knowledge asset.
- Download signed/temporary audio immediately if ASR is needed.
- Record provider, retrieval timestamp and ASR model.
- Delete temporary audio after successful ASR unless explicitly retained for debugging.
- Raw transcript remains separate from AI interpretation.

## Provider Configuration

Secrets are runtime-only.

Suggested environment variables:

```text
FIRECRAWL_API_KEY
SUPADATA_API_KEY
SCRAPECREATORS_API_KEY
APIFY_API_TOKEN
JINA_API_KEY              # optional depending on usage
```

Never commit API keys, cookies, proxy credentials or signed media URLs.

Suggested runtime config (not committed):

```json
{
  "providers": [
    "supadata",
    "scrapecreators",
    "apify",
    "firecrawl_transcript",
    "jina",
    "firecrawl_audio",
    "local"
  ],
  "stop_on_first_acceptable": true,
  "minimum_coverage": 0.9,
  "prefer_native_timestamps": true
}
```

## Source Truth

The normalized transcript JSON is the machine source-of-truth for downstream analysis.

Provider raw responses may be cached for debugging, but downstream Creator Intelligence MUST consume the normalized contract rather than provider-specific payloads.

## Scaling Rule

Do not choose a provider by marketing claims alone.

For every new source type or major provider change:

1. run `ACQUISITION_BENCHMARK.md`;
2. compare success rate, timestamp quality, mismatch rate, latency and cost;
3. promote the best provider to Primary;
4. retain at least one independent Backup plus Local/Residential fallback.
