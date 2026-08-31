from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sera_message_intelligence.context_graph.extraction import ContextGraphExtractor
from sera_message_intelligence.intelligence.schemas import IntelligenceMessage


class FakeLLM:
    def __init__(self, payload: dict[str, Any]):
        self.payload = payload

    def generate_json(self, *, system: str, prompt: str) -> dict[str, Any]:
        assert "Do not invent identities" in system
        assert "Allowed sender IDs" in prompt
        return self.payload


def message(
    message_id: int,
    sender_id: str,
    sender_name: str,
    text: str,
    minute: int,
) -> IntelligenceMessage:
    return IntelligenceMessage(
        id=message_id,
        platform="wechat",
        account_id="acct-main",
        conversation_id="group-1",
        conversation_name="Industry Group",
        sender_id=sender_id,
        sender_name=sender_name,
        sent_at=datetime(2026, 8, 31, 4, minute, tzinfo=timezone.utc),
        message_type="text",
        text_content=text,
    )


def test_extracts_sender_backed_person_opportunity_commitment_and_event() -> None:
    messages = [
        message(101, "alice", "Alice", "We need an AI system to summarize our client groups.", 1),
        message(102, "me", "Sera", "I can send you a demo tomorrow.", 2),
    ]
    llm = FakeLLM(
        {
            "events": [
                {
                    "event_type": "relationship_signal",
                    "summary": "Alice expressed a concrete product need and Sera offered a demo.",
                    "actor_sender_ids": ["alice", "me"],
                    "message_ids": [101, 102],
                    "confidence": 0.91,
                }
            ],
            "opportunities": [
                {
                    "title": "AI client-group intelligence demo",
                    "opportunity_type": "customer",
                    "person_sender_ids": ["alice"],
                    "problem": "Too much client-group information to review manually.",
                    "proposed_value": "AI message intelligence demo.",
                    "estimated_value": None,
                    "currency": None,
                    "urgency": 0.8,
                    "fit": 0.95,
                    "probability": 0.65,
                    "next_actions": ["Send demo"],
                    "message_ids": [101, 102],
                    "confidence": 0.9,
                }
            ],
            "commitments": [
                {
                    "owner_sender_id": "me",
                    "beneficiary_sender_ids": ["alice"],
                    "summary": "Send Alice a demo tomorrow.",
                    "due_at": "2026-09-01T12:00:00Z",
                    "related_opportunity_titles": ["AI client-group intelligence demo"],
                    "message_ids": [102],
                    "confidence": 0.94,
                }
            ],
        }
    )

    result = ContextGraphExtractor(llm).extract(messages)

    assert {person.display_name for person in result.persons} == {"Alice", "Sera"}
    assert len(result.events) == 1
    assert len(result.opportunities) == 1
    assert len(result.commitments) == 1
    assert not result.rejected_candidates

    opportunity = result.opportunities[0]
    assert opportunity.stage == "signal"
    assert opportunity.evidence_refs[0].message_id == 101
    assert opportunity.inferences[0].status == "hypothesis"
    assert opportunity.person_ids

    commitment = result.commitments[0]
    assert commitment.owner_person_id != commitment.beneficiary_person_ids[0]
    assert commitment.related_opportunity_ids == [opportunity.id]
    assert commitment.evidence_refs[0].message_id == 102


def test_rejects_candidate_that_cites_unknown_message_id() -> None:
    messages = [message(101, "alice", "Alice", "Maybe we should work together.", 1)]
    llm = FakeLLM(
        {
            "events": [],
            "opportunities": [
                {
                    "title": "Invented opportunity",
                    "opportunity_type": "partnership",
                    "person_sender_ids": ["alice"],
                    "problem": None,
                    "proposed_value": None,
                    "estimated_value": None,
                    "currency": None,
                    "urgency": 0.5,
                    "fit": 0.5,
                    "probability": 0.5,
                    "next_actions": [],
                    "message_ids": [999],
                    "confidence": 0.9,
                }
            ],
            "commitments": [],
        }
    )

    result = ContextGraphExtractor(llm).extract(messages)

    assert result.opportunities == []
    assert result.rejected_candidates == ["opportunity:Invented opportunity:invalid_evidence"]


def test_rejects_unknown_sender_identity_in_model_output() -> None:
    messages = [message(101, "alice", "Alice", "We may have a distribution opportunity.", 1)]
    llm = FakeLLM(
        {
            "events": [],
            "opportunities": [
                {
                    "title": "Distribution lead",
                    "opportunity_type": "distribution",
                    "person_sender_ids": ["bob-who-never-appeared"],
                    "problem": None,
                    "proposed_value": None,
                    "estimated_value": None,
                    "currency": None,
                    "urgency": 0.7,
                    "fit": 0.8,
                    "probability": 0.6,
                    "next_actions": [],
                    "message_ids": [101],
                    "confidence": 0.8,
                }
            ],
            "commitments": [
                {
                    "owner_sender_id": "ghost",
                    "beneficiary_sender_ids": [],
                    "summary": "Ghost promised something.",
                    "due_at": None,
                    "related_opportunity_titles": [],
                    "message_ids": [101],
                    "confidence": 0.8,
                }
            ],
        }
    )

    result = ContextGraphExtractor(llm).extract(messages)

    assert result.opportunities == []
    assert result.commitments == []
    assert "opportunity:Distribution lead:unknown_sender" in result.rejected_candidates
    assert "commitment:Ghost promised something.:unknown_owner" in result.rejected_candidates


def test_person_identity_is_deterministic_and_not_model_invented() -> None:
    messages = [
        message(101, "alice", "Alice", "hello", 1),
        message(102, "alice", "Alice A.", "updated display name", 2),
    ]
    empty_llm = FakeLLM({"events": [], "opportunities": [], "commitments": []})

    first = ContextGraphExtractor(empty_llm).extract(messages)
    second = ContextGraphExtractor(empty_llm).extract(messages)

    assert len(first.persons) == 1
    assert first.persons[0].id == second.persons[0].id
    assert first.persons[0].display_name == "Alice A."
    assert first.persons[0].identities == {"wechat": ["alice"]}
    assert first.persons[0].organization is None
    assert first.persons[0].roles == []
    assert first.persons[0].inferences == []


def test_empty_batch_does_not_call_llm() -> None:
    class ExplodingLLM:
        def generate_json(self, *, system: str, prompt: str) -> dict[str, Any]:
            raise AssertionError("LLM must not be called for an empty batch")

    result = ContextGraphExtractor(ExplodingLLM()).extract([])
    assert result.persons == []
    assert result.events == []
    assert result.opportunities == []
    assert result.commitments == []
