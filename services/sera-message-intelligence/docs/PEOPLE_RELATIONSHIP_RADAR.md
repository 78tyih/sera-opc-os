# People / Relationship Radar

This view answers a different question from a contact list:

> Who deserves attention now, and what concrete context connects us?

The first version deliberately avoids inferring closeness, friendship, trust or relationship quality from message frequency alone.

## People Radar

A person's attention score is:

```text
People Attention Score =
  40% strongest active Opportunity signal
+ 30% strongest active Commitment attention
+ 20% interaction recency
+ 10% interaction evidence strength
```

Interaction evidence is intentionally low-weight. Someone who posts heavily in a group should not outrank a quieter person connected to a real opportunity or overdue promise just because they generated more messages.

Relationship recency uses a slower 60-day linear decay than Opportunity freshness.

### Explainability tags

Possible reasons include:
- `active_opportunity`
- `open_commitment`
- `overdue_commitment`
- `recent_interaction`
- `stale_contact`
- `repeated_interaction`

## Relationship Radar

Relationship Radar is currently a **derived evidence view**, not a claim that two people are close.

An edge is created only when two durable Person objects have one of these explicit contexts:

1. they are both linked to the same active Opportunity; or
2. one is the owner and the other is the beneficiary of an active Commitment.

Mere co-presence in the same WeChat group does **not** create a relationship edge.

Current relationship attention score:

```text
Relationship Attention Score =
  45% strongest shared active Opportunity
+ 35% strongest linked Commitment attention
+ 20% context recency
```

Possible reasons include:
- `shared_active_opportunity`
- `open_commitment_link`
- `overdue_commitment_link`
- `recent_signal`

## CLI

```bash
python scripts/generate_people_radar.py
```

Default outputs:

```text
reports/people-radar/
├── people-radar.json
└── people-radar.md
```

The CLI does not call an LLM. It derives the view from durable, evidence-backed objects.

## Important limitation

This is not yet cross-platform identity resolution. A WeChat identity and an email identity that belong to the same human remain separate People objects until conservative identity evidence is available.

That limitation is intentional: two separate people incorrectly merged into one identity is more damaging to long-term context than temporarily having two records for the same human.
