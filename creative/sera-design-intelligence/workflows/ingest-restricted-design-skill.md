# Workflow — Ingest Restricted / Internal Design Skill

Use this workflow when the user wants Sera Design Intelligence to learn from an internal, private, paid or otherwise restricted design skill.

## Goal

Learn reusable design intelligence without leaking source material, credentials, internal links, brand-only rules or confidential examples.

## Flow

```text
Reference received
  ↓
Classify access level
  ├─ public → normal extraction workflow
  └─ restricted/private
        ↓
Register metadata only
        ↓
Acquire authorized source access
        ↓
Extract capability facts
        ↓
Normalize into Sera evidence model
        ↓
Compare against existing Sera rules
        ↓
Conflict + portability + privacy review
        ↓
Adopt / Adapt / Reject
        ↓
Test on generic demo
        ↓
Promote only reviewed Sera-native abstractions
```

## Required metadata

- skill name
- organization / source
- release or observed date
- access level
- source freshness
- user-reported claims, clearly labeled
- extraction status
- merge status

## Extraction schema

When source content is available, extract:

- `triggers`
- `inputs`
- `workflow`
- `routing_logic`
- `design_decisions`
- `component_patterns`
- `quality_gates`
- `safety_rules`
- `outputs`
- `failure_handling`
- `update_model`
- `generalizable_candidates`
- `source_specific_rules`

## Evidence labels

- `user_reported` — supplied by the user or announcement, not independently inspected.
- `document_observed` — directly present in authorized source documentation.
- `derived` — reproducible synthesis from observed rules.
- `recommended` — Sera adaptation proposal.

Never convert `user_reported` directly into a canonical rule.

## Restricted-source rules

1. Never mirror the full restricted source into a public repository.
2. Do not publish private Wiki URLs, credentials, internal screenshots or private examples.
3. Summarize only the minimum necessary abstractions.
4. Company-specific implementations should remain references, not canonical Sera defaults.
5. If authorization/access is unavailable, stop at metadata registration rather than guessing.
6. Test adopted rules against generic, de-branded examples before promotion.

## Promotion destinations

A reviewed idea may be promoted into one or more of:

- `SKILL.md` — routing or execution rule
- `patterns/` — reusable interaction/design pattern
- `component-library/registry.json` — composite component
- `template-library/registry.json` — reusable solution template
- `workflows/` — repeatable production workflow
- `knowledge/` — explanatory design knowledge
- `styles/registry.json` — visual/style DNA

## Current intake

First registered restricted benchmarks:

- hx-skill / 火效
- MarketUI skill

See `benchmark/internal-skills/registry.json`.
