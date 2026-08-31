from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sera_message_intelligence.context_graph.change_feed import (
    build_world_change_brief,
    render_world_change_markdown,
)
from sera_message_intelligence.models import ContextGraphChange


BASE = datetime(2026, 8, 31, 0, 0, tzinfo=timezone.utc)


def change(
    change_id: int,
    *,
    object_id: str,
    object_type: str,
    kind: str,
    semantics: list[str],
    before: dict | None,
    after: dict,
    minute: int,
    evidence_ids: list[str] | None = None,
) -> ContextGraphChange:
    return ContextGraphChange(
        change_id=change_id,
        object_id=object_id,
        object_type=object_type,
        change_kind=kind,
        changed_fields=[],
        semantic_changes=semantics,
        evidence_ids=evidence_ids or [],
        before_payload=before,
        after_payload=after,
        batch_id="batch-1",
        effective_at=BASE + timedelta(minutes=minute),
        recorded_at=BASE + timedelta(minutes=minute),
    )


def test_world_change_brief_groups_and_explains_material_changes() -> None:
    opportunity = change(
        1,
        object_id="opp-1",
        object_type="opportunity",
        kind="created",
        semantics=["object_created"],
        before=None,
        after={
            "title": "AI workflow partnership",
            "fit": 0.9,
            "urgency": 0.8,
            "probability": 0.7,
            "stage": "signal",
        },
        minute=1,
        evidence_ids=["message:1"],
    )
    commitment = change(
        2,
        object_id="commit-1",
        object_type="commitment",
        kind="updated",
        semantics=["new_evidence", "conflict_added"],
        before={"summary": "Send demo", "status": "open", "due_at": "2026-09-01T00:00:00Z"},
        after={"summary": "Send demo", "status": "open", "due_at": "2026-09-01T00:00:00Z", "confidence": 0.9},
        minute=2,
        evidence_ids=["message:2"],
    )
    person = change(
        3,
        object_id="person-1",
        object_type="person",
        kind="updated",
        semantics=["new_evidence", "meaningful_interaction"],
        before={"display_name": "Alice"},
        after={"display_name": "Alice"},
        minute=3,
        evidence_ids=["message:3"],
    )

    brief = build_world_change_brief(
        changes=[person, commitment, opportunity],
        window_start=BASE,
        window_end=BASE + timedelta(days=1),
        as_of=BASE + timedelta(hours=12),
    )

    assert brief.total_changes == 3
    assert brief.new_opportunities[0].title == "AI workflow partnership"
    assert "New opportunity" in brief.new_opportunities[0].summary
    assert "conflicting evidence" in brief.commitment_changes[0].summary
    assert "meaningful interaction" in brief.people_changes[0].summary
    assert "1 new opportunities" in brief.executive_summary
    markdown = render_world_change_markdown(brief)
    assert "# Personal Intelligence Brief V2 — World Changes" in markdown
    assert "AI workflow partnership" in markdown
    assert "Evidence: message:1" in markdown


def test_opportunity_stage_move_explains_before_and_after() -> None:
    item = change(
        4,
        object_id="opp-2",
        object_type="opportunity",
        kind="updated",
        semantics=["new_evidence", "opportunity_stage_changed", "opportunity_signal_changed"],
        before={
            "title": "Distribution deal",
            "stage": "qualified",
            "fit": 0.8,
            "urgency": 0.5,
            "probability": 0.4,
        },
        after={
            "title": "Distribution deal",
            "stage": "negotiating",
            "fit": 0.8,
            "urgency": 0.8,
            "probability": 0.7,
        },
        minute=10,
        evidence_ids=["message:10"],
    )

    brief = build_world_change_brief(
        changes=[item],
        window_start=BASE,
        window_end=BASE + timedelta(days=1),
        as_of=BASE + timedelta(hours=12),
    )

    summary = brief.opportunity_changes[0].summary
    assert "qualified → negotiating" in summary
    assert "probability 40% → 70%" in summary
    assert brief.opportunity_changes[0].priority_score > 0.5


def test_empty_window_returns_explicit_no_material_change_summary() -> None:
    brief = build_world_change_brief(
        changes=[],
        window_start=BASE,
        window_end=BASE + timedelta(days=1),
        as_of=BASE + timedelta(days=1),
    )
    assert brief.total_changes == 0
    assert "No material" in brief.executive_summary
