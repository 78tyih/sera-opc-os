# Benchmark Architecture Map

本文件记录 `sera-creator-intelligence` 的设计来源。只吸收架构/产品模式，不复制第三方代码。

## 1. FlorianBruniaux/youtube-video-insights

Borrow:
- channel → VTT/metadata → per-video structured JSON → aggregate report
- JSON as source of truth; Markdown rendered from JSON
- atomic/idempotent output
- SQLite/FTS5 timestamp passage index
- read-only MCP access
- deterministic operations separated from LLM analysis

Do not blindly copy:
- fixed transcript truncation strategy
- subtitle-only limitation when ASR is genuinely needed

Source: https://github.com/FlorianBruniaux/youtube-video-insights

## 2. coleam00/cole-medin-knowledge-base

Borrow:
- “idea, not video” as durable knowledge unit
- bulk two-pass: Extract → Canonicalize → Write
- incremental read-before-write
- typed bidirectional links
- contradictions explicitly flagged
- lint/index regeneration after ingest

Source: https://github.com/coleam00/cole-medin-knowledge-base

## 3. wjgoarxiv/youtube-digest-skill

Borrow:
- TL;DR first
- Key Takeaways
- timestamped Core Assertions
- Topic Timeline
- Quick Triage
- environment-aware transcript acquisition tiers

Upgrade in Sera:
- Assertions become Claim/Evidence/Reasoning/Assumption objects
- Fact/Interpretation/Prediction are explicitly separated

Source: https://github.com/wjgoarxiv/youtube-digest-skill

## 4. n8n workflow #9268

Borrow:
- scheduled monitoring
- source list + user relevance criteria
- recent-video discovery
- metadata/stats enrichment
- stable-ID dedupe
- summary + relevance score + reasoning
- one failure continues batch

Keep n8n at orchestration layer; do not put canonical knowledge logic in n8n.

Source: https://n8n.io/workflows/9268-youtube-channel-monitor-with-video-stats-ai-transcription-and-summarization/

## 5. Summario

Borrow:
- progressive consumption: quick summary before full detail
- per-channel analysis preferences
- Watch/Skip decision as first-class output
- verdict + confidence + reasoning
- clickable/timestamped timeline UX

Sera verdict vocabulary:
- must_watch
- worth_watching
- skim
- note_only
- skip

Source: https://summario.net/

## 6. ckryptickunal/Founder-Book

Borrow:
- self-updating source watch list
- newest-first incremental discovery
- known-item early stop
- lockfile + cooldown
- failure tolerance
- Markdown wiki + raw transcript RAG
- grounded answers with citations

Avoid coupling core protocol to Gemini/Tor implementation choices.

Source: https://github.com/ckryptickunal/Founder-Book

## 7. 0xchamin/mcptube

Borrow:
- CLI/service/MCP separation
- MCP passthrough: server returns grounded data, client model reasons
- cross-video search and synthesis
- frame extraction on demand
- multi-provider LLM compatibility
- metadata/transcript/frame as separate capabilities

Sera V1 keeps SQLite FTS5 primary; vector storage is optional.

Source: https://github.com/0xchamin/mcptube

## 8. n8n workflow #3408

Borrow:
- playlist/single video corpus ingestion
- retrieval + conversational follow-up
- persistent session context
- batch-to-chat workflow

Sera change:
- Vector DB is optional, not mandatory
- conversation state must not replace durable content state

Source: https://n8n.io/workflows/3408-ai-youtube-playlist-and-video-analyst-chatbot/

---

## Sera Unified Capability Matrix

| Layer | Canonical pattern |
|---|---|
| Discovery | yt-insights + Founder Book + n8n #9268 |
| Transcript | youtube-digest + yt-insights |
| Single-video digest | youtube-digest + Summario |
| Argument mining | Sera extension |
| Watch scoring | Summario + n8n #9268 |
| Vision | mcptube |
| Cross-video synthesis | yt-insights + mcptube |
| Canonical knowledge | Cole Medin KB + Founder Book |
| Retrieval/Ask | yt-insights FTS5 + mcptube/Founder Book RAG |
| Monitoring | Founder Book + n8n #9268 |
| Portable agent access | SKILL contract + MCP-compatible data surface |
