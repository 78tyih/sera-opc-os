from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from sqlalchemy import select
from sqlalchemy.orm import Session

from sera_message_intelligence.models import ContextGraphChange


ChangeObjectType = Literal["person", "event", "opportunity", "commitment"]

_IGNORED_PAYLOAD_FIELDS = {"created_at", "updated_at"}


def _evidence_ids(payload: dict[str, Any] | None) -> list[str]:
    if not payload:
        return []
    result: list[str] = []
    for ref in payload.get("evidence_refs", []):
        source_id = ref.get("source_id") if isinstance(ref, dict) else None
        if source_id:
            result.append(str(source_id))
    return result


def _conflict_statements(payload: dict[str, Any] | None) -> set[str]:
    if not payload:
        return set()
    result: set[str] = set()
    for inference in payload.get("inferences", []):
        if not isinstance(inference, dict):
            continue
        statement = str(inference.get("statement") or "")
        if statement.startswith("Conflicting commitment due dates observed"):
            result.add(statement)
    return result


def classify_payload_change(
    *,
    object_type: ChangeObjectType,
    before: dict[str, Any] | None,
    after: dict[str, Any],
) -> tuple[list[str], list[str], list[str]]:
    """Return changed fields, semantic change labels and newly-added evidence IDs.

    Metadata timestamps are ignored. The function is deterministic and deliberately
    conservative: if a rerun produces the same durable state, it returns no change.
    """

    if before is None:
        changed_fields = sorted(
            key for key in after if key not in _IGNORED_PAYLOAD_FIELDS
        )
        evidence_ids = _evidence_ids(after)
        return changed_fields, ["object_created"], evidence_ids

    keys = set(before) | set(after)
    changed_fields = sorted(
        key
        for key in keys
        if key not in _IGNORED_PAYLOAD_FIELDS and before.get(key) != after.get(key)
    )

    before_evidence = set(_evidence_ids(before))
    after_evidence = _evidence_ids(after)
    new_evidence = [item for item in after_evidence if item not in before_evidence]

    semantic: list[str] = []
    if new_evidence:
        semantic.append("new_evidence")

    if object_type == "person":
        if "display_name" in changed_fields or "aliases" in changed_fields:
            semantic.append("identity_label_changed")
        if "last_meaningful_interaction_at" in changed_fields:
            semantic.append("meaningful_interaction")
        if any(field in changed_fields for field in ("organization", "roles", "expertise", "interests")):
            semantic.append("person_context_changed")

    elif object_type == "opportunity":
        if "stage" in changed_fields:
            semantic.append("opportunity_stage_changed")
        if any(field in changed_fields for field in ("probability", "urgency", "fit")):
            semantic.append("opportunity_signal_changed")
        if "next_actions" in changed_fields:
            semantic.append("next_actions_changed")
        if any(
            field in changed_fields
            for field in (
                "problem",
                "proposed_value",
                "estimated_value",
                "currency",
                "person_ids",
                "organization_ids",
                "project_ids",
            )
        ):
            semantic.append("opportunity_context_changed")

    elif object_type == "commitment":
        if "status" in changed_fields:
            semantic.append("commitment_status_changed")
        if "due_at" in changed_fields:
            semantic.append("commitment_deadline_changed")
        if any(
            field in changed_fields
            for field in (
                "beneficiary_person_ids",
                "related_person_ids",
                "related_project_ids",
                "related_opportunity_ids",
            )
        ):
            semantic.append("commitment_context_changed")
        new_conflicts = _conflict_statements(after) - _conflict_statements(before)
        if new_conflicts:
            semantic.append("conflict_added")

    elif object_type == "event":
        if changed_fields:
            semantic.append("event_updated")

    # Changes only in inference/evidence containers are still meaningful when they
    # represent new support or a new conflict. Otherwise avoid noisy history rows.
    material_fields = [
        field
        for field in changed_fields
        if field not in {"evidence_refs", "inferences", "observations"}
    ]
    if not material_fields and not semantic:
        return [], [], []

    return changed_fields, list(dict.fromkeys(semantic)), new_evidence


def append_graph_change(
    session: Session,
    *,
    object_id: str,
    object_type: ChangeObjectType,
    before_payload: dict[str, Any] | None,
    after_payload: dict[str, Any],
    effective_at: datetime,
    batch_id: str | None = None,
) -> ContextGraphChange | None:
    changed_fields, semantic_changes, evidence_ids = classify_payload_change(
        object_type=object_type,
        before=before_payload,
        after=after_payload,
    )
    if before_payload is not None and not changed_fields and not semantic_changes:
        return None

    change = ContextGraphChange(
        object_id=object_id,
        object_type=object_type,
        change_kind="created" if before_payload is None else "updated",
        changed_fields=changed_fields,
        semantic_changes=semantic_changes,
        evidence_ids=evidence_ids,
        before_payload=before_payload,
        after_payload=after_payload,
        batch_id=batch_id,
        effective_at=effective_at,
        recorded_at=datetime.now(timezone.utc),
    )
    session.add(change)
    session.flush()
    return change


def list_graph_changes(
    session: Session,
    *,
    start: datetime | None = None,
    end: datetime | None = None,
    object_type: ChangeObjectType | None = None,
    batch_id: str | None = None,
) -> list[ContextGraphChange]:
    stmt = select(ContextGraphChange)
    if start is not None:
        stmt = stmt.where(ContextGraphChange.effective_at >= start)
    if end is not None:
        stmt = stmt.where(ContextGraphChange.effective_at < end)
    if object_type is not None:
        stmt = stmt.where(ContextGraphChange.object_type == object_type)
    if batch_id is not None:
        stmt = stmt.where(ContextGraphChange.batch_id == batch_id)
    stmt = stmt.order_by(
        ContextGraphChange.effective_at.asc(),
        ContextGraphChange.change_id.asc(),
    )
    return list(session.scalars(stmt).all())
