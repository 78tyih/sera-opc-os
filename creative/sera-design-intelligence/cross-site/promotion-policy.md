# Cross-site Pattern Promotion Policy V1.1

## Core Rule

**重复 ≠ 真理；重复只是值得审查的证据。**

- 1 independent domain → `case_local`
- 2 → `candidate`
- 3+ → `strong_candidate`
- same domain never counts twice
- no candidate becomes canonical without Review

## Promotion Lanes

Cross-site overlap 必须先按类型分流：

| Type | Lane | 可直接进入 Pattern Library Review？ |
|---|---|---|
| `semantic` | `pattern_review` | 是 |
| `layout` / `motion` / `conversion` | 对应 Pattern Review | 是 |
| `brand` | `brand_voice_review` | 否，进入品牌/文案记忆 |
| `component_presence` | `component_coverage` | 否，只说明组件覆盖 |
| `layout_class` | `taxonomy_only` | 否，只是页面分类 |

所以“三个优秀网站都有按钮”不会成为“高级设计原则”。

## Semantic Pattern Requirement

V4.1 的 `STYLE_DNA.design_patterns[]` 用于表达 Evidence-backed abstraction：

```json
{
  "name": "flex-dominant layout with grid support",
  "category": "layout",
  "abstraction": "semantic",
  "confidence": 0.92,
  "evidence_refs": ["..."]
}
```

它必须由 observed facts 推导，不能为了凑跨站重复而人为统一命名。

## Raw Token Rule

相同 HEX、font family、px 数字、品牌图形、文案默认都不是跨站 Pattern。它们是 Evidence。

## Review Questions

1. 多站 Pattern 是否真的处于同一抽象层？
2. 是否只是相似业务场景造成？
3. 是否存在反例 / trade-off？
4. 是否能不复制品牌资产地复用？
5. 对 Sera 的目标产品是否有价值？
6. Evidence 是否足够新？历史快照是否需要 live revalidation？

## Canonical Promotion

```text
Cross-site Candidate
      ↓
Promotion Lane
      ↓
Design Strategy Review
      ↓
Design Critic Review
      ↓
Freshness Gate / optional Product Test
      ↓
Canonical Memory
```

所有晋升条目必须保留来源、独立支持数、适用/不适用场景、evidence refs、最近复核时间。