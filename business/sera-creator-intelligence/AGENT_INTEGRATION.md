# Agent Integration — Sera Creator Intelligence

`sera-creator-intelligence` is model-agnostic. The protocol is defined by `SKILL.md`, Source Acquisition V2, JSON schemas, templates and validation rules; no single LLM or scraper provider is authoritative.

## Native Skill Runtimes

For WorkBuddy / Codex / Trae / Claude Code / Cursor, expose or install:

`business/sera-creator-intelligence/`

The platform should read `SKILL.md` when intent matches Creator/Channel analysis, transcript learning, video triage, argument breakdown, creator knowledge-base generation or monitoring.

## Generic Agents — DeepSeek / Kimi / other models

If the runtime has repository/file access but no native Skill loader:

1. Read `SKILL.md` completely.
2. Read `SOURCE_ACQUISITION_V2.md` before any YouTube transcript/audio acquisition.
3. Read the relevant schemas:
   - `schemas/transcript-acquisition.schema.json`
   - `schemas/video-intelligence.schema.json`
   - `schemas/creator-intelligence.schema.json`
4. Read only the output template needed for the task.
5. If Notion/cloud publishing is requested, also read `NOTION_PUBLISHER.md`.
6. Write normalized transcript JSON before downstream analysis.
7. Write Video/Creator JSON source-of-truth before rendering Markdown.
8. Run validators before claiming completion or publishing reviewed knowledge.

Do not fork the shared contract into a provider-specific permanent format.

## Source Acquisition V2

YouTube acquisition must no longer assume that cloud `youtube-transcript-api` or `yt-dlp` will work.

Provider candidates:

```text
Supadata
ScrapeCreators
Apify transcript Actor
Firecrawl transcript/page extraction
Jina Reader transcript DOM extraction
Firecrawl audio → ASR
Local / Residential Runner
```

Every provider response must normalize to:

`schemas/transcript-acquisition.schema.json`

The downstream Agent consumes the normalized result, not a vendor payload.

### Acquisition Gate

Do not run Main Thesis / Claims / Evidence / Score / Watch Verdict unless an acceptable transcript is available.

Title, description, search snippets, public mirrors and comments may enrich metadata but may not silently replace a missing transcript.

### Provider Benchmark

Before a full-channel backfill or after a material provider change, follow:

`ACQUISITION_BENCHMARK.md`

For the first benchmark use the canonical 10-video `一个狠人` sample.

The benchmark must choose:

- Primary Transcript Provider
- Backup Transcript Provider
- Managed Audio Fallback
- Local / Residential Fallback

Do not choose by marketing claims alone.

## Sera Router

Central route id: `creator-intelligence`.

Expected triggers include:

- 分析博主 / 博主分析 / 频道分析
- 哪些视频最值得看
- 视频总结 / 视频拆解 / 视频文字稿
- 论点论据
- Creator Intelligence / Creator Analysis
- YouTube 知识库 / 博主知识库
- 监控博主

The route must precede generic video-production routing.

## Invocation Contract

```json
{
  "skill": "sera-creator-intelligence",
  "mode": "inventory|acquisition-benchmark|video|triage|channel|refresh|ask|rebuild-report",
  "source": "channel/video/playlist/local-corpus",
  "output_root": "optional path",
  "analysis_focus": "optional",
  "max_items": null,
  "publish_targets": ["markdown", "notion"]
}
```

`acquisition-benchmark` is acquisition-only and must stop before LLM content analysis unless explicitly requested.

## Notion Publishing

When `notion` is requested:

1. Read `NOTION_PUBLISHER.md`.
2. Discover exact databases by title through connected Notion MCP/API; do not hardcode public-repo IDs.
3. Cache resolved IDs only in local non-Git runtime state.
4. Dedupe videos by `Video ID` and creators by `Channel ID`/canonical URL.
5. Create when missing; update when existing.
6. Publish video pages first, recompute creator aggregates second, then update Creator page/report.
7. Record a local publish audit log.
8. If Notion is unavailable, emit `publish/notion_publish_queue.jsonl` and continue.

## Completion Contract

An Agent may claim completion only when:

- requested scope has explicit coverage count;
- acquisition attempts/failures are recorded instead of hidden;
- normalized transcript JSON parses when acquisition succeeded;
- content mismatch is explicitly gated;
- required Video/Creator JSON parses;
- claims are grounded to source/timestamp where available;
- Fact / Interpretation / Prediction are separated;
- Watch Verdict contains reason and confidence;
- bundle validator passes, or limitation is explicitly reported;
- if Notion publishing was requested, each item has publish status (`create/update/skip/fail/queued`).

## Benchmark Before Smoke Test

For `一个狠人`:

1. Run `ACQUISITION_BENCHMARK.md` first if no production provider stack has been selected.
2. STOP and review provider results.
3. Only after a source stack is promoted should `SMOKE_TEST.md` run Transcript → Intelligence → Score → Notion.
4. Never launch the 755-item backfill before the 10-item analysis sample is reviewed.
