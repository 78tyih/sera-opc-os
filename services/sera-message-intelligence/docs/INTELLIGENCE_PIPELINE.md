# Intelligence Pipeline

The product goal is **one Personal Intelligence Brief across all monitored conversations**, not one diary per group.

## Two-stage flow

```text
PostgreSQL messages
  -> group by platform/account/conversation
  -> bounded conversation chunks
  -> LLM chunk claims bound to exact [m:ID] evidence
  -> validate every claim message_id against its chunk
  -> expose ONLY validated claims to the cross-conversation merge
  -> candidate intelligence items
  -> require every final message_id to be in the validated-claim ID set
  -> rebuild source references from database metadata
  -> application-calculated importance score
  -> JSON + Markdown + HTML
```

## Evidence contract

Messages are formatted as `[m:123] ...`. The Level-1 LLM must attach exact message IDs to every factual claim.

Validation is fail-closed:

- A chunk claim citing an ID outside its chunk raises `EvidenceError`.
- Free-form chunk summaries and full chunk message-ID lists are **not** exposed to Level 2; only validated claims are.
- A final brief item may cite only IDs that appeared in validated Level-1 claims. It is not enough for the ID to merely exist somewhere in the report window.
- A final brief item citing an ID not present in stored report-window messages also raises `EvidenceError`.
- Final `sources` are never trusted from model output; they are rebuilt from the stored messages.

This does not make an LLM infallible, but it narrows the synthesis surface and creates an auditable path from each surfaced item to explicitly promoted source messages.

## Importance score

The model supplies normalized components only. Application code computes:

```text
0.30 Personal Relevance
+ 0.25 Actionability
+ 0.20 Urgency
+ 0.15 Novelty
+ 0.10 Source Weight
```

The formula is deterministic and can later be personalized without changing the report schema.

## Report window

`SMI_REPORT_TIMEZONE` defaults to `Asia/Singapore`. `scripts/generate_daily_brief.py` converts the selected local calendar day into UTC bounds before querying PostgreSQL.

## Provider contract

The pipeline uses an OpenAI-compatible HTTP client. Configure:

- `SMI_LLM_BASE_URL`
- `SMI_LLM_API_KEY`
- `SMI_LLM_MODEL`

This allows DeepSeek or another compatible provider without coupling the core to a vendor SDK.
