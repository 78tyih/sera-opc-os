# Personal Context Graph

## Vision

Sera Message Intelligence is not a chat-summary product. Its long-term purpose is to turn human communication, opportunities, relationships, risks, commitments, projects, tables and accounts into durable context that an agent can continuously understand and query.

The core product question is:

> Can an agent gradually understand not only what the user said, but what the user is actually experiencing, who matters, what is changing, what is promised, and what deserves attention?

Raw messages are evidence. The durable product surface is a Personal Context Graph.

```text
Messages / Files / Calendar / Projects / Tables / Accounts / Agent Runs
                         |
                         v
                       Event
                         |
       +-----------------+-----------------+
       |                 |                 |
       v                 v                 v
     People         Opportunities        Self
       |                 |                 |
       +------ Commitments / Risks / Topics ------+
                         |
                      Projects
                         |
                         v
                Personal Context Graph
                         |
                         v
                 Agent Long-term Context
```

## Design principles

1. **Evidence first.** Every derived object should retain evidence references.
2. **Observation != inference.** Store observed facts separately from model hypotheses.
3. **Confidence is explicit.** Inferences have confidence, freshness and support counts.
4. **Temporal by default.** Relationships, interests, risks and priorities change over time.
5. **User correction wins.** Explicit user corrections supersede model-derived assumptions.
6. **No psychological diagnosis.** Self Intelligence may surface behavioral patterns and hypotheses, but must not present clinical or psychiatric diagnoses as facts.
7. **Cross-source convergence matters.** Repeated signals across independent conversations/sources should carry more weight than a single isolated message.
8. **Do not collapse ambiguity.** If two people, projects or opportunities may be the same entity but identity is uncertain, keep them separate until resolved.

---

## Object 1 — Event

The atomic fact layer. An Event is something that happened, was said, changed or was observed.

Typical examples:
- someone proposed a partnership;
- a client asked for pricing;
- a project deadline moved;
- the user promised to send a document;
- a relationship became inactive;
- an account balance changed;
- the same topic appeared in five different groups.

Suggested fields:

```yaml
id: evt_...
event_type: message|meeting|commitment|decision|transaction|project_change|relationship_signal|self_signal
occurred_at: timestamp
actors: [person_ids]
entities: [object_ids]
summary: string
source_refs: [message/file/calendar/etc]
observed_facts: []
inferred_meaning: []
confidence: 0.0-1.0
created_by: rule|model|user
```

Events are append-oriented. Higher-level objects are projections over Events.

---

## Object 2 — Person

A durable identity object for a human or organization contact.

The goal is not a static address book. It should answer:
- Who is this person?
- Where did we meet?
- What do they do?
- Which projects/opportunities/topics connect us?
- What have they asked for?
- What have I promised them?
- When did we last meaningfully interact?

Suggested fields:

```yaml
id: person_...
display_name: string
aliases: []
identities:
  wechat: []
  email: []
  telegram: []
  slack: []
organization: string|null
roles: []
locations: []
interests: []
expertise: []
relationship_ids: []
opportunity_ids: []
project_ids: []
commitment_ids: []
last_meaningful_interaction_at: timestamp|null
source_refs: []
confidence: 0.0-1.0
```

Identity resolution must be conservative. Name similarity alone is insufficient to merge people.

---

## Object 3 — Relationship

A temporal edge between the user and a Person, or between two Persons.

This turns a contact list into a Relationship Graph.

Useful dimensions:
- relationship context: friend / colleague / client / partner / investor / supplier / community / unknown;
- strength: how much meaningful interaction exists;
- recency: how recently the relationship was active;
- reciprocity: one-way vs two-way interaction;
- trust evidence: based on concrete behavior, not model vibe;
- shared topics/projects/opportunities;
- outstanding commitments;
- relationship trend: warming / stable / cooling / reactivated.

Suggested fields:

```yaml
id: rel_...
from_person_id: person_self
to_person_id: person_...
contexts: []
strength_score: 0.0-1.0
recency_score: 0.0-1.0
reciprocity_score: 0.0-1.0
trend: warming|stable|cooling|reactivated|unknown
shared_topic_ids: []
shared_project_ids: []
shared_opportunity_ids: []
open_commitment_ids: []
observations: []
inferences: []
source_refs: []
last_updated_at: timestamp
```

Relationship scores are decision aids, not statements about a person's worth.

---

## Object 4 — Opportunity

A potential commercial, professional, investment, resource or collaboration opportunity.

The system should detect opportunities that are explicit and implicit.

Examples:
- direct client demand;
- a repeated pain point that could become a product;
- someone seeking a capability the user already has;
- two contacts who could benefit from an introduction;
- an industry change creating demand;
- a conversation that is becoming commercially actionable.

Suggested fields:

```yaml
id: opp_...
title: string
opportunity_type: customer|partnership|product|investment|distribution|resource|introduction|other
stage: signal|qualified|exploring|negotiating|won|lost|parked
people_ids: []
organization_ids: []
project_ids: []
problem: string|null
proposed_value: string|null
estimated_value: number|null
currency: string|null
urgency: 0.0-1.0
fit: 0.0-1.0
probability: 0.0-1.0
next_actions: []
risks: []
source_refs: []
first_seen_at: timestamp
last_signal_at: timestamp
```

An opportunity should not be created from one vague sentence unless confidence is low and the object is explicitly marked as a weak signal.

---

## Object 5 — Commitment

A promise, obligation, follow-up or expected delivery by either side.

Examples:
- "I will send the deck tomorrow";
- "They will introduce me to X";
- "We agreed to review this next week";
- "Need to reply with pricing".

Suggested fields:

```yaml
id: commit_...
owner_person_id: person_...
beneficiary_person_ids: []
summary: string
status: open|done|cancelled|overdue|unknown
due_at: timestamp|null
related_person_ids: []
related_project_ids: []
related_opportunity_ids: []
source_refs: []
confidence: 0.0-1.0
```

Commitments are especially useful for a future Personal CRM / follow-up engine.

---

## Object 6 — Risk

A potentially negative condition that merits monitoring or action.

Risk types may include:
- commercial;
- project execution;
- compliance;
- counterparty;
- relationship;
- financial;
- information quality;
- deadline;
- operational dependency.

Suggested fields:

```yaml
id: risk_...
title: string
risk_type: string
severity: 0.0-1.0
likelihood: 0.0-1.0
status: watching|active|mitigated|resolved|dismissed
related_people_ids: []
related_project_ids: []
related_opportunity_ids: []
triggers: []
mitigations: []
source_refs: []
first_seen_at: timestamp
last_signal_at: timestamp
```

The system should distinguish a factual risk signal from speculation.

---

## Object 7 — Topic

A recurring subject that persists across messages, groups and time.

Topics answer:
- What am I repeatedly exposed to?
- What is becoming more important?
- Which themes connect otherwise unrelated conversations?

Suggested fields:

```yaml
id: topic_...
name: string
aliases: []
summary: string
momentum: rising|stable|falling|episodic
attention_score: 0.0-1.0
personal_relevance: 0.0-1.0
related_people_ids: []
related_project_ids: []
related_opportunity_ids: []
source_refs: []
first_seen_at: timestamp
last_seen_at: timestamp
```

Topic identity should be canonicalized over time rather than generating a new topic per conversation.

---

## Object 8 — Project

A durable workstream with goals, people, decisions, risks, commitments and activity.

The Project object should bridge Message Intelligence with Sera OPC OS / Notion / GitHub rather than duplicate project systems.

Suggested fields:

```yaml
id: project_...
canonical_project_ref: string|null
name: string
status: string
people_ids: []
opportunity_ids: []
commitment_ids: []
risk_ids: []
topic_ids: []
recent_events: []
current_state_summary: string
next_actions: []
source_refs: []
```

Messages should update project context, not become a second project-management database.

---

## Object 9 — SelfSignal

A time-bounded signal about the user's attention, preferences, behavior or current lived context.

SelfSignal is the foundation of Self Intelligence. It must be designed carefully because inference about a person is inherently uncertain.

Appropriate examples:
- "AI infrastructure has appeared in many independent conversations this week";
- "The user has repeatedly postponed the same task";
- "A large share of recent meaningful conversations concern changing jobs";
- "Commercial partnership discussions have increased over the last 30 days";
- "The user is spending more attention on product-building than trading this month".

Inappropriate examples:
- presenting a clinical diagnosis;
- assigning a fixed personality trait from one message;
- claiming hidden motives without sufficient evidence;
- treating sentiment from a single conversation as the user's stable emotional state.

Suggested fields:

```yaml
id: selfsig_...
signal_type: attention|preference|behavior_pattern|goal|concern|transition|decision_style|interest_shift
statement: string
window_start: timestamp
window_end: timestamp
supporting_event_ids: []
contradicting_event_ids: []
confidence: 0.0-1.0
status: hypothesis|supported|confirmed_by_user|rejected_by_user|superseded
source_diversity: integer
last_updated_at: timestamp
```

### Self Intelligence evidence ladder

Use an explicit ladder:

```text
Level 0 — Raw evidence
Level 1 — Observation
Level 2 — Pattern hypothesis
Level 3 — Repeated cross-source pattern
Level 4 — User-confirmed self knowledge
```

Only Level 4 should be treated as durable user-confirmed knowledge without qualification.

---

## Three Intelligence Engines

### 1. Opportunity Intelligence

Inputs:
- messages;
- people;
- repeated pain points;
- project signals;
- external changes.

Outputs:
- opportunity candidates;
- qualification score;
- who to contact;
- why now;
- next action;
- competing risks;
- evidence trail.

Daily question:

> What new opportunities became more real today, and which ones deserve action?

### 2. Relationship Intelligence

Inputs:
- interaction history;
- commitments;
- shared projects/topics;
- meaningful response patterns;
- recency and reciprocity.

Outputs:
- People Radar;
- warming/cooling relationships;
- people needing follow-up;
- relationship context summaries;
- dormant but strategically relevant contacts;
- introduction opportunities.

Daily question:

> Who matters right now, what changed in those relationships, and what should I do next?

### 3. Self Intelligence

Inputs:
- the user's own messages;
- topics receiving repeated attention;
- actions vs stated intentions;
- project movement;
- recurring decisions;
- commitments opened/closed;
- future calendar/project/account signals.

Outputs:
- attention map;
- concern/interest shifts;
- repeated unresolved loops;
- behavior-pattern hypotheses;
- major life/work transitions;
- "what is actually happening to me" narrative over time.

Daily/weekly question:

> What does the evidence say I am actually spending my life, attention and decisions on — not just what I say is important?

---

## Personal Intelligence Brief V2

The current brief can evolve from a message-oriented report into a context-oriented report:

```text
1. What changed today?
2. Opportunities becoming actionable
3. People / relationships requiring attention
4. Open commitments and promises
5. Risks increasing or resolving
6. Projects moved forward / blocked
7. Topics gaining momentum
8. Self Intelligence: attention and behavior patterns
9. Important contradictions / uncertain hypotheses
10. Recommended next actions
```

Every section should support drill-down to evidence.

---

## Update pipeline

```text
MessageEventV1
  -> Event Extraction
  -> Entity Resolution
  -> Object Candidate Updates
  -> Evidence Validation
  -> Temporal Merge / Supersede
  -> Graph Update
  -> Intelligence Views
  -> Personal Intelligence Brief
```

The system should use append-only evidence wherever practical and maintain `supersedes` / `contradicts` relationships rather than silently rewriting history.

---

## Future source expansion

The same graph can later accept non-message evidence:

- GitHub / project state;
- Notion databases and tables;
- Calendar events;
- email;
- CRM;
- financial accounts / transaction facts;
- documents;
- browser/research artifacts;
- agent runs and decisions.

This is how "communication intelligence" becomes a broader Personal Context Layer without forcing every source into a chat abstraction.
