# premium-product-web-v1 — Smoke Test

状态：`configured_not_run`

## Anchors

1. Linear — product craft / dense-but-calm information architecture / motion
2. Stripe — fintech trust / conversion / visual storytelling
3. Vercel — developer SaaS / product demo / typography

Panda AI：queued，等待 canonical URL 确认后加入第二轮，不生成伪结果。

## One-command Runner

从 `creative/sera-design-intelligence/` 执行：

```bash
python3 cross-site/run_study.py \
  cross-site/studies/premium-product-web-v1/study.json \
  --continue-on-error
```

Runner 会：

- 只执行 `status=ready` 的 anchors
- 调用 V4 Extraction Adapter
- 写 `execution.json`
- 不伪造语义 Style DNA

Extraction 完成后，由 `design-extraction-agent` 生成各站 evidence-backed `STYLE_DNA.json`，再执行：

```bash
python3 cross-site/run_study.py \
  cross-site/studies/premium-product-web-v1/study.json \
  --skip-extraction \
  --mine-if-ready
```

## Optional Native Designlang Evidence

Designlang 自身已经能多站比较：

```bash
npx designlang brands linear.app stripe.com vercel.com
npx designlang diff linear.app stripe.com
```

这些产物属于 measured comparison evidence；Sera 的 `miner.py` 负责长期 Memory 的 support count / promotion governance，不与 Designlang 重复造轮子。

## Expected Outputs

- 3 immutable raw extraction sets
- 3 normalized manifests
- 3 evidence-backed STYLE_DNA files
- `execution.json`
- `result.json` deterministic overlap report
- `result.md` human review queue
- reviewed Pattern Candidates

## Pass Criteria

- no fabricated extraction data
- all three source domains are independent
- repeated semantic Pattern is detected deterministically
- single-site Pattern remains case-local
- every promoted Candidate has source/evidence refs
- reviewer can reject a repeated Pattern without data loss
