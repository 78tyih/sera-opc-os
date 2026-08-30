# premium-product-web-v1 — Smoke Test

状态：`configured_not_run`

## Anchors

1. Linear — product craft / dense-but-calm information architecture / motion
2. Stripe — fintech trust / conversion / visual storytelling
3. Vercel — developer SaaS / product demo / typography

Panda AI：queued，等待 canonical URL 确认后加入第二轮，不生成伪结果。

## Execution

```bash
# 1. Extract
python3 ../../../extraction-engine/adapter.py https://linear.app/ --out ../../../case-studies/linear/raw/designlang
python3 ../../../extraction-engine/adapter.py https://stripe.com/ --out ../../../case-studies/stripe/raw/designlang
python3 ../../../extraction-engine/adapter.py https://vercel.com/ --out ../../../case-studies/vercel/raw/designlang

# 2. Design Extraction Agent synthesizes evidence-backed STYLE_DNA.json for each case

# 3. Mine overlaps
python3 ../../miner.py \
  --case linear=../../../case-studies/linear \
  --case stripe=../../../case-studies/stripe \
  --case vercel=../../../case-studies/vercel \
  --out result.json \
  --markdown result.md
```

## Expected Outputs

- 3 immutable raw extraction sets
- 3 normalized manifests
- 3 evidence-backed STYLE_DNA files
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
