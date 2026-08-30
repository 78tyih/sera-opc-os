# Cross-site Learning Engine

> V4.1 · 从“收藏优秀网站”升级为“跨站提炼可复用模式”。

## Why

单个网站只能告诉我们“这个站怎么做”。真正进入 Sera Design Memory 的 Pattern 应尽量由多个独立来源共同支持。

```text
Site A ─┐
Site B ─┼→ Case-local DNA → Cross-site Miner → Pattern Candidate → Design Review → Canonical Pattern
Site C ─┘
```

## Promotion Levels

| Level | 条件 | 默认处理 |
|---|---|---|
| `case_local` | 只在 1 个独立域名出现 | 留在案例，不晋升 |
| `candidate` | 至少 2 个独立域名支持 | 进入 Review Queue |
| `strong_candidate` | 至少 3 个独立域名支持 | 高优先级 Review Queue |

**独立域名计票**：同一个网站的多个页面不能重复增加 support count。

## What We Mine

V4.1 首先挖“语义 Pattern”，而不是把相同 HEX / px 当成设计规律：

- Brand personality
- Component patterns
- Conversion patterns
- Layout patterns
- Motion / hover patterns
- Usage patterns

颜色、字体、间距等 raw tokens 主要作为 Evidence 与实现参考；只有经过抽象后才可能进入跨站 Pattern Memory。

## CLI

前置：每个 Case 已有 `dna/STYLE_DNA.json`。

```bash
python3 cross-site/miner.py \
  --case linear=case-studies/linear \
  --case stripe=case-studies/stripe \
  --case vercel=case-studies/vercel \
  --out cross-site/studies/premium-product-web-v1/result.json \
  --markdown cross-site/studies/premium-product-web-v1/result.md
```

输出遵守 `comparison.schema.json`。

## What the Miner Does NOT Do

`miner.py` 是确定性 overlap engine，不使用 LLM，不做审美判断，也不自动晋升规则。它只回答：

> 哪些已经被结构化的语义模式在多个独立案例里重复出现？

随后由 Design Strategy / Design Review 判断重复是否有意义、是否属于同一抽象层、是否值得复用。

## First Smoke Test

`studies/premium-product-web-v1/`

当前 ready anchors：Linear / Stripe / Vercel。

Panda AI 保留在 queued target，因为公开检索暂时无法稳定确认 `pandaai.com` 是否就是目标产品；在 canonical URL 确认前不得伪造提取结果。

## Tests

```bash
python3 cross-site/tests/test_miner.py
```

覆盖：

- 3 个独立站重复 Pattern → `strong_candidate`
- 2 个独立站重复 Pattern → `candidate`
- 同一域名多个 Case 不重复计票
