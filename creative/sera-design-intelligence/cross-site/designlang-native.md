# Designlang Native Multi-site vs Sera Cross-site Learning

Designlang 已经提供多站能力，因此 Sera 不重复实现浏览器级比较。

## Designlang Native Layer — Measurement

适合做：

```bash
# N 站比较矩阵
npx designlang brands linear.app stripe.com vercel.com

# 两站 Design System 差异
npx designlang diff linear.app stripe.com

# 两站评分对比
npx designlang battle linear.app stripe.com

# 整站统一 Design System
npx designlang site linear.app --max-pages 8

# 探索性融合，不等于 Sera 规则
npx designlang pair stripe.com linear.app
```

它回答：

- 两个/多个网站在颜色、字体、布局、组件、动效等方面有什么差异？
- 哪些 token 是 site-wide，哪些是 page-local？
- 某个站内部一致性如何？

这些属于 **measurement/comparison evidence**。

## Sera Cross-site Layer — Memory Governance

`cross-site/miner.py` 不尝试替代上面的功能。它读取已经归一化/解释过的 `STYLE_DNA.json`，回答：

> 哪些语义模式在多个独立产品中重复出现，因此值得进入 Design Memory Review Queue？

它关心：

- independent domain support count
- Pattern abstraction level
- evidence provenance
- case-local vs candidate vs strong-candidate
- Sera 产品适用性
- Reviewer 是否允许晋升
- 后续 experiment / conversion / user-feedback 是否支持

## Boundary

```text
Designlang brands/diff/site
        ↓
Measured Multi-site Evidence
        ↓
Sera Evidence / STYLE_DNA
        ↓
Sera deterministic overlap miner
        ↓
Design Strategy semantic review
        ↓
Design Critic gate
        ↓
Canonical Pattern Memory
```

`designlang pair/remix/clone` 可以用于探索和实现实验，但它们生成的组合不能直接进入 Canonical Design Memory；必须重新经过 evidence + review。
