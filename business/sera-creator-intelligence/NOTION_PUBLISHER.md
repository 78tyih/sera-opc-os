# Notion Publisher Contract — Sera Creator Intelligence

Notion is the cloud reading/dashboard layer for `sera-creator-intelligence`.

Machine truth remains the validated JSON/JSONL bundle. Publishing to Notion happens **after** validation and must be idempotent.

## Target Structure

Expected Notion workspace structure:

- `Sera Creator Intelligence｜博主视频学习系统`
  - `Creator Intelligence Index`
  - `Creator Video Knowledge Base`

Do not hardcode workspace/database IDs in the public repository.

At runtime, discover them by exact title through the connected Notion MCP/API, then cache the resolved IDs in a local non-Git runtime file such as:

`~/.sera/creator-intelligence/notion.json`

Suggested local config:

```json
{
  "root_page_id": "...",
  "creator_data_source_id": "...",
  "video_data_source_id": "...",
  "resolved_at": "ISO-8601"
}
```

Never commit Notion tokens, API keys, cookies, or credentials.

---

## Publish Gate

Before any Notion write:

1. Requested analysis scope is complete or explicitly partial.
2. Required JSON files parse.
3. `scripts/validate_bundle.py <creator-root>` returns PASS, unless the run explicitly records a validator limitation.
4. Source provenance is present.
5. Fact / interpretation / prediction separation is present.

If these conditions fail, do not publish a page as `reviewed`.

---

## Video Database Mapping

Target database: `Creator Video Knowledge Base`.

One Notion row/page per canonical content item.

Primary dedupe key: `Video ID`.

If `Video ID` is unavailable, fallback to canonical source URL.

### Property mapping

| Notion property | Source |
|---|---|
| Title | video title |
| Creator | creator/channel name |
| Platform | YouTube / Podcast / Course / Other |
| Video ID | canonical content/video id |
| URL | canonical source URL |
| Published | publication date |
| Duration | human-readable duration |
| Topics | normalized topic list |
| Main Thesis | `main_thesis` |
| Knowledge Score | `scores.knowledge_score` |
| Personal Relevance | `scores.personal_relevance` |
| Watch Verdict | `watch_verdict.verdict` |
| Confidence | `watch_verdict.confidence` |
| Transcript Source | provenance/transcript source |
| Status | inventory / transcript_ready / analyzed / reviewed / failed |
| Processed At | analysis timestamp |

### Page body

Render the human-readable analysis, not raw JSON.

Recommended order:

1. 30 秒看懂 / TL;DR
2. Main Thesis
3. Key Takeaways
4. Core Claims
5. Evidence
6. Reasoning Chain
7. Hidden Assumptions
8. Fact / Interpretation / Prediction
9. Critical Analysis / Verification Needed
10. Best Segments / Timeline
11. Knowledge Score breakdown
12. Watch Verdict + reason
13. Related Concepts
14. Source / Transcript provenance

Raw full transcripts should normally remain in the source corpus rather than being duplicated into the Notion page body. Link or reference them when available.

---

## Creator Database Mapping

Target database: `Creator Intelligence Index`.

One row/page per creator/channel.

Primary dedupe key: `Channel ID` when available; fallback to canonical Channel URL.

### Property mapping

| Notion property | Source |
|---|---|
| Creator | creator name |
| Platform | platform |
| Channel URL | canonical creator/channel URL |
| Channel ID | platform-specific channel id |
| Total Items | inventory total |
| Analyzed Items | count with valid intelligence JSON |
| Must Watch | count with verdict `must_watch` |
| Average Score | average Knowledge Score over analyzed items |
| Status | inventory / active / reviewed / paused / failed |
| Primary Topics | top normalized creator topics |
| Last Sync | most recent inventory/refresh timestamp |
| Report Version | Creator Report schema/version |

### Creator page body

Render the current Creator Intelligence Report:

- Executive Summary
- Content Distribution
- Top Must Watch
- Best Videos by Topic
- Evergreen Library
- Recurring Ideas
- Most Repeated Ideas / Redundancy
- Idea Evolution
- Contradictions
- Evidence Style
- Argument Style
- Prediction Track Record
- Coverage / Data Quality

Update the same page on subsequent refreshes. Do not create a new page every run.

---

## Idempotency Rules

### Video item

Before create:

1. Query `Creator Video Knowledge Base` by `Video ID`.
2. If found, update that page.
3. If not found, create it.
4. Never create duplicate rows for the same Video ID.

### Creator item

Before create:

1. Query `Creator Intelligence Index` by `Channel ID` or Channel URL.
2. If found, update properties and Creator Report body.
3. If not found, create it.

### Retry safety

A retry must be safe after interruption. Writes should be item-level and resumable.

---

## Status Rules

- `inventory`: metadata only.
- `transcript_ready`: transcript acquired/normalized, analysis not yet complete.
- `analyzed`: validated analysis exists and has been published.
- `reviewed`: human or explicit review gate accepted the analysis.
- `failed`: processing/publishing failed; error must be recorded locally.

Do not mark smoke-test output `reviewed` automatically.

---

## Runtime Modes

### Native Notion connector/MCP available

Discover the databases by exact title, fetch schemas, then publish directly.

### Notion connector unavailable

Do not block content analysis. Emit a local publish queue:

`publish/notion_publish_queue.jsonl`

Each line should contain:

```json
{
  "entity_type": "video|creator",
  "dedupe_key": "video_id or channel_id",
  "properties": {},
  "markdown_body_path": "...",
  "status": "pending"
}
```

A later Agent with Notion access can drain the queue idempotently.

---

## Batch Publish Order

For a channel run:

1. Publish/update analyzed video pages.
2. Recompute creator aggregate statistics from validated local JSON.
3. Publish/update the Creator page.
4. Write local publish audit log.

Suggested audit file:

`publish/notion_publish_log.jsonl`

Record at least:

- entity type
- dedupe key
- Notion page id/url if available
- action: create/update/skip/fail
- timestamp
- error if any

---

## First Benchmark

For `一个狠人`, publish only the 10-item Smoke Test first.

Expected result after the first successful sample:

- 10 rows/pages in `Creator Video Knowledge Base`.
- 1 updated row/page in `Creator Intelligence Index`.
- `Analyzed Items = 10`.
- `Must Watch`, `Average Score`, topics and Creator Report calculated from those 10 items only.
- Full 755-item backfill remains blocked until review approval.
