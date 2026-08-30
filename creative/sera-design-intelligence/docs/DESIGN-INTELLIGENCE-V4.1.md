# Sera Design Intelligence V4.1 — Cross-site Learning

> Date: 2026-08-31
> Goal: 从单站 Design Extraction 升级为多站 Pattern Learning。

## Decision

V4.0 解决了“事实先提取，再推理”。V4.1 解决下一个问题：**怎样避免把一个网站的偶然实现当成长期设计规则？**

答案是把 Design Memory 的晋升单元从 single-site insight 改成 cross-site evidence candidate。

```text
3 independent sites
      ↓
3 Evidence-backed STYLE_DNA
      ↓
Deterministic overlap miner
      ↓
Semantic review
      ↓
Design critic
      ↓
Canonical Pattern Candidate
```

## Promotion Rule

- 1 site → case-local only
- 2 independent sites → candidate
- 3+ independent sites → strong candidate
- same domain never counts twice
- no candidate becomes canonical without Review

## Deterministic Miner

`cross-site/miner.py` deliberately does not call an LLM. It matches structured semantic fields from Style DNA so that the first discovery step is reproducible.

LLM/Agent reasoning begins after the overlap report, where Design Strategy asks whether the repeated item is genuinely the same pattern and whether it generalizes.

## Smoke Test Set

Ready anchors on 2026-08-31:

- `linear.app`
- `stripe.com`
- `vercel.com`

`pandaai.com` remains queued until the intended product's canonical URL is verified. This is a deliberate anti-hallucination rule: unavailable or ambiguous references must not be turned into fake Design DNA.

## Why These Anchors

The first trio spans different design strengths: product-workflow craft, fintech trust/conversion, and developer SaaS/product demonstration. The point is not to copy their appearance; it is to find patterns that survive across different brands.

## Next

After the first real extraction run:

1. Review every strong candidate.
2. Separate universal patterns from category-specific patterns.
3. Add negative/anti-pattern evidence.
4. Feed accepted patterns into Component Retrieval / Style Composition.
5. Then add Drift Monitoring as V4.2.
