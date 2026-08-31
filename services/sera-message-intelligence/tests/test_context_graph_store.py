from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from sera_message_intelligence.context_graph.extraction import ContextExtractionResult
from sera_message_intelligence.context_graph.schemas import (
    Commitment,
    ContextEvidenceRef,
    ContextInference,
    Opportunity,
    Person,
)
from sera_message_intelligence.context_graph.store import (
    list_graph_objects,
    upsert_context_result,
)
from sera_message_intelligence.db import Base


BASE_TIME = datetime(2026, 8, 31, 4, 0, tzinfo=timezone.utc)


def engine():
    value = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(value)
    return value


def evidence(message_id: int, minute: int = 0) -> ContextEvidenceRef:
    return ContextEvidenceRef(
        source_type="message",
        source_id=f"message:wechat:acct:{message_id}",
        platform="wechat",
        account_id="acct",
        conversation_id="group",
        message_id=message_id,
        occurred_at=BASE_TIME + timedelta(minutes=minute),
    )


def person(person_id: str = "person_alice") -> Person:
    ref = evidence(1)
    return Person(
        id=person_id,
        created_at=BASE_TIME,
        updated_at=BASE_TIME,
        evidence_refs=[ref],
        observations=["Observed sender identity wechat:acct:alice"],
        inferences=[],
        display_name="Alice",
        aliases=[],
        identities={"wechat": ["alice"]},
        organization=None,
        roles=[],
        locations=[],
        interests=[],
        expertise=[],
        relationship_ids=[],
        opportunity_ids=[],
        project_ids=[],
        commitment_ids=[],
        last_meaningful_interaction_at=BASE_TIME,
        confidence=1.0,
    )


def opportunity(
    object_id: str,
    message_id: int,
    minute: int,
    *,
    title: str = "AI Client Group Demo",
    person_ids: list[str] | None = None,
    probability: float = 0.5,
) -> Opportunity:
    ref = evidence(message_id, minute)
    seen = BASE_TIME + timedelta(minutes=minute)
    return Opportunity(
        id=object_id,
        created_at=seen,
        updated_at=seen,
        evidence_refs=[ref],
        observations=[],
        inferences=[
            ContextInference(
                statement=f"Potential opportunity: {title}",
                confidence=0.8,
                status="hypothesis",
                supporting_evidence_ids=[ref.source_id],
            )
        ],
        title=title,
        opportunity_type="customer",
        stage="signal",
        person_ids=person_ids or ["person_alice"],
        organization_ids=[],
        project_ids=[],
        problem="Too much information",
        proposed_value="AI intelligence",
        estimated_value=None,
        currency=None,
        urgency=0.7,
        fit=0.8,
        probability=probability,
        next_actions=["Send demo"],
        risk_ids=[],
        first_seen_at=seen,
        last_signal_at=seen,
    )


def commitment(
    object_id: str,
    message_id: int,
    minute: int,
    opportunity_id: str,
    *,
    due_at: datetime | None = None,
) -> Commitment:
    ref = evidence(message_id, minute)
    seen = BASE_TIME + timedelta(minutes=minute)
    return Commitment(
        id=object_id,
        created_at=seen,
        updated_at=seen,
        evidence_refs=[ref],
        observations=[],
        inferences=[
            ContextInference(
                statement="Possible commitment: Send demo",
                confidence=0.9,
                status="hypothesis",
                supporting_evidence_ids=[ref.source_id],
            )
        ],
        owner_person_id="person_me",
        beneficiary_person_ids=["person_alice"],
        summary="Send demo",
        status="open",
        due_at=due_at,
        related_person_ids=["person_alice"],
        related_project_ids=[],
        related_opportunity_ids=[opportunity_id],
        confidence=0.9,
    )


def test_same_exact_opportunity_signature_updates_one_durable_object() -> None:
    db = engine()
    first = opportunity("opp_first", 10, 1, probability=0.4)
    second = opportunity("opp_second", 11, 20, title="AI client-group demo!", probability=0.7)

    with Session(db) as session:
        first_summary = upsert_context_result(
            session,
            ContextExtractionResult(persons=[person()], opportunities=[first]),
        )
        second_summary = upsert_context_result(
            session,
            ContextExtractionResult(persons=[person()], opportunities=[second]),
        )
        records = list_graph_objects(session, "opportunity")

    assert first_summary.created == 2
    assert second_summary.updated == 2
    assert len(records) == 1
    assert second_summary.resolved_ids["opp_second"] == "opp_first"
    assert records[0].object_id == "opp_first"
    assert records[0].evidence_count == 2
    assert records[0].payload["probability"] == 0.7


def test_same_title_with_different_person_does_not_merge() -> None:
    db = engine()
    first = opportunity("opp_alice", 10, 1, person_ids=["person_alice"])
    second = opportunity("opp_bob", 11, 2, person_ids=["person_bob"])

    with Session(db) as session:
        upsert_context_result(session, ContextExtractionResult(opportunities=[first]))
        upsert_context_result(session, ContextExtractionResult(opportunities=[second]))
        records = list_graph_objects(session, "opportunity")

    assert len(records) == 2
    assert {record.object_id for record in records} == {"opp_alice", "opp_bob"}


def test_commitment_remaps_transient_opportunity_id_to_durable_id() -> None:
    db = engine()
    first = opportunity("opp_first", 10, 1)
    later = opportunity("opp_later", 11, 5, title="AI client group demo")
    followup = commitment("commit_1", 12, 6, "opp_later")

    with Session(db) as session:
        upsert_context_result(session, ContextExtractionResult(opportunities=[first]))
        summary = upsert_context_result(
            session,
            ContextExtractionResult(opportunities=[later], commitments=[followup]),
        )
        commitments = list_graph_objects(session, "commitment")

    assert summary.resolved_ids["opp_later"] == "opp_first"
    assert len(commitments) == 1
    assert commitments[0].payload["related_opportunity_ids"] == ["opp_first"]


def test_conflicting_commitment_due_date_is_preserved_as_inference() -> None:
    db = engine()
    original_due = BASE_TIME + timedelta(days=1)
    conflicting_due = BASE_TIME + timedelta(days=2)
    first = commitment("commit_first", 20, 1, "opp_x", due_at=original_due)
    second = commitment("commit_second", 21, 2, "opp_x", due_at=conflicting_due)

    with Session(db) as session:
        upsert_context_result(session, ContextExtractionResult(commitments=[first]))
        summary = upsert_context_result(session, ContextExtractionResult(commitments=[second]))
        records = list_graph_objects(session, "commitment")

    assert summary.resolved_ids["commit_second"] == "commit_first"
    assert len(records) == 1
    assert records[0].payload["due_at"] == original_due.isoformat().replace("+00:00", "Z") or records[0].payload["due_at"] == original_due.isoformat()
    statements = [item["statement"] for item in records[0].payload["inferences"]]
    assert any("Conflicting commitment due dates observed" in statement for statement in statements)
