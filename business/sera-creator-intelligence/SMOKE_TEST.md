# Smoke Test — 一个狠人

目标：在 Source Acquisition V2 已选出可用生产链路后，验证 `sera-creator-intelligence` 能完成 Transcript → Video Intelligence → Argument Analysis → Score → Sample Creator Report → Notion Publish。

## Precondition — Acquisition Gate

如果尚未选出 Production Source Stack，先执行：

`ACQUISITION_BENCHMARK.md`

并得到：

```text
Primary Transcript Provider
Backup Transcript Provider
Managed Audio Fallback
Local / Residential Fallback
```

没有达到 `ACQUISITION_BENCHMARK.md` 的 Promotion Gate 时，本 Smoke Test 不得继续生成完整 Intelligence。

## Source

- Creator：一个狠人
- Handle：@henren778
- Channel ID：UCJAPsTtcJJWGk8e-_CJL8TQ
- 已有 Phase 1 Inventory：755 条可枚举内容（若已有 `videos.json`，必须复用）

## Test Scope

只处理以下 10 条，不运行全量 Backfill：

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

排除：`7mvtItF_hTs`（subscriber-only）。

## Required Run

1. 读取：
   - `SKILL.md`
   - `SOURCE_ACQUISITION_V2.md`
   - `ACQUISITION_BENCHMARK.md`
   - `schemas/transcript-acquisition.schema.json`
   - 两个 Intelligence Schema
   - 模板
   - `NOTION_PUBLISHER.md`
2. 检查已有 Phase 1 catalog；已有则复用。
3. 按已晋升的 Provider Stack 获取 10 条 Transcript。
4. 每条 acquisition 必须写标准化 Transcript JSON；失败必须保留 attempts/failure class。
5. 只有通过 Acquisition Gate 的条目才进入 Video Intelligence。
6. 对成功条目生成：
   - `intelligence/videos/<video_id>.json`
   - 对应 Markdown 阅读笔记
7. 每条必须拆：Main Thesis / Claims / Evidence / Reasoning / Assumptions / Fact vs Interpretation vs Prediction。
8. 计算 6 维 Knowledge Score + Personal Relevance + Watch Verdict。
9. 基于成功样本生成 sample Creator Report；不得把失败条目当作已分析内容。
10. 运行：

```bash
python3 scripts/validate_bundle.py <creator-root>
```

11. Validator PASS 后按 `NOTION_PUBLISHER.md` 幂等发布。
12. 完成后立即停止，不得继续全量 Backfill。

## Acquisition Rules

- Provider 原始响应不可直接成为下游真相源，必须先 normalize。
- `content_mismatch` 是硬失败。
- `partial` Transcript 可以做受限分析，但必须明确 Coverage。
- 标题/Description/搜索摘要不能替代 Transcript。
- Firecrawl Audio 等临时媒体完成 ASR 后默认删除。
- Cloud Provider 全失败时转 Local/Residential Runner，不重复无意义撞同一 YouTube Gate。

## Notion Expected State

成功分析并直写 Notion时：

- 10 条样本按 Video ID 幂等更新；不得重复创建。
- 只有真正完成 Intelligence 的条目进入 `analyzed`。
- Acquire 失败条目保留失败/待处理状态，不填伪 Score。
- Creator `Analyzed Items` = 实际完成 Intelligence 的数量，而不是固定写 10。
- `Must Watch` / `Average Score` 只从成功分析条目计算。
- Smoke Test 不自动标记为 `reviewed`。

## Acceptance Criteria

- 10 条目标均有明确 acquisition status。
- 每个 Provider attempt 可审计。
- 成功 Transcript 有正确 Video ID / URL / Language / Provenance。
- 无未解决 `content_mismatch`。
- Timestamp Coverage 被记录。
- 进入 Intelligence 的条目符合核心 Schema。
- Fact / Interpretation / Prediction 分离。
- Watch Verdict 有 confidence + reason。
- Creator Report 明确 sample coverage 与失败数量。
- Notion 每个条目都有 publish action/status。
- 完成 10 条后停止。

## Failure Report

处理失败写入：

`state/failures.jsonl`

至少包含：video_id、stage、provider、error_class、error、retryable、timestamp。

Notion 发布日志：

`publish/notion_publish_log.jsonl`

## Final Response

向用户报告：

### Acquisition
- Primary / Backup / Audio / Local stack
- 10 条成功/partial/失败数量
- Provider 来源分布
- Native Caption vs Provider Transcript vs ASR 数量
- Timestamp coverage
- Mismatch count

### Intelligence
- 实际分析数量 / 10
- 成功条目评分表
- Top 3（仅从已分析条目产生）
- 主要 Topic / Recurring Ideas
- Argument Analysis 质量问题

### Validation / Publish
- Validator PASS / FAIL
- Notion created / updated / queued / failed
- Creator Index 是否正确按实际分析数量更新
- 是否建议进入 30–50 条 Phase 3

## STOP

禁止自动进入剩余 745 条 Full Backfill。
