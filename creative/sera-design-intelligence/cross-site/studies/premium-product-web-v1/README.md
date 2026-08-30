# premium-product-web-v1 — Cross-site Smoke Test

状态：**offline smoke test completed · live revalidation pending**

## Evidence

首轮没有伪造实时抓取。我们复用了 Designlang 官方仓库中 2026-05-21 已真实生成并提交的 gallery snapshots：

- Linear — `linear-app-DESIGN.md`
- Stripe — `stripe-com-DESIGN.md`
- Vercel — `vercel-com-DESIGN.md`

每个 Case 都保存 external provenance + historical freshness 标记。Panda AI 继续 queued，canonical URL 未确认前不生成 DNA。

## Offline Result

- 15 strong overlaps
- 3 two-site candidates
- 9 case-local observations
- **5 Pattern-Library eligible**

详见 `offline-result.json` 与 `semantic-review.md`。

核心结论不是“三站都长得一样”，而是它们在颜色、字体、material 明显不同的情况下，仍出现若干可验证的结构性重复：flex 主导 + grid 辅助、大 display + 紧凑 body、完整 radius scale，以及 neutral second-person voice。

## Live Revalidation

当前环境 `npx designlang` bootstrap 曾超时，因此 live crawl 尚未冒充完成。后续可在正常 Node/Network 环境执行：

```bash
python3 cross-site/run_study.py \
  cross-site/studies/premium-product-web-v1/study.json \
  --continue-on-error
```

如果其他机器 / MCP / CI 已经生成 Designlang 输出，可直接：

```bash
python3 extraction-engine/import_existing.py \
  --source-dir <designlang-output> \
  --url <url> \
  --copy-to-raw case-studies/<case>/raw/designlang \
  --manifest case-studies/<case>/normalized/extraction-manifest.json
```

Fresh live evidence 通过后，再允许 Pattern Candidate 晋升 canonical memory。
