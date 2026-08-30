# Smoke Test — 一个狠人

目标：验证 `sera-creator-intelligence` 在真实 Creator Corpus 上能稳定完成 Transcript → Video Intelligence → Argument Analysis → Score → Sample Creator Report。

## Source

- Creator：一个狠人
- Handle：@henren778
- Channel ID：UCJAPsTtcJJWGk8e-_CJL8TQ
- 已有 Phase 1 Inventory：755 条可枚举内容（若本机已有 `videos.json`，必须复用，不要重抓全频道）

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

1. 读取本目录 `SKILL.md`、两个 Schema 与模板。
2. 检查已有 Phase 1 catalog；已有则复用。
3. 对 10 条逐条获取 Transcript，记录来源与失败原因。
4. 对每条生成：
   - `intelligence/videos/<video_id>.json`
   - 对应 Markdown 阅读笔记
5. 每条必须拆：Main Thesis / Claims / Evidence / Reasoning / Assumptions / Fact vs Interpretation vs Prediction。
6. 计算 6 维 Knowledge Score + Personal Relevance + Watch Verdict。
7. 基于 10 条样本生成 sample `reports/creator-intelligence.json` 与 `CREATOR_INTELLIGENCE_REPORT.md`。
8. 运行：

```bash
python3 scripts/validate_bundle.py <creator-root>
```

9. validator 必须 PASS；若 FAIL，先修复再报告。

## Acceptance Criteria

- 10 条目标内容全部有明确状态；单条失败不得中断批次。
- 可获得 Transcript 的条目必须保留 Source + Timestamp。
- 所有 Video Intelligence JSON 可解析并符合核心字段约束。
- 事实、作者判断、未来预测不能混写。
- 每个 Watch Verdict 有 confidence + reason。
- Sample Creator Report 至少包含：Coverage、Topic Distribution、Top Videos、Recurring Ideas、Best Video by Topic、Redundancy/Contradiction 初步观察。
- 最终列出最值得优先看的 Top 3，并解释原因。
- 完成 10 条后停止；不要自动跑剩余 745 条。

## Failure Report

失败必须写入 `state/failures.jsonl`，至少包含：video_id、stage、error、retryable、timestamp。

## Final Response

向用户报告：

- Transcript 成功率与来源分布
- 10 条评分表
- Top 3 Must Watch
- 主要 Topic/Recurring Ideas
- Argument Analysis 中发现的质量问题
- validator 结果
- 是否建议进入全量 Backfill
