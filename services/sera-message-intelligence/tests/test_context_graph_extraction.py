from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sera_message_intelligence.context_graph.extraction import ContextGraphExtractor
from sera_message_intelligence.context_graph.pipeline import extract_context_candidates
from sera_message_intelligence.intelligence.schemas import IntelligenceMessage


class FakeLLM:
    def __init__(self, payload: dict[str, Any]):
        self.payload = payload

    def generate_json(self, *, system: str, prompt: str) -> dict[str, Any]:
        assert "Do not invent identities" in system
        assert "Allowed sender refs" in prompt
        return self.payload


def message(
    message_id: int,
    sender_id: str,
    sender_name: str,
    text: str,
    minute: int,
    *,
    account_id: str = "acct-main",
) -> IntelligenceMessage:
    return IntelligenceMessage(
        id=message_id,
        platform="wechat",
        account_id=account_id,
        conversation_id="group-1",
        conversation_name="Industry Group",
        sender_id=sender_id,
        sender_name=sender_name,
        sent_at=datetime(2026, 8, 31, 4, minute, tzinfo=timezone.utc),
        message_type="text",
        text_content=text,
    )


def sender_ref(sender_id: str, account_id: str = "acct-main") -> str:
    return f"wechat:{account_id}:{sender_id}"


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
                    "actor_sender_refs": [sender_ref("alice"), sender_ref("me")],
                    "message_ids": [101, 102],
                    "confidence": 0.91,
                }
            ],
            "opportunities": [
                {
                    "title": "AI client-group intelligence demo",
                    "opportunity_type": "customer",
                    "person_sender_refs": [sender_ref("alice")],
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
                    "owner_sender_ref": sender_ref("me"),
                    "beneficiary_sender_refs": [sender_ref("alice")],
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
                    "person_sender_refs": [sender_ref("alice")],
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
                    "person_sender_refs": ["wechat:acct-main:bob-who-never-appeared"],
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
                    "owner_sender_ref": "wechat:acct-main:ghost",
                    "beneficiary_sender_refs": [],
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


def test_same_sender_id_on_two_accounts_does_not_merge_people() -> None:
    messages = [
        message(101, "shared-id", "Alice on A", "hello", 1, account_id="acct-a"),
        message(102, "shared-id", "Alice on B", "hello", 2, account_id="acct-b"),
    ]
    empty_llm = FakeLLM({"events": [], "opportunities": [], "commitments": []})

    result = ContextGraphExtractor(empty_llm).extract(messages)

    assert len(result.persons) == 2
    assert result.persons[0].id != result.persons[1].id
    evidence_accounts = {person.evidence_refs[0].account_id for person in result.persons}
    assert evidence_accounts == {"acct-a", "acct-b"}


def test_pipeline_merges_same_person_across_bounded_chunks() -> None:
    messages = [
        message(101, "alice", "Alice", "first message is long enough to force a chunk", 1),
        message(102, "alice", "Alice A.", "second message is also long enough to force a chunk", 2),
    ]
    empty_llm = FakeLLM({"events": [], "opportunities": [], "commitments": []})

    result = extract_context_candidates(messages=messages, llm=empty_llm, max_chars=100)

    assert len(result.persons) == 1
    person = result.persons[0]
    assert person.display_name == "Alice A."
    assert [ref.message_id for ref in person.evidence_refs] == [101, 102]
    assert "Alice" in person.aliases


def test_empty_batch_does_not_call_llm() -> None:
    class ExplodingLLM:
        def generate_json(self, *, system: str, prompt: str) -> dict[str, Any]:
            raise AssertionError("LLM must not be called for an empty batch")

    result = ContextGraphExtractor(ExplodingLLM()).extract([])
    assert result.persons == []
    assert result.events == []
    assert result.opportunities == []
    assert result.commitments == []
