from __future__ import annotations
from datetime import date, datetime
from typing import Literal
from pydantic import BaseModel, Field

class IntelligenceMessage(BaseModel):
    id: int
    platform: str
    account_id: str
    conversation_id: str
    conversation_name: str | None = None
    sender_id: str
    sender_name: str | None = None
    sent_at: datetime
    message_type: str
    text_content: str | None = None

class MessageChunk(BaseModel):
    chunk_id: str
    platform: str
    account_id: str
    conversation_id: str
    conversation_name: str | None = None
    message_ids: list[int]
    messages: list[IntelligenceMessage]

ClaimKind = Literal["key_point","action","decision","risk","opportunity","resource"]

class ChunkClaim(BaseModel):
    kind: ClaimKind
    text: str
    message_ids: list[int] = Field(min_length=1)

class ChunkSummary(BaseModel):
    chunk_id: str
    conversation_id: str
    conversation_name: str | None = None
    message_ids: list[int]
    summary: str
    claims: list[ChunkClaim] = Field(default_factory=list)

class ImportanceComponents(BaseModel):
    personal_relevance: float = Field(ge=0, le=1)
    actionability: float = Field(ge=0, le=1)
    urgency: float = Field(ge=0, le=1)
    novelty: float = Field(ge=0, le=1)
    source_weight: float = Field(ge=0, le=1)

    def score(self) -> float:
        return round(0.30*self.personal_relevance + 0.25*self.actionability + 0.20*self.urgency + 0.15*self.novelty + 0.10*self.source_weight, 4)

BriefCategory = Literal["must_handle","important","actions","decisions","opportunities","risks","people_to_reply","resources","knowledge","topics"]

class CandidateItem(BaseModel):
    category: BriefCategory
    title: str
    summary: str
    message_ids: list[int] = Field(min_length=1)
    confidence: float = Field(ge=0, le=1)
    importance: ImportanceComponents

class SourceRef(BaseModel):
    platform: str
    account_id: str
    conversation_id: str
    conversation_name: str | None = None
    message_ids: list[int]

class BriefItem(BaseModel):
    title: str
    summary: str
    importance_score: float = Field(ge=0, le=1)
    confidence: float = Field(ge=0, le=1)
    sources: list[SourceRef]

class DailyBrief(BaseModel):
    date: date
    executive_summary: str
    must_handle: list[BriefItem] = Field(default_factory=list)
    important: list[BriefItem] = Field(default_factory=list)
    actions: list[BriefItem] = Field(default_factory=list)
    decisions: list[BriefItem] = Field(default_factory=list)
    opportunities: list[BriefItem] = Field(default_factory=list)
    risks: list[BriefItem] = Field(default_factory=list)
    people_to_reply: list[BriefItem] = Field(default_factory=list)
    resources: list[BriefItem] = Field(default_factory=list)
    knowledge: list[BriefItem] = Field(default_factory=list)
    topics: list[BriefItem] = Field(default_factory=list)
