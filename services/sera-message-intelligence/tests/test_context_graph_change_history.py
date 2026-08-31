from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from sera_message_intelligence.context_graph.change_history import list_graph_changes
from sera_message_intelligence.context_graph.extraction import ContextExtractionResult
from sera_message_intelligence.context_graph.schemas import (
    Commitment,
    ContextEvidenceRef,
    ContextInference,
    Opportunity,
    Person,
)
from sera_message_intelligence.context_graph.store import upsert_context_result
from sera_message_intelligence.db import Base


BASE = datetime(2026, 8, 31, 4, 0, tzinfo=timezone.utc)


def engine():
    value = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(value)
    return value


def evidence(message_id: int, minute: int) -> ContextEvidenceRef:
    return ContextEvidenceRef(
        source_type="message",
        source_id=f"message:wechat:acct:{message_id}",
        platform="wechat",
        account_id="acct",
        conversation_id="group",
        message_id=message_id,
        occurred_at=BASE + timedelta(minutes=minute),
    )


def person(ref: ContextEvidenceRef) -> Person:
    return Person(
        id="person_alice",
        created_at=BASE,
        updated_at=BASE,
        evidence_refs=[ref],
        observations=["Observed sender identity"],
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
        last_meaningful_interaction_at=ref.occurred_at,
        confidence=1.0,
    )


def opportunity(
    object_id: str,
    ref: ContextEvidenceRef,
    *,
    probability: float,
) -> Opportunity:
    return Opportunity(
        id=object_id,
        created_at=ref.occurred_at or BASE,
        updated_at=ref.occurred_at or BASE,
        evidence_refs=[ref],
        observations=[],
        inferences=[
            ContextInference(
                statement="Potential opportunity: Demo",
                confidence=0.8,
                status="hypothesis",
                supporting_evidence_ids=[ref.source_id],
            )
        ],
        title="AI client group demo",
        opportunity_type="customer",
        stage="signal",
        person_ids=["person_alice"],
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
        first_seen_at=ref.occurred_at or BASE,
        last_signal_at=ref.occurred_at or BASE,
    )


def commitment(
    object_id: str,
    ref: ContextEvidenceRef,
    *,
    due_at: datetime,
) -> Commitment:
    return Commitment(
        id=object_id,
        created_at=ref.occurred_at or BASE,
        updated_at=ref.occurred_at or BASE,
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
        related_opportunity_ids=[],
        confidence=0.9,
    )


def test_creation_writes_append_only_change_rows() -> None:
    db = engine()
    ref = evidence(1, 1)
    extracted = ContextExtractionResult(
        persons=[person(ref)],
        opportunities=[opportunity("opp_1", ref, probability=0.4)],
    )

    with Session(db) as session:
        summary = upsert_context_result(session, extracted)
        changes = list_graph_changes(session)

    assert summary.created == 2
    assert summary.changes_recorded == 2
    assert len(changes) == 2
    assert {change.change_kind for change in changes} == {"created"}
    assert all(change.semantic_changes == ["object_created"] for change in changes)
    assert all(change.batch_id == summary.batch_id for change in changes)


def test_rerunning_identical_durable_state_does_not_create_history_noise() -> None:
    db = engine()
    ref = evidence(1, 1)
    extracted = ContextExtractionResult(
        persons=[person(ref)],
        opportunities=[opportunity("opp_1", ref, probability=0.4)],
    )

    with Session(db) as session:
        first = upsert_context_result(session, extracted)
        second = upsert_context_result(session, extracted)
        changes = list_graph_changes(session)

    assert first.changes_recorded == 2
    assert second.changes_recorded == 0
    assert len(changes) == 2


def test_new_opportunity_signal_records_evidence_and_probability_change() -> None:
    db = engine()
    first_ref = evidence(10, 1)
    second_ref = evidence(11, 20)

    with Session(db) as session:
        upsert_context_result(
            session,
            ContextExtractionResult(
                opportunities=[opportunity("opp_first", first_ref, probability=0.4)]
            ),
        )
        summary = upsert_context_result(
            session,
            ContextExtractionResult(
                opportunities=[opportunity("opp_second", second_ref, probability=0.75)]
            ),
        )
        changes = list_graph_changes(session, object_type="opportunity")

    assert summary.changes_recorded == 1
    assert len(changes) == 2
    latest = changes[-1]
    assert latest.change_kind == "updated"
    assert "new_evidence" in latest.semantic_changes
    assert "opportunity_signal_changed" in latest.semantic_changes
    assert "probability" in latest.changed_fields
    assert latest.evidence_ids == [second_ref.source_id]
    assert latest.after_payload["probability"] == 0.75


def test_conflicting_commitment_deadline_is_recorded_as_conflict_not_silent_overwrite() -> None:
    db = engine()
    original_due = BASE + timedelta(days=1)
    conflicting_due = BASE + timedelta(days=2)
    first_ref = evidence(20, 1)
    second_ref = evidence(21, 2)

    with Session(db) as session:
        upsert_context_result(
            session,
            ContextExtractionResult(
                commitments=[commitment("commit_first", first_ref, due_at=original_due)]
            ),
        )
        upsert_context_result(
            session,
            ContextExtractionResult(
                commitments=[commitment("commit_second", second_ref, due_at=conflicting_due)]
            ),
        )
        changes = list_graph_changes(session, object_type="commitment")

    assert len(changes) == 2
    latest = changes[-1]
    assert "conflict_added" in latest.semantic_changes
    assert "new_evidence" in latest.semantic_changes
    assert "inferences" in latest.changed_fields
    # The durable deadline remains the original one; the conflict is preserved separately.
    assert latest.after_payload["due_at"] in {
        original_due.isoformat(),
        original_due.isoformat().replace("+00:00", "Z"),
    }
