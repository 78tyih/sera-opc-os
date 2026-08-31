from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, model_validator


EvidenceSourceType = Literal[
    "message",
    "file",
    "calendar",
    "project",
    "table",
    "account",
    "agent_run",
    "user_confirmation",
]
InferenceStatus = Literal[
    "hypothesis",
    "supported",
    "confirmed_by_user",
    "rejected_by_user",
    "superseded",
]


class ContextEvidenceRef(BaseModel):
    source_type: EvidenceSourceType
    source_id: str
    platform: str | None = None
    account_id: str | None = None
    conversation_id: str | None = None
    message_id: int | None = None
    occurred_at: datetime | None = None


class ContextInference(BaseModel):
    statement: str
    confidence: float = Field(ge=0, le=1)
    status: InferenceStatus = "hypothesis"
    supporting_evidence_ids: list[str] = Field(default_factory=list)
    contradicting_evidence_ids: list[str] = Field(default_factory=list)
    user_confirmation_ref: str | None = None

    @model_validator(mode="after")
    def validate_confirmation(self) -> "ContextInference":
        if self.status == "confirmed_by_user" and not self.user_confirmation_ref:
            raise ValueError("confirmed_by_user inference requires user_confirmation_ref")
        return self


class ContextObject(BaseModel):
    id: str
    created_at: datetime
    updated_at: datetime
    evidence_refs: list[ContextEvidenceRef] = Field(default_factory=list)
    observations: list[str] = Field(default_factory=list)
    inferences: list[ContextInference] = Field(default_factory=list)


EventType = Literal[
    "message",
    "meeting",
    "commitment",
    "decision",
    "transaction",
    "project_change",
    "relationship_signal",
    "self_signal",
    "other",
]


class ContextEvent(ContextObject):
    event_type: EventType
    occurred_at: datetime
    actor_person_ids: list[str] = Field(default_factory=list)
    related_object_ids: list[str] = Field(default_factory=list)
    summary: str
    observed_facts: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1)
    created_by: Literal["rule", "model", "user"]


class Person(ContextObject):
    display_name: str
    aliases: list[str] = Field(default_factory=list)
    identities: dict[str, list[str]] = Field(default_factory=dict)
    organization: str | None = None
    roles: list[str] = Field(default_factory=list)
    locations: list[str] = Field(default_factory=list)
    interests: list[str] = Field(default_factory=list)
    expertise: list[str] = Field(default_factory=list)
    relationship_ids: list[str] = Field(default_factory=list)
    opportunity_ids: list[str] = Field(default_factory=list)
    project_ids: list[str] = Field(default_factory=list)
    commitment_ids: list[str] = Field(default_factory=list)
    last_meaningful_interaction_at: datetime | None = None
    confidence: float = Field(ge=0, le=1)


RelationshipTrend = Literal["warming", "stable", "cooling", "reactivated", "unknown"]


class Relationship(ContextObject):
    from_person_id: str
    to_person_id: str
    contexts: list[str] = Field(default_factory=list)
    strength_score: float = Field(ge=0, le=1)
    recency_score: float = Field(ge=0, le=1)
    reciprocity_score: float = Field(ge=0, le=1)
    trend: RelationshipTrend = "unknown"
    shared_topic_ids: list[str] = Field(default_factory=list)
    shared_project_ids: list[str] = Field(default_factory=list)
    shared_opportunity_ids: list[str] = Field(default_factory=list)
    open_commitment_ids: list[str] = Field(default_factory=list)


OpportunityStage = Literal["signal", "qualified", "exploring", "negotiating", "won", "lost", "parked"]
OpportunityType = Literal[
    "customer",
    "partnership",
    "product",
    "investment",
    "distribution",
    "resource",
    "introduction",
    "other",
]


class Opportunity(ContextObject):
    title: str
    opportunity_type: OpportunityType
    stage: OpportunityStage = "signal"
    person_ids: list[str] = Field(default_factory=list)
    organization_ids: list[str] = Field(default_factory=list)
    project_ids: list[str] = Field(default_factory=list)
    problem: str | None = None
    proposed_value: str | None = None
    estimated_value: float | None = Field(default=None, ge=0)
    currency: str | None = None
    urgency: float = Field(ge=0, le=1)
    fit: float = Field(ge=0, le=1)
    probability: float = Field(ge=0, le=1)
    next_actions: list[str] = Field(default_factory=list)
    risk_ids: list[str] = Field(default_factory=list)
    first_seen_at: datetime
    last_signal_at: datetime


CommitmentStatus = Literal["open", "done", "cancelled", "overdue", "unknown"]


class Commitment(ContextObject):
    owner_person_id: str
    beneficiary_person_ids: list[str] = Field(default_factory=list)
    summary: str
    status: CommitmentStatus = "open"
    due_at: datetime | None = None
    related_person_ids: list[str] = Field(default_factory=list)
    related_project_ids: list[str] = Field(default_factory=list)
    related_opportunity_ids: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1)


RiskStatus = Literal["watching", "active", "mitigated", "resolved", "dismissed"]


class Risk(ContextObject):
    title: str
    risk_type: str
    severity: float = Field(ge=0, le=1)
    likelihood: float = Field(ge=0, le=1)
    status: RiskStatus = "watching"
    related_person_ids: list[str] = Field(default_factory=list)
    related_project_ids: list[str] = Field(default_factory=list)
    related_opportunity_ids: list[str] = Field(default_factory=list)
    triggers: list[str] = Field(default_factory=list)
    mitigations: list[str] = Field(default_factory=list)
    first_seen_at: datetime
    last_signal_at: datetime


TopicMomentum = Literal["rising", "stable", "falling", "episodic"]


class Topic(ContextObject):
    name: str
    aliases: list[str] = Field(default_factory=list)
    summary: str
    momentum: TopicMomentum = "stable"
    attention_score: float = Field(ge=0, le=1)
    personal_relevance: float = Field(ge=0, le=1)
    related_person_ids: list[str] = Field(default_factory=list)
    related_project_ids: list[str] = Field(default_factory=list)
    related_opportunity_ids: list[str] = Field(default_factory=list)
    first_seen_at: datetime
    last_seen_at: datetime


class ProjectContext(ContextObject):
    canonical_project_ref: str | None = None
    name: str
    status: str
    person_ids: list[str] = Field(default_factory=list)
    opportunity_ids: list[str] = Field(default_factory=list)
    commitment_ids: list[str] = Field(default_factory=list)
    risk_ids: list[str] = Field(default_factory=list)
    topic_ids: list[str] = Field(default_factory=list)
    recent_event_ids: list[str] = Field(default_factory=list)
    current_state_summary: str
    next_actions: list[str] = Field(default_factory=list)


SelfSignalType = Literal[
    "attention",
    "preference",
    "behavior_pattern",
    "goal",
    "concern",
    "transition",
    "decision_style",
    "interest_shift",
]
SelfEvidenceLevel = Literal[0, 1, 2, 3, 4]


class SelfSignal(ContextObject):
    signal_type: SelfSignalType
    statement: str
    window_start: datetime
    window_end: datetime
    supporting_event_ids: list[str] = Field(default_factory=list)
    contradicting_event_ids: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1)
    status: InferenceStatus = "hypothesis"
    evidence_level: SelfEvidenceLevel = 2
    source_diversity: int = Field(default=1, ge=1)
    user_confirmation_ref: str | None = None

    @model_validator(mode="after")
    def validate_self_signal(self) -> "SelfSignal":
        if self.window_end < self.window_start:
            raise ValueError("window_end must be >= window_start")
        if self.evidence_level >= 2 and not self.supporting_event_ids:
            raise ValueError("pattern-level SelfSignal requires supporting_event_ids")
        if self.evidence_level >= 3 and self.source_diversity < 2:
            raise ValueError("cross-source SelfSignal requires source_diversity >= 2")
        if self.evidence_level == 4:
            if self.status != "confirmed_by_user":
                raise ValueError("level 4 SelfSignal must be confirmed_by_user")
            if not self.user_confirmation_ref:
                raise ValueError("level 4 SelfSignal requires user_confirmation_ref")
        return self
