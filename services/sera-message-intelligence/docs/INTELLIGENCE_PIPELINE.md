# Intelligence Pipeline

The product goal is **one Personal Intelligence Brief across all monitored conversations**, not one diary per group.

## Two-stage flow

```text
PostgreSQL messages
  -> group by platform/account/conversation
  -> bounded conversation chunks
  -> LLM chunk summaries + evidence-bound claims
  -> validate every claim message_id against the chunk
  -> cross-conversation merge using only validated claims
  -> candidate intelligence items
  -> validate every final message_id against original messages
  -> application-calculated importance score
  -> rebuild source references from database metadata
  -> JSON + Markdown + HTML
```

## Evidence contract

Messages are formatted as `[m:123] ...`. The LLM must attach exact message IDs to every factual claim.

Validation is fail-closed:

- A chunk claim citing an ID outside its chunk raises `EvidenceError`.
- A final brief item citing an ID not present in the report window raises `EvidenceError`.
- Final `sources` are never trusted from model output; they are rebuilt from the stored messages.

This does not make an LLM infallible, but it prevents unsupported IDs from silently entering reports and gives every surfaced item a path back to original chat evidence.

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
