from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sera_message_intelligence.context_graph.radar import build_context_radar
from sera_message_intelligence.context_graph.schemas import (
    Commitment,
    ContextEvidenceRef,
    ContextInference,
    Opportunity,
)
from sera_message_intelligence.models import ContextGraphObject


NOW = datetime(2026, 9, 10, 12, 0, tzinfo=timezone.utc)


def evidence(message_id: int, at: datetime) -> ContextEvidenceRef:
    return ContextEvidenceRef(
        source_type="message",
        source_id=f"message:wechat:acct:{message_id}",
        platform="wechat",
        account_id="acct",
        conversation_id="group",
        message_id=message_id,
        occurred_at=at,
    )


def opportunity_record(
    object_id: str,
    *,
    title: str,
    days_ago: int,
    fit: float,
    urgency: float,
    probability: float,
    evidence_count: int,
    stage: str = "signal",
) -> ContextGraphObject:
    last_signal = NOW - timedelta(days=days_ago)
    ref = evidence(100 + evidence_count, last_signal)
    obj = Opportunity(
        id=object_id,
        created_at=last_signal,
        updated_at=last_signal,
        evidence_refs=[ref],
        observations=[],
        inferences=[],
        title=title,
        opportunity_type="customer",
        stage=stage,
        person_ids=["person_alice"],
        organization_ids=[],
        project_ids=[],
        problem=None,
        proposed_value=None,
        estimated_value=None,
        currency=None,
        urgency=urgency,
        fit=fit,
        probability=probability,
        next_actions=["Follow up"],
        risk_ids=[],
        first_seen_at=last_signal - timedelta(days=2),
        last_signal_at=last_signal,
    )
    return ContextGraphObject(
        object_id=object_id,
        object_type="opportunity",
        canonical_key=f"key:{object_id}",
        payload=obj.model_dump(mode="json"),
        first_seen_at=obj.first_seen_at,
        last_seen_at=obj.last_signal_at,
        evidence_count=evidence_count,
        created_at=last_signal,
        updated_at=last_signal,
    )


def commitment_record(
    object_id: str,
    *,
    summary: str,
    due_at: datetime | None,
    status: str = "open",
    evidence_count: int = 1,
    conflict: bool = False,
) -> ContextGraphObject:
    ref = evidence(200 + evidence_count, NOW - timedelta(days=1))
    inferences = []
    if conflict:
        inferences.append(
            ContextInference(
                statement="Conflicting commitment due dates observed: A vs B",
                confidence=0.9,
                status="hypothesis",
                supporting_evidence_ids=[ref.source_id],
            )
        )
    obj = Commitment(
        id=object_id,
        created_at=NOW - timedelta(days=2),
        updated_at=NOW - timedelta(days=1),
        evidence_refs=[ref],
        observations=[],
        inferences=inferences,
        owner_person_id="person_me",
        beneficiary_person_ids=["person_alice"],
        summary=summary,
        status=status,
        due_at=due_at,
        related_person_ids=["person_alice"],
        related_project_ids=[],
        related_opportunity_ids=["opp_1"],
        confidence=0.9,
    )
    return ContextGraphObject(
        object_id=object_id,
        object_type="commitment",
        canonical_key=f"key:{object_id}",
        payload=obj.model_dump(mode="json"),
        first_seen_at=obj.created_at,
        last_seen_at=obj.updated_at,
        evidence_count=evidence_count,
        created_at=obj.created_at,
        updated_at=obj.updated_at,
    )


def test_opportunity_radar_prefers_active_high_value_fresh_signal() -> None:
    strong = opportunity_record(
        "opp_strong",
        title="Strong fresh opportunity",
        days_ago=1,
        fit=0.95,
        urgency=0.9,
        probability=0.75,
        evidence_count=4,
    )
    weak = opportunity_record(
        "opp_weak",
        title="Weak stale opportunity",
        days_ago=25,
        fit=0.4,
        urgency=0.3,
        probability=0.3,
        evidence_count=1,
    )
    terminal = opportunity_record(
        "opp_terminal",
        title="Already won",
        days_ago=0,
        fit=1.0,
        urgency=1.0,
        probability=1.0,
        evidence_count=5,
        stage="won",
    )

    radar = build_context_radar(
        opportunity_records=[weak, terminal, strong],
        commitment_records=[],
        now=NOW,
    )

    assert [item.object_id for item in radar.opportunities] == [
        "opp_strong",
        "opp_weak",
        "opp_terminal",
    ]
    top = radar.opportunities[0]
    assert top.opportunity_score > radar.opportunities[1].opportunity_score
    assert "high_fit" in top.reasons
    assert "high_urgency" in top.reasons
    assert "fresh_signal" in top.reasons
    assert radar.opportunities[-1].is_active is False


def test_commitment_tracker_puts_overdue_and_conflicted_commitment_first() -> None:
    overdue = commitment_record(
        "commit_overdue",
        summary="Send overdue demo",
        due_at=NOW - timedelta(days=1),
        evidence_count=4,
        conflict=True,
    )
    upcoming = commitment_record(
        "commit_upcoming",
        summary="Prepare proposal",
        due_at=NOW + timedelta(days=5),
        evidence_count=2,
    )
    terminal = commitment_record(
        "commit_done",
        summary="Already done",
        due_at=NOW - timedelta(days=2),
        status="done",
        evidence_count=5,
    )

    radar = build_context_radar(
        opportunity_records=[],
        commitment_records=[terminal, upcoming, overdue],
        now=NOW,
    )

    assert [item.object_id for item in radar.commitments] == [
        "commit_overdue",
        "commit_upcoming",
        "commit_done",
    ]
    first = radar.commitments[0]
    assert first.overdue is True
    assert first.conflict_count == 1
    assert "overdue" in first.reasons
    assert "has_conflict" in first.reasons
    assert first.attention_score > radar.commitments[1].attention_score
    assert radar.commitments[-1].attention_score == 0
    assert radar.commitments[-1].overdue is False


def test_no_due_date_is_visible_but_not_more_urgent_than_overdue() -> None:
    no_due = commitment_record(
        "commit_no_due",
        summary="Follow up without date",
        due_at=None,
        evidence_count=3,
    )
    overdue = commitment_record(
        "commit_overdue",
        summary="Overdue task",
        due_at=NOW - timedelta(hours=1),
        evidence_count=1,
    )

    radar = build_context_radar(
        opportunity_records=[],
        commitment_records=[no_due, overdue],
        now=NOW,
    )

    assert radar.commitments[0].object_id == "commit_overdue"
    assert radar.commitments[1].object_id == "commit_no_due"
    assert "no_due_date" in radar.commitments[1].reasons
