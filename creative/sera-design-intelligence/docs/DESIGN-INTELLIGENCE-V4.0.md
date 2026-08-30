# Sera Design Intelligence V4.0 — Evidence-first Upgrade

> Date: 2026-08-31
> Decision: integrate Designlang as the default URL Extraction Backend while preserving Sera's higher-level reasoning, memory, routing and review architecture.

## Executive Decision

Do **not** rebuild Designlang.

Do **not** replace `sera-design-intelligence` with Designlang.

Use:

```text
Designlang = L0 Extraction Backend
Sera Design Intelligence = L0 → L5 Intelligence System
```

Designlang answers: **What is actually on the page?**

Sera answers: **Why does it work, what should we remember, and how should we use it?**

## Why V4

V3.x already solved Design Strategy, Design Director, Style Router, Benchmark, Design DNA, Pattern Library, Component / Asset Memory, UX / Design Review, Experiment / Conversion Learning.

The weak point was URL extraction: too much factual work was mixed with Agent perception. V4 fixes this by introducing a stable evidence layer.

## New Components

### `extraction-engine/adapter.py`

Runs Designlang, preserves raw output, emits a stable Sera manifest, hashes/classifies artefacts, never interprets design quality, and supports runtime `cookie-file` without storing values.

### `extraction-contract.schema.json`

Decouples Sera from upstream output filenames and schema churn.

### `designlang-adapter.yaml`

Declares backend capabilities, commands, security policy and fallback.

### Evidence-aware DNA

`dna-engine/extraction-schema.json` now supports provenance, evidence, confidence, responsive behavior, interaction states, dark mode, accessibility and CSS health.

## Agent Change

```text
old: visual extractor + analyst
new: extraction orchestrator + evidence curator + DNA synthesizer
```

Design Strategy / Director own interpretation and design decision.

## Workflow Change

```text
old:
capture → extract → visual analysis → case → registry → assets

new:
capture → preflight → machine extraction → normalize → validate
→ DNA synthesis → design reasoning → benchmark/pattern mining
→ case → memory candidate → review
```

## Data Boundary

```text
raw/          = immutable upstream evidence
normalized/   = Sera stable interface
dna/          = interpreted design features
analysis.md   = reasoning
registry      = reviewed canonical memory
```

This boundary is the key V4 architectural decision.

## What We Reuse from Designlang

Rendered DOM / computed-style extraction, DTCG token output, typography / spacing / radius / shadow extraction, component clustering, motion / interaction state capture, responsive behavior, dark mode, accessibility / CSS health, multi-format exports, MCP, and drift / visual diff as future monitoring backend.

## What Remains Sera-native

Benchmark curation, design quality reasoning, product × style matching, business / conversion judgment, pattern abstraction, component selection, style composition, Design Memory, experiments / feedback, design generation, review gates and final design decisions.

## Next

### V4.1 — Living Design Database

Use scheduled re-extraction + drift to identify meaningful changes in selected benchmark products.

### V4.2 — Cross-site Pattern Miner

Compare multiple strong products and promote patterns supported by independent sources.

### V4.3 — Retrieval + Composition

Given a new product brief, retrieve the best matching Hero, Navigation, Pricing, Input and motion patterns, then let Design Director compose a new system rather than imitate one reference.

## Acceptance Criteria

V4 is operational when URL extraction produces a Sera manifest; raw artefacts remain immutable; STYLE_DNA contains provenance/evidence; inferred claims are distinguishable from observed facts; Designlang failure can fall back without changing the upper-layer contract; Case Study and Style Memory only promote reviewed candidates.
