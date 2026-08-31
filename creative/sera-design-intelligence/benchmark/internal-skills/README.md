# Internal Design Skill Benchmarks

This directory records restricted-access or internal design/workflow skills that are useful as benchmark inputs for Sera Design Intelligence.

## Why this layer exists

A mature Design Intelligence system should learn not only from public websites and open-source design systems, but also from validated production skills used in real organizations. However, restricted documentation must not be copied into a public repository.

Therefore this layer separates **reference registration** from **rule extraction**.

```text
Skill announcement / internal reference
        ↓
Metadata registration
        ↓
Authenticated document review
        ↓
Observed capability extraction
        ↓
Compare with Sera existing rules
        ↓
Keep / adapt / reject
        ↓
Only reviewed rules may enter canonical Skill / Component / Template memory
```

## Current registered references

- `hx-skill` / 火效 — HTX internal, latest version reported 2026-08-31.
- `MarketUI skill` — HTX internal, latest version reported 2026-08-31.

The release announcement reports that the latest versions can cover roughly 80% of day-to-day work. This is stored as **user-reported evidence**, not as an independently verified capability measurement.

## Public-repository safety rules

1. Do not mirror restricted Wiki pages, screenshots, attachments, credentials or internal-only examples.
2. Do not store private Wiki URLs in this public repository.
3. A skill name and high-level release metadata may be registered as a benchmark reference.
4. Detailed capabilities stay `unknown` until the documentation is actually read with authorized access.
5. Internal rules never overwrite Sera canonical rules automatically.
6. After extraction, classify every imported conclusion as `document_observed`, `derived`, `recommended`, or rejected.
7. Product-, brand-, security- and company-specific constraints remain local unless explicitly safe and generalizable.

## Promotion gate

An internal skill can influence Sera Design Intelligence only after:

- authenticated source review;
- rule-by-rule comparison;
- conflict detection;
- portability review;
- security/privacy review;
- explicit promotion into a Sera-native rule, component, template or workflow.

Machine-readable index: `registry.json`.
