# Sera Message Intelligence — Project Overview

## One-sentence definition

A local-first message intelligence system that continuously collects approved IM conversations and converts them into one evidence-backed Personal Intelligence Brief.

## Why this exists

High-value information is distributed across dozens of groups and direct chats. Reading every stream creates three recurring failures:

1. important messages are missed;
2. decisions and follow-ups are forgotten;
3. useful knowledge disappears inside chat history.

Sera Message Intelligence separates **message collection** from **intelligence synthesis**. Platform-specific collectors can change without changing the canonical message store or reporting layer.

## Who it is for

The first target is a high-context operator who participates in many work, market, project and relationship conversations and needs a compressed daily view rather than another inbox.

Later the same substrate can serve founders, BD/sales operators, investment/research teams, communities, operations teams and AI-agent workspaces.

## Core value

The validation question for P0–P2 is simple:

> If the user ignores the monitored chats for one day and reads only the next Personal Intelligence Brief, can they avoid missing the important things?

The product therefore optimizes for:

- recall of important events;
- actionable follow-up;
- traceability to source messages;
- cross-group topic merging;
- low operational burden;
- replaceable collectors.

## Architecture

```text
Collectors
  WeChat A / WeChat B / WeChat C
  future: OpeniLink / Feishu / WeCom / Telegram / Slack
        |
        v
Message Gateway
        |
Normalize -> MessageEventV1
        |
Idempotent storage -> PostgreSQL
        |
Conversation chunks
        |
Level-1 evidence claims
        |
Validated-claim-only cross-group merge
        |
Importance engine
        |
Personal Intelligence Brief
        |
JSON / Markdown / HTML / future delivery sinks
```

## Server Win role

Server Win is the default always-on WeChat runtime because the collection layer needs a stable interactive Windows session. Mac remains a control/development surface.

The production account-isolation rule is:

**one WeChat identity -> one Windows user/session -> one external webot environment -> one SMI collector identity.**

This avoids making multi-account correctness depend on a single WeChat process namespace or whichever `wxid_*` directory changed most recently.

## Intelligence output

The Personal Intelligence Brief contains:

- executive summary
- must handle
- important
- actions
- decisions
- opportunities
- risks
- people to reply to
- resources
- knowledge
- topics

Each important item carries confidence, deterministic importance score and exact source message references.

## Product boundaries

P0/P1 WeChat is read-only. SMI does not send messages or control the WeChat UI. Native WCDB/key behavior remains an external replaceable dependency.

The system does not treat chat data as free public data. Raw storage is local-first, downstream export should be explicit, and reports preserve provenance.

## Expansion path

P3 adds official/replaceable connectors and search. P4 turns the accumulated message substrate into a broader Intelligence OS: People Radar, project/topic memory, capability-scoped agent access and long-term learning.
