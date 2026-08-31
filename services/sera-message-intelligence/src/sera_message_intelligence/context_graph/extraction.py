from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field

from sera_message_intelligence.intelligence.schemas import IntelligenceMessage
from sera_message_intelligence.llm.client import StructuredLLM

from .schemas import (
    Commitment,
    ContextEvidenceRef,
    ContextEvent,
    ContextInference,
    Opportunity,
    Person,
)


ExtractableEventType = Literal[
    "decision",
    "project_change",
    "relationship_signal",
    "other",
]


class EventCandidate(BaseModel):
    event_type: ExtractableEventType
    summary: str
    actor_sender_ids: list[str] = Field(default_factory=list)
    message_ids: list[int] = Field(min_length=1)
    confidence: float = Field(ge=0, le=1)


class OpportunityCandidate(BaseModel):
    title: str
    opportunity_type: Literal[
        "customer",
        "partnership",
        "product",
        "investment",
        "distribution",
        "resource",
        "introduction",
        "other",
    ]
    person_sender_ids: list[str] = Field(default_factory=list)
    problem: str | None = None
    proposed_value: str | None = None
    estimated_value: float | None = Field(default=None, ge=0)
    currency: str | None = None
    urgency: float = Field(ge=0, le=1)
    fit: float = Field(ge=0, le=1)
    probability: float = Field(ge=0, le=1)
    next_actions: list[str] = Field(default_factory=list)
    message_ids: list[int] = Field(min_length=1)
    confidence: float = Field(ge=0, le=1)


class CommitmentCandidate(BaseModel):
    owner_sender_id: str
    beneficiary_sender_ids: list[str] = Field(default_factory=list)
    summary: str
    due_at: datetime | None = None
    related_opportunity_titles: list[str] = Field(default_factory=list)
    message_ids: list[int] = Field(min_length=1)
    confidence: float = Field(ge=0, le=1)


class ExtractionPayload(BaseModel):
    events: list[EventCandidate] = Field(default_factory=list)
    opportunities: list[OpportunityCandidate] = Field(default_factory=list)
    commitments: list[CommitmentCandidate] = Field(default_factory=list)


class ContextExtractionResult(BaseModel):
    persons: list[Person] = Field(default_factory=list)
    events: list[ContextEvent] = Field(default_factory=list)
    opportunities: list[Opportunity] = Field(default_factory=list)
    commitments: list[Commitment] = Field(default_factory=list)
    rejected_candidates: list[str] = Field(default_factory=list)


SYSTEM_PROMPT = """You extract durable personal-context candidates from chat messages.
Return JSON only. Do not invent identities, facts, deadlines, values, organizations or relationships.
Every extracted object MUST cite one or more exact message IDs from the input.
Only use sender IDs that appear in the input.
A candidate is a hypothesis backed by evidence, not a confirmed long-term fact.
Extract only information materially useful for decisions, opportunities, commitments, projects or relationships.
Do not create personality, mental-health or clinical conclusions.
"""


def _stable_id(prefix: str, *parts: object) -> str:
    raw = "|".join(str(part) for part in parts)
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:20]
    return f"{prefix}_{digest}"


def _person_id(message: IntelligenceMessage) -> str:
    return _stable_id("person", message.platform, message.account_id, message.sender_id)


def _evidence_id(message: IntelligenceMessage) -> str:
    return f"message:{message.platform}:{message.account_id}:{message.id}"


def _evidence_ref(message: IntelligenceMessage) -> ContextEvidenceRef:
    return ContextEvidenceRef(
        source_type="message",
        source_id=_evidence_id(message),
        platform=message.platform,
        account_id=message.account_id,
        conversation_id=message.conversation_id,
        message_id=message.id,
        occurred_at=message.sent_at,
    )


def _candidate_evidence(
    message_ids: list[int],
    messages_by_id: dict[int, IntelligenceMessage],
) -> list[IntelligenceMessage] | None:
    if not message_ids:
        return None
    if len(set(message_ids)) != len(message_ids):
        return None
    if any(message_id not in messages_by_id for message_id in message_ids):
        return None
    return [messages_by_id[message_id] for message_id in message_ids]


def _time_bounds(messages: list[IntelligenceMessage]) -> tuple[datetime, datetime]:
    times = [message.sent_at for message in messages]
    return min(times), max(times)


def _build_prompt(messages: list[IntelligenceMessage]) -> str:
    allowed_senders = sorted({message.sender_id for message in messages})
    rows = []
    for message in messages:
        rows.append(
            {
                "message_id": message.id,
                "platform": message.platform,
                "account_id": message.account_id,
                "conversation_id": message.conversation_id,
                "conversation_name": message.conversation_name,
                "sender_id": message.sender_id,
                "sender_name": message.sender_name,
                "sent_at": message.sent_at.isoformat(),
                "text": message.text_content,
            }
        )
    schema = {
        "events": [
            {
                "event_type": "decision|project_change|relationship_signal|other",
                "summary": "string",
                "actor_sender_ids": ["existing sender_id"],
                "message_ids": [123],
                "confidence": 0.0,
            }
        ],
        "opportunities": [
            {
                "title": "string",
                "opportunity_type": "customer|partnership|product|investment|distribution|resource|introduction|other",
                "person_sender_ids": ["existing sender_id"],
                "problem": "string or null",
                "proposed_value": "string or null",
                "estimated_value": None,
                "currency": None,
                "urgency": 0.0,
                "fit": 0.0,
                "probability": 0.0,
                "next_actions": [],
                "message_ids": [123],
                "confidence": 0.0,
            }
        ],
        "commitments": [
            {
                "owner_sender_id": "existing sender_id",
                "beneficiary_sender_ids": [],
                "summary": "string",
                "due_at": None,
                "related_opportunity_titles": [],
                "message_ids": [123],
                "confidence": 0.0,
            }
        ],
    }
    return (
        "Allowed sender IDs:\n"
        + json.dumps(allowed_senders, ensure_ascii=False)
        + "\n\nRequired output shape:\n"
        + json.dumps(schema, ensure_ascii=False, indent=2)
        + "\n\nMessages:\n"
        + json.dumps(rows, ensure_ascii=False, indent=2)
    )


class ContextGraphExtractor:
    """Extract evidence-bound graph candidates from a bounded message batch.

    Person identity creation is deterministic and based only on actual message senders.
    LLM output may propose events, opportunities and commitments, but a proposal is
    rejected if it cites unknown message IDs or sender IDs.
    """

    def __init__(self, llm: StructuredLLM):
        self.llm = llm

    def extract(self, messages: list[IntelligenceMessage]) -> ContextExtractionResult:
        if not messages:
            return ContextExtractionResult()

        messages_by_id = {message.id: message for message in messages}
        sender_messages: dict[str, list[IntelligenceMessage]] = defaultdict(list)
        for message in messages:
            sender_messages[message.sender_id].append(message)
        allowed_senders = set(sender_messages)
        now = datetime.now(timezone.utc)

        persons = self._build_persons(sender_messages, now)
        person_ids = {
            sender_id: _person_id(sender_batch[-1])
            for sender_id, sender_batch in sender_messages.items()
        }

        raw = self.llm.generate_json(system=SYSTEM_PROMPT, prompt=_build_prompt(messages))
        payload = ExtractionPayload.model_validate(raw)

        result = ContextExtractionResult(persons=persons)
        opportunity_ids_by_title: dict[str, str] = {}

        for candidate in payload.events:
            evidence_messages = _candidate_evidence(candidate.message_ids, messages_by_id)
            if evidence_messages is None:
                result.rejected_candidates.append(f"event:{candidate.summary}:invalid_evidence")
                continue
            if any(sender_id not in allowed_senders for sender_id in candidate.actor_sender_ids):
                result.rejected_candidates.append(f"event:{candidate.summary}:unknown_sender")
                continue
            evidence_refs = [_evidence_ref(message) for message in evidence_messages]
            evidence_ids = [ref.source_id for ref in evidence_refs]
            occurred_at = max(message.sent_at for message in evidence_messages)
            event_id = _stable_id(
                "event",
                candidate.event_type,
                candidate.summary,
                *sorted(candidate.message_ids),
            )
            result.events.append(
                ContextEvent(
                    id=event_id,
                    created_at=now,
                    updated_at=now,
                    evidence_refs=evidence_refs,
                    observations=[],
                    inferences=[
                        ContextInference(
                            statement=candidate.summary,
                            confidence=candidate.confidence,
                            status="hypothesis",
                            supporting_evidence_ids=evidence_ids,
                        )
                    ],
                    event_type=candidate.event_type,
                    occurred_at=occurred_at,
                    actor_person_ids=[person_ids[sender_id] for sender_id in candidate.actor_sender_ids],
                    related_object_ids=[],
                    summary=candidate.summary,
                    observed_facts=[],
                    confidence=candidate.confidence,
                    created_by="model",
                )
            )

        for candidate in payload.opportunities:
            evidence_messages = _candidate_evidence(candidate.message_ids, messages_by_id)
            if evidence_messages is None:
                result.rejected_candidates.append(f"opportunity:{candidate.title}:invalid_evidence")
                continue
            if any(sender_id not in allowed_senders for sender_id in candidate.person_sender_ids):
                result.rejected_candidates.append(f"opportunity:{candidate.title}:unknown_sender")
                continue
            first_seen_at, last_signal_at = _time_bounds(evidence_messages)
            evidence_refs = [_evidence_ref(message) for message in evidence_messages]
            evidence_ids = [ref.source_id for ref in evidence_refs]
            opportunity_id = _stable_id(
                "opportunity",
                candidate.title.casefold(),
                *sorted(candidate.message_ids),
            )
            opportunity_ids_by_title[candidate.title.casefold()] = opportunity_id
            result.opportunities.append(
                Opportunity(
                    id=opportunity_id,
                    created_at=now,
                    updated_at=now,
                    evidence_refs=evidence_refs,
                    observations=[],
                    inferences=[
                        ContextInference(
                            statement=f"Potential opportunity: {candidate.title}",
                            confidence=candidate.confidence,
                            status="hypothesis",
                            supporting_evidence_ids=evidence_ids,
                        )
                    ],
                    title=candidate.title,
                    opportunity_type=candidate.opportunity_type,
                    stage="signal",
                    person_ids=[person_ids[sender_id] for sender_id in candidate.person_sender_ids],
                    organization_ids=[],
                    project_ids=[],
                    problem=candidate.problem,
                    proposed_value=candidate.proposed_value,
                    estimated_value=candidate.estimated_value,
                    currency=candidate.currency,
                    urgency=candidate.urgency,
                    fit=candidate.fit,
                    probability=candidate.probability,
                    next_actions=candidate.next_actions,
                    risk_ids=[],
                    first_seen_at=first_seen_at,
                    last_signal_at=last_signal_at,
                )
            )

        for candidate in payload.commitments:
            evidence_messages = _candidate_evidence(candidate.message_ids, messages_by_id)
            if evidence_messages is None:
                result.rejected_candidates.append(f"commitment:{candidate.summary}:invalid_evidence")
                continue
            if candidate.owner_sender_id not in allowed_senders:
                result.rejected_candidates.append(f"commitment:{candidate.summary}:unknown_owner")
                continue
            if any(sender_id not in allowed_senders for sender_id in candidate.beneficiary_sender_ids):
                result.rejected_candidates.append(f"commitment:{candidate.summary}:unknown_beneficiary")
                continue
            evidence_refs = [_evidence_ref(message) for message in evidence_messages]
            evidence_ids = [ref.source_id for ref in evidence_refs]
            commitment_id = _stable_id(
                "commitment",
                candidate.owner_sender_id,
                candidate.summary.casefold(),
                *sorted(candidate.message_ids),
            )
            related_opportunity_ids = [
                opportunity_ids_by_title[title.casefold()]
                for title in candidate.related_opportunity_titles
                if title.casefold() in opportunity_ids_by_title
            ]
            result.commitments.append(
                Commitment(
                    id=commitment_id,
                    created_at=now,
                    updated_at=now,
                    evidence_refs=evidence_refs,
                    observations=[],
                    inferences=[
                        ContextInference(
                            statement=f"Possible commitment: {candidate.summary}",
                            confidence=candidate.confidence,
                            status="hypothesis",
                            supporting_evidence_ids=evidence_ids,
                        )
                    ],
                    owner_person_id=person_ids[candidate.owner_sender_id],
                    beneficiary_person_ids=[
                        person_ids[sender_id] for sender_id in candidate.beneficiary_sender_ids
                    ],
                    summary=candidate.summary,
                    status="open",
                    due_at=candidate.due_at,
                    related_person_ids=[
                        person_ids[sender_id] for sender_id in candidate.beneficiary_sender_ids
                    ],
                    related_project_ids=[],
                    related_opportunity_ids=related_opportunity_ids,
                    confidence=candidate.confidence,
                )
            )

        return result

    def _build_persons(
        self,
        sender_messages: dict[str, list[IntelligenceMessage]],
        now: datetime,
    ) -> list[Person]:
        persons: list[Person] = []
        for sender_id, messages in sorted(sender_messages.items()):
            ordered = sorted(messages, key=lambda message: message.sent_at)
            latest = ordered[-1]
            display_name = next(
                (
                    message.sender_name
                    for message in reversed(ordered)
                    if message.sender_name and message.sender_name.strip()
                ),
                sender_id,
            )
            evidence_refs = [_evidence_ref(message) for message in ordered]
            persons.append(
                Person(
                    id=_person_id(latest),
                    created_at=now,
                    updated_at=now,
                    evidence_refs=evidence_refs,
                    observations=[f"Observed sender identity {sender_id}"],
                    inferences=[],
                    display_name=display_name,
                    aliases=[],
                    identities={latest.platform: [sender_id]},
                    organization=None,
                    roles=[],
                    locations=[],
                    interests=[],
                    expertise=[],
                    relationship_ids=[],
                    opportunity_ids=[],
                    project_ids=[],
                    commitment_ids=[],
                    last_meaningful_interaction_at=max(message.sent_at for message in ordered),
                    confidence=1.0,
                )
            )
        return persons
