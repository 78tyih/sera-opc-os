# Agent Integration — Sera Creator Intelligence

`sera-creator-intelligence` is model-agnostic. The protocol is defined by `SKILL.md`, JSON schemas, templates and validation rules; no single LLM provider is authoritative.

## Native Skill Runtimes

For WorkBuddy / Codex / Trae / Claude Code / Cursor, expose or install the directory:

`business/sera-creator-intelligence/`

The platform should read `SKILL.md` when the user's intent matches Creator/Channel analysis, transcript learning, video triage, argument breakdown, creator knowledge-base generation or monitoring.

## Generic Agents — DeepSeek / Kimi / other models

If the runtime has repository/file access but no native Skill loader:

1. Read `business/sera-creator-intelligence/SKILL.md` completely.
2. Read the relevant schema(s):
   - `schemas/video-intelligence.schema.json`
   - `schemas/creator-intelligence.schema.json`
3. Read only the template needed for the requested output.
4. Execute the requested mode exactly as defined in the Skill.
5. Write JSON source-of-truth first; render Markdown second.
6. Run `scripts/validate_bundle.py <creator-root>` before reporting completion.

Do not translate the Skill into a provider-specific permanent format. Keep the shared contract canonical in this directory.

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

The route must precede generic video-production routing so content analysis is not mistaken for video creation.

## Invocation Contract

Minimum invocation object:

```json
{
  "skill": "sera-creator-intelligence",
  "mode": "inventory|video|triage|channel|refresh|ask|rebuild-report",
  "source": "channel/video/playlist/local-corpus",
  "output_root": "optional path",
  "analysis_focus": "optional",
  "max_items": null
}
```

## Completion Contract

An agent may claim completion only when:

- requested scope has an explicit coverage count;
- failures are recorded instead of hidden;
- required JSON output parses;
- claims are grounded to source/timestamp where available;
- Fact / Interpretation / Prediction are separated;
- Watch Verdict contains reason and confidence;
- bundle validator passes, or the agent explicitly reports why validation cannot run.

## Smoke Test

For the first real execution, follow `SMOKE_TEST.md` and process only the specified 10-item sample. Do not launch a full-channel backfill before the sample is reviewed.
