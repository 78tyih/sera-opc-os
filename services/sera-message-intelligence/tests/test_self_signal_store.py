from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from sera_message_intelligence.context_graph.change_history import list_graph_changes
from sera_message_intelligence.context_graph.schemas import (
    ContextEvidenceRef,
    ContextInference,
    SelfSignal,
)
from sera_message_intelligence.context_graph.store import (
    list_graph_objects,
    upsert_self_signals,
)
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


def signal(
    *,
    status: str = "hypothesis",
    evidence_level: int = 2,
    confidence: float = 0.6,
    user_confirmation_ref: str | None = None,
    updated_at: datetime = BASE + timedelta(days=7),
) -> SelfSignal:
    ref = ContextEvidenceRef(
        source_type="message",
        source_id="message:wechat:acct:1",
        platform="wechat",
        account_id="acct",
        conversation_id="group-a",
        message_id=1,
        occurred_at=BASE + timedelta(days=1),
    )
    return SelfSignal(
        id="self_weekly_focus",
        created_at=BASE + timedelta(days=7),
        updated_at=updated_at,
        evidence_refs=[ref],
        observations=[],
        inferences=[
            ContextInference(
                statement="During this window, product building repeatedly captured attention.",
                confidence=confidence,
                status=status,
                supporting_evidence_ids=[ref.source_id],
                user_confirmation_ref=user_confirmation_ref,
            )
        ],
        signal_type="attention",
        statement="During this window, product building repeatedly captured attention.",
        window_start=BASE,
        window_end=BASE + timedelta(days=7),
        supporting_event_ids=[],
        contradicting_event_ids=[],
        supporting_change_ids=[1, 2],
        contradicting_change_ids=[],
        confidence=confidence,
        status=status,
        evidence_level=evidence_level,
        source_diversity=2,
        user_confirmation_ref=user_confirmation_ref,
    )


def test_self_signal_is_durable_and_identical_rerun_is_idempotent() -> None:
    db = engine()
    item = signal()

    with Session(db) as session:
        first = upsert_self_signals(session, [item])
        second = upsert_self_signals(session, [item])
        records = list_graph_objects(session, "self_signal")
        changes = list_graph_changes(session, object_type="self_signal")

    assert first.created == 1
    assert first.changes_recorded == 1
    assert second.created == 0
    assert second.changes_recorded == 0
    assert len(records) == 1
    assert len(changes) == 1
    assert changes[0].change_kind == "created"


def test_user_confirmation_promotes_signal_to_level_four_and_is_audited() -> None:
    db = engine()
    hypothesis = signal()
    confirmed = signal(
        status="confirmed_by_user",
        evidence_level=4,
        confidence=1.0,
        user_confirmation_ref="user-confirmation:2026-09-07:self_weekly_focus",
        updated_at=BASE + timedelta(days=8),
    )

    with Session(db) as session:
        upsert_self_signals(session, [hypothesis])
        summary = upsert_self_signals(session, [confirmed])
        records = list_graph_objects(session, "self_signal")
        changes = list_graph_changes(session, object_type="self_signal")

    assert summary.updated == 1
    assert summary.changes_recorded == 1
    payload = records[0].payload
    assert payload["status"] == "confirmed_by_user"
    assert payload["evidence_level"] == 4
    assert payload["user_confirmation_ref"] == "user-confirmation:2026-09-07:self_weekly_focus"
    latest = changes[-1]
    assert "self_signal_status_changed" in latest.semantic_changes
    assert "self_signal_evidence_strength_changed" in latest.semantic_changes
    assert "self_signal_user_confirmation_changed" in latest.semantic_changes


def test_later_model_hypothesis_cannot_downgrade_user_confirmed_signal() -> None:
    db = engine()
    confirmed = signal(
        status="confirmed_by_user",
        evidence_level=4,
        confidence=1.0,
        user_confirmation_ref="user-confirmation:1",
        updated_at=BASE + timedelta(days=8),
    )
    later_model = signal(
        status="supported",
        evidence_level=3,
        confidence=0.9,
        updated_at=BASE + timedelta(days=9),
    )

    with Session(db) as session:
        upsert_self_signals(session, [confirmed])
        summary = upsert_self_signals(session, [later_model])
        record = list_graph_objects(session, "self_signal")[0]

    assert summary.changes_recorded == 0
    assert record.payload["status"] == "confirmed_by_user"
    assert record.payload["evidence_level"] == 4
    assert record.payload["user_confirmation_ref"] == "user-confirmation:1"
