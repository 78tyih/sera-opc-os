# Living Design Benchmark · V4.2

> 目标：把一次性的优秀设计收藏升级为可追踪、可解释、可审计的长期 Design Radar。

## Pipeline

```text
Live Website
   ↓
Designlang / Extraction Backend
   ↓
Evidence Contract
   ↓
STYLE_DNA.json
   ↓
snapshot.py
   ↓
Immutable Design Snapshot
   ↓
drift.py
   ↓
Design Drift Report
   ↓
Meaningful Change Gate
   ├─ none/minor → archive only
   ├─ moderate   → Design Memory Review
   └─ major      → Semantic Review + Cross-site recompute
```

## Core Rule

**Change ≠ Improvement.**

Drift Engine only answers “what changed and how structurally important it is”. It does not automatically promote a changed design into Canonical Memory.

## Radar

Canonical target list: `radar.json`.

First wave:
- Linear
- Stripe
- Vercel
- Apple
- Raycast
- Figma

All six currently have historical Designlang baselines. They remain `live_revalidation_pending` until a current extraction is run.

## Snapshot

```bash
python3 living-benchmark/snapshot.py \
  --target-id linear \
  --dna case-studies/linear/dna/STYLE_DNA.json \
  --manifest case-studies/linear/normalized/extraction-manifest.json \
  --out living-benchmark/snapshots/linear/2026-08-31.json
```

The snapshot stores only stable tracked design state, provenance and hashes. Evidence text is not copied into the fingerprint.

## Drift

```bash
python3 living-benchmark/drift.py \
  --before living-benchmark/snapshots/linear/2026-05-21.json \
  --after living-benchmark/snapshots/linear/2026-08-31.json \
  --out living-benchmark/drifts/linear/2026-05-21..2026-08-31.json \
  --markdown living-benchmark/drifts/linear/2026-05-21..2026-08-31.md
```

## Severity

- `none`: tracked design state did not change.
- `minor`: implementation-level or low-signal change; archive only.
- `moderate`: meaningful visual/system change; Design Memory Review.
- `major`: semantic pattern or conversion pattern changed, or accumulated score is high; rerun semantic review and relevant Cross-site studies.

See `meaningful-change-policy.md`.

## Measurement Coverage

A field newly measured in the current run is **not** considered drift. Missing current measurement is a data-quality issue, not a design change. This prevents extractor capability upgrades from generating false product-change alerts.

## Upstream Boundary

Designlang may provide `diff`, `site`, `dna`, `grade`, fidelity or other measurement tools. Sera does not duplicate those responsibilities.

Sera owns:
1. immutable longitudinal snapshots;
2. meaningful-change classification;
3. memory update gates;
4. cross-site recomputation decisions;
5. long-term benchmark history.
