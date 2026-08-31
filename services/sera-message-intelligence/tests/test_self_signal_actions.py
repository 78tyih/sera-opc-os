from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from sera_message_intelligence.context_graph.change_history import list_graph_changes
from sera_message_intelligence.context_graph.schemas import (
    ContextEvidenceRef,
    ContextInference,
    SelfSignal,
)
from sera_message_intelligence.context_graph.self_actions import apply_self_signal_decision
from sera_message_intelligence.context_graph.store import list_graph_objects, upsert_self_signals
from sera_message_intelligence.db import Base


BASE = datetime(2026, 8, 31, 0, 0, tzinfo=timezone.utc)


def engine():
    value = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(value)
    return value


def signal() -> SelfSignal:
    ref = ContextEvidenceRef(
        source_type="message",
        source_id="message:wechat:acct:1",
        platform="wechat",
        account_id="acct",
        conversation_id="group-a",
        message_id=1,
        occurred_at=BASE,
    )
    return SelfSignal(
        id="self_focus_week",
        created_at=BASE,
        updated_at=BASE,
        evidence_refs=[ref],
        observations=[],
        inferences=[
            ContextInference(
                statement="During this week, product building appears to have captured attention.",
                confidence=0.7,
                status="hypothesis",
                supporting_evidence_ids=[ref.source_id],
            )
        ],
        signal_type="attention",
        statement="During this week, product building appears to have captured attention.",
        window_start=BASE - timedelta(days=7),
        window_end=BASE,
        supporting_event_ids=[],
        contradicting_event_ids=[],
        supporting_change_ids=[1, 2],
        contradicting_change_ids=[],
        confidence=0.7,
        status="hypothesis",
        evidence_level=2,
        source_diversity=1,
        user_confirmation_ref=None,
    )


def test_confirm_requires_explicit_reference_and_promotes_to_level_four() -> None:
    db = engine()
    with Session(db) as session:
        upsert_self_signals(session, [signal()])
        with pytest.raises(ValueError, match="decision_reference"):
            apply_self_signal_decision(
                session,
                object_id="self_focus_week",
                action="confirm",
                decision_reference="",
            )

        result = apply_self_signal_decision(
            session,
            object_id="self_focus_week",
            action="confirm",
            decision_reference="user-decision:confirm:1",
            note="This reflects my current core focus.",
            occurred_at=BASE + timedelta(hours=1),
        )
        record = list_graph_objects(session, "self_signal")[0]
        changes = list_graph_changes(session, object_type="self_signal")

    assert result.previous_status == "hypothesis"
    assert result.new_status == "confirmed_by_user"
    assert result.evidence_level == 4
    assert record.payload["status"] == "confirmed_by_user"
    assert record.payload["confidence"] == 1.0
    assert record.payload["user_confirmation_ref"] == "user-decision:confirm:1"
    assert any(
        ref["source_type"] == "user_confirmation"
        and ref["source_id"] == "user-decision:confirm:1"
        for ref in record.payload["evidence_refs"]
    )
    latest = changes[-1]
    assert "self_signal_status_changed" in latest.semantic_changes
    assert "self_signal_evidence_strength_changed" in latest.semantic_changes
    assert "self_signal_user_confirmation_changed" in latest.semantic_changes


def test_reject_is_audited_and_does_not_promote_to_level_four() -> None:
    db = engine()
    with Session(db) as session:
        upsert_self_signals(session, [signal()])
        result = apply_self_signal_decision(
            session,
            object_id="self_focus_week",
            action="reject",
            decision_reference="user-decision:reject:1",
            occurred_at=BASE + timedelta(hours=1),
        )
        record = list_graph_objects(session, "self_signal")[0]

    assert result.new_status == "rejected_by_user"
    assert result.evidence_level == 2
    assert record.payload["status"] == "rejected_by_user"
    assert record.payload["evidence_level"] == 2
    assert record.payload["user_confirmation_ref"] == "user-decision:reject:1"


def test_explicit_user_action_can_reverse_prior_user_decision() -> None:
    db = engine()
    with Session(db) as session:
        upsert_self_signals(session, [signal()])
        apply_self_signal_decision(
            session,
            object_id="self_focus_week",
            action="reject",
            decision_reference="user-decision:reject:1",
            occurred_at=BASE + timedelta(hours=1),
        )
        result = apply_self_signal_decision(
            session,
            object_id="self_focus_week",
            action="confirm",
            decision_reference="user-decision:confirm:2",
            note="I reconsidered this after reviewing the evidence.",
            occurred_at=BASE + timedelta(hours=2),
        )
        record = list_graph_objects(session, "self_signal")[0]

    assert result.previous_status == "rejected_by_user"
    assert result.new_status == "confirmed_by_user"
    assert record.payload["status"] == "confirmed_by_user"
    assert record.payload["user_confirmation_ref"] == "user-decision:confirm:2"


def test_non_self_signal_object_is_rejected() -> None:
    db = engine()
    with Session(db) as session:
        with pytest.raises(ValueError, match="SelfSignal not found"):
            apply_self_signal_decision(
                session,
                object_id="missing",
                action="confirm",
                decision_reference="user-decision:confirm:missing",
            )
