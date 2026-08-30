# Cross-site Pattern Promotion Policy

## Core Rule

**重复 ≠ 真理；重复只是值得审查的证据。**

### Case-local

只有一个独立域名支持：保留在 Case Study。不得写进全局 Pattern Registry。

### Candidate

至少 2 个独立域名支持相同语义 Pattern：进入 Review Queue，但仍不能自动成为 canonical rule。

Review 必须回答：

1. 两个站的 Pattern 是否真的处于同一抽象层？
2. 是否由相似业务场景造成，而不是通用规律？
3. 是否存在反例或明显 trade-off？
4. 是否能在不复制品牌资产的前提下复用？
5. 对 Sera 当前产品类型是否有价值？

### Strong Candidate

至少 3 个独立域名支持，或 2 个独立域名 + 明确 outcome / experiment evidence。

Strong Candidate 只代表优先审查，不代表自动晋升。

## Raw Token Rule

以下默认不是跨站 Pattern：

- 相同 HEX
- 相同 font family
- 相同 px 数字
- 相同品牌图形
- 相同文案

可抽象成 Pattern 的例子：

- low-contrast secondary navigation
- single dominant CTA above the fold
- product-in-context demo instead of decorative hero art
- compact information density with strong alignment
- subtle motion used for state explanation rather than decoration

## Independence

计票单位是独立 domain / product，不是 page。`linear.app/homepage` 与 `linear.app/plan` 不能算 2 个独立来源。

## Canonical Promotion

```text
Cross-site Candidate
      ↓
Design Strategy Review
      ↓
Design Critic Review
      ↓
(optional) Product Test / User Feedback
      ↓
Pattern Registry
```

所有晋升后的 Pattern 必须保留：来源、支持数量、适用场景、不适用场景、evidence refs、最近复核时间。
