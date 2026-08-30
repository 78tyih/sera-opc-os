---
name: sera-creator-intelligence
version: 0.1.0
author: Sera
category: business
status: active
compatible:
  - WorkBuddy
  - Codex
  - Trae
  - Claude-Code
  - Cursor
  - DeepSeek
  - Kimi
purpose: 将 YouTube 博主、播客、访谈、课程等持续内容源编译成可浏览、可评分、可检索、可持续更新的 Creator Intelligence 知识系统。
description: |
  当用户要求分析一个博主/频道/视频库、抓取并整理视频文字稿、判断哪些视频最值得看、拆解视频论点论据、生成频道级内容分布与思想报告、把内容沉淀到 Obsidian/Markdown/JSON/SQLite，或持续监控新内容时调用。
  不用于视频制作、剪辑、数字人、B-roll 或单纯下载视频文件。
---

# Sera Creator Intelligence

## Purpose

把“内容消费”变成“知识编译”。输入一个 Creator / Channel / Playlist / 单视频，输出：

1. 完整内容目录与覆盖率；
2. 可溯源 Transcript；
3. 单内容 Intelligence（摘要、主题、Timeline、关键片段）；
4. Argument Intelligence（论点、论据、推理、假设、预测）；
5. Knowledge Score + Watch Verdict；
6. 跨视频 Topic / Recurring Ideas / Evolution / Contradictions；
7. Canonical Concepts / Entities / Claims / Predictions；
8. Creator Intelligence Report；
9. Obsidian/Markdown 阅读层 + JSON 真相源 + 可重建检索层；
10. 增量监控与重复处理防护。

这个 Skill 是 **Creator Compiler**，不是普通 YouTube Summarizer。

---

## When to use

触发示例：

- “分析这个 YouTube 博主过去都讲了什么”
- “把这个频道所有视频做成笔记”
- “哪些视频最值得看？”
- “把每期视频的论点、论据、推理拆出来”
- “生成这个博主的内容分布和思想地图”
- “把这个频道沉淀进 Obsidian”
- “每天监控这个博主的新视频并更新知识库”
- “YouTube channel analysis / creator intelligence / transcript digest”

不要触发：

- 用户要制作/剪辑/渲染视频 → `sera-video-pipeline`
- 用户只要下载媒体文件 → 使用下载工具，不进入本 Skill
- 用户只要普通网页设计 → `sera-design-studio`

---

## Core Architecture

```text
Source Registry
    ↓
Discover / Inventory
    ↓
Acquire Raw Content
    ↓
Normalize Transcript
    ↓
Single Content Intelligence
    ↓
Argument Intelligence
    ↓
Quality / Relevance Scoring
    ↓
Cross-Content Synthesis
    ↓
Canonicalize Knowledge
    ↓
Index / Search / Ask
    ↓
Obsidian / Reports / Context Hub
    ↓
Incremental Monitor
```

### 三层存储原则

```text
JSON / JSONL  = Source of Truth
Markdown      = Human Reading Layer
SQLite FTS5   = Derived Retrieval Layer
```

Vector DB（Qdrant/Chroma）不是 V1 必需品。只有关键词/FTS 检索明显不够时再启用。

---

## Modes

### 1. `inventory`
只建立频道/Creator 内容目录，不做 LLM 分析。

适合第一次接入新博主。

### 2. `video`
分析单条视频：Transcript → Intelligence → Argument → Score → Note。

### 3. `triage`
批量判断哪些内容值得优先处理/观看。输出排序与 Verdict。

### 4. `channel`
批量处理 Creator 内容，并生成跨视频 Creator Report。

### 5. `refresh`
只发现和处理上次同步后的新增内容；禁止重跑已完成内容。

### 6. `ask`
从已经建立的 Creator Corpus 中检索并回答问题，返回 Source + Timestamp。

### 7. `rebuild-report`
不重新抓取 Transcript，只用现有 JSON 重建 Creator Report。

---

## Inputs

最少一个：

- Creator/Channel URL
- Playlist URL
- Video URL / Video ID
- 已存在的 `videos.json` / CSV
- 本地 Transcript 目录

可选：

- `creator_name`
- `output_root`
- `language`
- `personal_relevance_profile`
- `analysis_focus`
- `mode`
- `max_items`
- `since`
- `vision_policy`
- `model_policy`

如果用户已经提供明确频道、输出路径和范围，不重复询问。

---

## Standard Output Bundle

```text
<creator>/
├── 00_Creator_Profile.md
├── 01_Video_Catalog.md
├── 02_Best_Videos.md
├── 03_Topic_Map.md
├── 04_Idea_Evolution.md
├── 05_Predictions.md
├── reports/
│   ├── CREATOR_INTELLIGENCE_REPORT.md
│   └── creator-intelligence.json
├── catalog/
│   ├── videos.json
│   └── videos.csv
├── raw/
│   ├── metadata/
│   ├── subtitles/
│   └── transcripts/
├── intelligence/
│   └── videos/
│       ├── <video_id>.json
│       └── <video_id>.md
├── knowledge/
│   ├── concepts/
│   ├── entities/
│   ├── claims/
│   └── predictions/
├── state/
│   ├── processed.jsonl
│   ├── failures.jsonl
│   └── sync.json
└── .index/
    └── search-v1.sqlite3
```

Raw 是证据层；Intelligence 是单条分析层；Knowledge 是跨内容的长期知识层。

---

# Execution Protocol

## Stage 0 — Preflight

1. 确认输入类型：channel / playlist / video / existing corpus。
2. 检查已有产物与 `state/processed.jsonl`，禁止重复做已经成功的工作。
3. 检查运行环境：
   - Python 3
   - `yt-dlp`（优先 metadata/subtitle collector）
   - `youtube-transcript-api`（可选）
   - ffmpeg（仅 ASR/视觉阶段需要）
   - SQLite（Python stdlib 即可）
4. 先 dry-run/preview 采集范围；大规模回填必须可断点续传。
5. 不把 API key/token 写入知识库或 Git。

---

## Stage 1 — Discover / Inventory

原则：**Metadata first, LLM later**。

采集字段至少包含：

```text
content_id / video_id
title
url
published_at
duration
views
likes (if available)
description
content_type
availability
channel_id
creator_id
```

要求：

- 按稳定 ID 去重；
- 建立 `videos.json` 作为目录真相源；
- 区分 public / subscriber_only / private / unavailable；
- 若平台 UI 总数与可枚举内容不一致，必须报告覆盖率和缺口，不得伪造缺失条目；
- Inventory 阶段不运行大模型。

---

## Stage 2 — Acquire Raw Content

Transcript 获取优先级：

```text
1. 官方人工字幕
2. 官方自动字幕
3. 其它可验证字幕轨
4. youtube-transcript-api / yt-dlp fallback
5. Web transcript fallback（必须记录来源）
6. ASR fallback（仅无字幕且任务确有必要）
```

ASR 规则：

- 只临时下载音频；
- ASR 完成后默认删除临时媒体；
- 不永久保存整个频道的视频文件；
- 标注 `transcript_source=asr` 与模型；
- 不允许不同文字源静默覆盖原始资料。

Raw Transcript 必须带 Provenance：

```json
{
  "source_type": "youtube_auto_caption",
  "language": "zh-Hans",
  "retrieved_at": "ISO-8601",
  "video_id": "...",
  "canonical_url": "..."
}
```

---

## Stage 3 — Normalize Transcript

目标是可读性，不是改写。

允许：

- 去 VTT 滚动字幕重复；
- 恢复标点/段落；
- 合并碎片；
- 保留 timestamp segment；
- 纠正明显格式问题。

禁止：

- 改变作者观点；
- 自动补充视频中不存在的事实；
- 把模型推断写进 Raw。

标准 Segment：

```json
{
  "segment_id": 38,
  "start": 421.2,
  "end": 437.8,
  "text": "..."
}
```

所有重要 Claim 应能回指至少一个 timestamp/segment。

---

## Stage 4 — Single Content Intelligence

每条内容必须生成 `schemas/video-intelligence.schema.json` 对应 JSON。

阅读层按 `templates/video-note.md` 渲染。

最少包含：

- 30 秒看懂 / TL;DR
- 3–8 Key Takeaways
- Topic Timeline
- Best Segments
- Main Thesis
- Claims
- Evidence
- Reasoning
- Assumptions
- Predictions
- Concepts / Entities
- Scores
- Watch Verdict
- Provenance

**JSON 先写成功并验证，再渲染 Markdown。Markdown 不作为唯一数据源。**

---

## Stage 5 — Argument Intelligence

这是本 Skill 的核心。

### Claim Types

- `fact`
- `interpretation`
- `opinion`
- `prediction`
- `recommendation`
- `hypothesis`

### Evidence Types

- `quantitative_data`
- `financial_data`
- `policy`
- `research`
- `news`
- `historical_event`
- `case_study`
- `expert_authority`
- `anecdote`
- `visual_chart`
- `analogy`
- `none`

每个重要 Claim 尽量形成：

```text
Evidence
  ↓
Intermediate Inference
  ↓
Hidden Assumption
  ↓
Claim
  ↓
Main Thesis
```

不得把作者的 opinion/prediction 写成已证实 fact。

无法找到论据时显式写：`evidence_type=none`。

---

## Stage 6 — Critical Analysis

每条视频必须区分：

### 已发生事实
只记录视频中陈述的事实性信息。

### 作者判断
作者如何解释事实。

### 未来预测
尚未发生、可在未来验证的判断。

并输出：

- evidence_strength: strong / medium / weak
- hidden_assumptions
- counterarguments
- verification_needed
- internal_consistency

不进行“因为喜欢这个 Creator 就默认正确”的处理。

---

## Stage 7 — Quality & Watch Scoring

### Knowledge Score / 100

| 维度 | 权重 |
|---|---:|
| Insight | 20 |
| Evidence | 15 |
| Evergreen | 20 |
| Novelty | 15 |
| Argument Quality | 15 |
| Density | 15 |

`Personal Relevance` 单独 0–10，不混入客观 Knowledge Score。

### Watch Verdict

- `must_watch`
- `worth_watching`
- `skim`
- `note_only`
- `skip`

每个 Verdict 必须包含：

```json
{
  "verdict": "must_watch",
  "confidence": 0.92,
  "reason": "..."
}
```

不能只给标签，不解释原因。

### Novelty

Novelty 必须相对于同 Creator 现有 corpus 计算/判断。一个观点如果过去 10 条视频已经重复，不应因为表达顺畅继续拿高 Novelty。

---

## Stage 8 — Vision Router

先判断：

```text
visual_dependency = low | medium | high
```

### low
口播/Podcast：Transcript Only。

### medium
偶尔 PPT/新闻截图：按关键 timestamp 抽帧。

### high
财报、K 线、代码、PPT、产品 Demo：启用 Vision。

视觉策略：**优先 Scene Change / key timestamp，不做无脑固定间隔截图。**

Vision 结果作为 Evidence Attachment，不能静默修改 Transcript。

---

## Stage 9 — Cross-Content Synthesis

当样本达到 10+ 条或用户明确要求频道报告时执行。

Creator Report 至少回答：

1. 内容主题分布是什么？
2. 哪些思想反复出现？
3. 哪些视频最值得看？
4. 同一主题哪一期解释最好？
5. 哪些内容高度重复？
6. 观点随时间如何变化？
7. 是否存在前后矛盾？
8. 常用的 Evidence / Reasoning 风格是什么？
9. 做过哪些预测？哪些已经可验证？
10. 哪些内容 Evergreen，哪些只是热点评论？

Creator Report 遵循 `schemas/creator-intelligence.schema.json` 与 `templates/creator-report.md`。

---

## Stage 10 — Canonicalize Knowledge

原则：**Synthesis, not accretion.**

视频不是最终知识单位，Idea 才是。

Bulk：

```text
Extract candidates per video
    ↓
Canonicalize once across corpus
    ↓
Freeze manifest/taxonomy
    ↓
Write concept/entity/claim pages
```

Incremental：

1. 先读已有 Concept/Entity；
2. 能扩展旧页面就扩展；
3. 只有真正新概念才创建新页面；
4. 同义词必须 merge/alias；
5. 观点冲突必须标记，不允许静默“调和”；
6. 每个 durable concept 必须保留 Source + Timestamp。

示例：

```text
土地财政
卖地财政
土地出让金依赖
房地产财政
```

应优先 canonicalize 到一个概念，而不是四张重复卡。

---

## Stage 11 — Index / Ask

V1 首选 SQLite FTS5：

- 每个 timestamp segment 建索引；
- 搜索结果返回 video_id + timestamp + source URL；
- 索引是 Derived Artifact，可随时从 Raw 重建；
- 不允许索引数据库反向成为唯一真相源。

当用户 Ask Creator：

```text
Answer
+ supporting Claim
+ Source video
+ Timestamp
+ URL
```

没有证据时明确说“现有 corpus 不支持”，不要补写。

---

## Stage 12 — Incremental Monitor

监控器只负责：

```text
Schedule/RSS/API
  ↓
Discover newest-first
  ↓
Stable-ID dedupe
  ↓
Queue new items
  ↓
Trigger this Skill
```

状态要求：

- one-item failure 不阻断 batch；
- lock 防止重复并发；
- cooldown 防止频繁重扫；
- known item 立即跳过；
- newest-first 遇到已处理区间可提前停止；
- 失败进入 `state/failures.jsonl`，可重试。

n8n 适合做 Schedule / API / Notify，不承载 Canonicalization、Argument Graph 等核心知识逻辑。

---

# Model Routing

## Deterministic / No LLM

用于：

- inventory
- metadata
- dedupe
- transcript normalization 基础规则
- file rendering
- FTS index
- validation

## Cheap/Fast Model

用于：

- topic classification
- entity extraction
- initial tags
- simple summary

## Medium Model

用于：

- TL;DR
- Key Takeaways
- Claims extraction
- Evidence typing
- scoring first pass

## Strong Reasoning Model

用于：

- Argument Graph
- contradiction detection
- cross-video synthesis
- idea evolution
- canonicalization difficult cases
- Creator Report narrative

不允许所有阶段默认调用最贵模型。

---

# Quality Gates

单视频完成条件：

- [ ] 有 metadata
- [ ] 有 transcript 或明确 unavailable
- [ ] Transcript source/provenance 已记录
- [ ] Intelligence JSON 可解析
- [ ] Main Thesis 不为空
- [ ] 重要 Claim 有 timestamp 或明确 timestamp unavailable
- [ ] Fact / Opinion / Prediction 已区分
- [ ] Score 范围合法
- [ ] Verdict 有 reason + confidence
- [ ] Markdown 由 JSON 渲染或与 JSON 一致

频道完成条件：

- [ ] Inventory coverage 已报告
- [ ] 失败条目有 failure ledger
- [ ] Topic distribution 基于完整已处理样本而非少量主观抽样
- [ ] Top Videos 有评分理由
- [ ] Recurring ideas 已去重
- [ ] Contradictions 不被静默解决
- [ ] Creator Report JSON + Markdown 同时存在
- [ ] Obsidian 链接/文件结构可导航

执行：

```bash
python3 scripts/validate_bundle.py <creator-root>
```

---

# Benchmark DNA

本 Skill 吸收以下项目的架构思想，但不直接依赖其代码：

- yt-insights：JSON-first、VTT corpus、FTS5、aggregate report、atomic/idempotent
- Cole Medin Knowledge Base：idea-as-unit、extract→canonicalize→write、双向链接、contradiction handling
- youtube-digest-skill：TL;DR、Key Takeaways、timestamped assertions、timeline、triage
- n8n #9268：scheduled channel monitoring、dedupe、relevance score/reasoning
- Summario：Must Watch / Worth / Skim / Skip、confidence、channel-specific consumption settings
- Founder Book：newest-first incremental sync、lock/cooldown/failure tolerance、grounded RAG wiki
- mcptube：MCP passthrough、cross-video report、frames/vision、CLI + service split
- n8n #3408：playlist corpus → retrieval → conversational analysis

详细映射见 `references/benchmarks.md`。

---

# Example — 一个狠人

用户：

> 把“一个狠人”整个频道做成知识库，告诉我哪些最值得看，并拆出每期论点论据。

执行：

```text
mode=inventory
→ 建完整目录
→ 报告 coverage

mode=triage (先取可处理样本/metadata+transcript)
→ Knowledge Score
→ Must Watch / Worth / Skim / Skip

mode=channel
→ 批量 Intelligence JSON
→ Argument Intelligence
→ Topic Distribution
→ Recurring Ideas
→ Idea Evolution
→ Prediction Track Record
→ Creator Intelligence Report

finalize
→ Markdown/Obsidian
→ sera-knowledge-sync
→ sera-context-system
```

建议先 10 条 Smoke Test，确认笔记与评分质量后再跑全频道。

---

## Dependencies

优先：

- Python 3.10+
- yt-dlp
- SQLite/FTS5

可选：

- youtube-transcript-api
- ffmpeg
- Whisper / faster-whisper / 其它 ASR
- mcptube（若已安装，可作为 MCP/视觉/检索适配器）
- n8n（调度/通知层）
- Qdrant/Chroma（V2 语义检索）

本 Skill 必须能在没有 n8n、没有 Vector DB 时完成核心分析。

---

## Iron Rules

1. **Raw immutable**：原始字幕/Transcript 与 AI 生成内容分层保存。
2. **JSON source of truth**：先结构化、后渲染；Markdown 不是唯一真相源。
3. **Source-grounded**：重要 Claim 必须尽量回指 Timestamp/Source。
4. **Fact ≠ Opinion ≠ Prediction**：禁止混写。
5. **Synthesis > Accretion**：知识单位是 Idea，不是一视频一知识卡无限增长。
6. **No silent contradiction resolution**：冲突必须显式标记。
7. **Idempotent**：稳定 ID 去重，重复运行不得复制产物。
8. **Incremental first**：日常同步只处理新增；Aggregate Report 周期性重算。
9. **Vision on demand**：只有视觉依赖高时才抽帧/跑视觉模型。
10. **Model routing**：确定性任务不用 LLM，简单任务不用强推理模型。
11. **No full-media hoarding**：默认不永久保存整频道视频/音频。
12. **One failure never aborts the corpus**：失败登记后继续。
13. **No secret in repo**：API key/token/credentials 只引用位置，不入库。
14. **Human-first report**：最终必须有“哪些最值得看、为什么”的明确浏览入口。
15. **Agent-portable**：不得把核心协议绑定某一家模型；DeepSeek/Kimi/Codex/Claude/Trae 均可按同一 Contract 执行。
