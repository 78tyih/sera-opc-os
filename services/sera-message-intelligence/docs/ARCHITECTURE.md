# Architecture

## Goal

Create a local-first message intelligence substrate that can ingest multiple IM platforms, preserve provenance, and later produce cross-conversation intelligence briefs.

## P0 data flow

```text
Collector -> POST /v1/messages -> MessageEventV1 -> Idempotency -> PostgreSQL
```

P1/P2 extends this without changing the ingest contract:

```text
Collectors -> Message Gateway -> Normalize -> Store -> Enrichment -> Chunk summaries -> Cross-conversation clustering -> Importance ranking -> Personal Intelligence Brief
```

## Boundaries

`core` owns message contracts and storage semantics. `collectors` own platform-native behavior such as WeChat WCDB access, official event APIs, polling, checkpoints, and retry queues.

The core must not import any WeChat-specific DLL, SDK, window controller, or database reader.

## Source-project lessons

- webot: local WeChat collector resilience patterns.
- OpeniLink Hub: provider/store/sink separation and processed-message semantics.
- WeChat Daily Report Skill: structured report pipeline and render stages.
- CipherTalk: permissioned plugin/search ideas only; do not copy its non-commercial core into a commercial codebase.
