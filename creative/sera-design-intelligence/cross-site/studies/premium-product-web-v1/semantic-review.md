# Offline Cross-site Smoke Test — Semantic Review

> Evidence source: official Designlang gallery snapshots generated on 2026-05-21.
> Review date: 2026-08-31.
> Status: **pipeline validated; live revalidation pending**.

## Result

Deterministic run: 15 strong overlaps · 3 two-site candidates · 9 case-local observations. After promotion-lane filtering, only **5** are eligible for Pattern Library review.

This distinction is the point of V4.1: `buttons`, `cards`, `navigation`, `footer`, `badges`, etc. occur on all three sites, but that only proves component coverage. It does not prove they are why the products feel premium.

## Pattern-Library Review Queue

### 1. Flex-dominant layout with grid support — strong candidate

- Stripe: 53 grid / 374 flex
- Linear: 98 grid / 495 flex
- Vercel: 56 grid / 500 flex

Interpretation: flex handles local composition while grid remains meaningful for macro alignment. Keep as a structural Pattern Candidate; do not copy the raw counts.

### 2. Large display type over compact body scale — strong candidate

- H1: Stripe 56px · Linear 64px · Vercel 48px
- Body: 16px · 14px · 16px

Keep as hierarchy Pattern Candidate; exact font family/weight remain brand-local evidence.

### 3. Radius scale spans subtle corners to pill controls — strong candidate

All three expose a progression from tiny/subtle radii to very rounded controls. The useful rule is **use a coherent radius scale**, not “use 16px everywhere”.

### 4. Neutral second-person marketing voice — strong cross-site signal

Designlang reports neutral voice + `you-only` posture for all three. Useful, but its primary destination is Brand Voice / Copy Memory; Design Intelligence keeps a cross-reference.

### 5. Primary sans with utility mono — two-site candidate

Linear: Inter Variable + Berkeley Mono. Vercel: Geist + Geist Mono. Stripe snapshot exposes only Sohne Var. Keep as a developer/product-SaaS candidate, not a universal rule.

## Strong overlaps that should NOT become “premium design principles”

- buttons/cards/navigation/footer/dropdowns/badges/switches → `component_coverage`
- `landing` → `taxonomy_only`
- exact colors / fonts / spacing / radius values → evidence only

`material-you` on Linear + Vercel is also **not promoted**: Designlang's own snapshot describes the material classification at only 0.45 confidence.

## Architecture lesson

```text
Raw overlap
    ↓
Promotion lane
    ├── semantic → Pattern Review
    ├── brand → Brand Voice Review
    ├── component_presence → Coverage Baseline
    └── taxonomy → no promotion
```

This prevents a deterministic miner from turning “three sites all have buttons” into a fake design law.

## Freshness Gate

These snapshots are historical evidence from 2026-05-21. They validate the Sera pipeline, but any Pattern promoted to canonical memory must be rechecked against a fresh live extraction first.
