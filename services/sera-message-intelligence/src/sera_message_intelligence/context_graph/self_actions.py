from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel
from sqlalchemy.orm import Session

from sera_message_intelligence.models import ContextGraphObject

from .change_history import append_graph_change
from .schemas import ContextEvidenceRef, ContextInference, SelfSignal


SelfSignalAction = Literal["confirm", "reject", "supersede"]


class SelfSignalDecisionResult(BaseModel):
    object_id: str
    action: SelfSignalAction
    previous_status: str
    new_status: str
    evidence_level: int
    decision_reference: str
    change_recorded: bool


def _load_self_signal(session: Session, object_id: str) -> tuple[ContextGraphObject, SelfSignal]:
    record = session.get(ContextGraphObject, object_id)
    if record is None:
        raise ValueError(f"SelfSignal not found: {object_id}")
    if record.object_type != "self_signal":
        raise ValueError(f"Object is not a SelfSignal: {object_id}")
    return record, SelfSignal.model_validate(record.payload)


def apply_self_signal_decision(
    session: Session,
    *,
    object_id: str,
    action: SelfSignalAction,
    decision_reference: str,
    note: str | None = None,
    occurred_at: datetime | None = None,
) -> SelfSignalDecisionResult:
    """Apply an explicit user decision to one durable SelfSignal.

    This function is intentionally separate from model synthesis. A model run never
    calls it automatically. `decision_reference` must identify the explicit user
    action that authorized this mutation.
    """

    if not decision_reference.strip():
        raise ValueError("decision_reference is required for a SelfSignal user decision")

    record, signal = _load_self_signal(session, object_id)
    before = signal.model_dump(mode="json")
    previous_status = signal.status
    now = occurred_at or datetime.now(timezone.utc)

    if action == "confirm":
        new_status = "confirmed_by_user"
        evidence_level = 4
        confidence = 1.0
        statement = "User explicitly confirmed this SelfSignal as durable self-knowledge."
    elif action == "reject":
        new_status = "rejected_by_user"
        evidence_level = signal.evidence_level
        confidence = signal.confidence
        statement = "User explicitly rejected this SelfSignal."
    else:
        new_status = "superseded"
        evidence_level = signal.evidence_level
        confidence = signal.confidence
        statement = "User explicitly superseded this SelfSignal with newer context."

    if note:
        statement += f" Note: {note.strip()}"

    decision_ref = ContextEvidenceRef(
        source_type="user_confirmation",
        source_id=decision_reference.strip(),
        occurred_at=now,
    )
    evidence_by_id = {ref.source_id: ref for ref in signal.evidence_refs}
    evidence_by_id[decision_ref.source_id] = decision_ref

    decision_inference = ContextInference(
        statement=statement,
        confidence=1.0,
        status=new_status,
        supporting_evidence_ids=[decision_ref.source_id],
        user_confirmation_ref=decision_ref.source_id if new_status == "confirmed_by_user" else None,
    )

    updated = signal.model_copy(
        update={
            "updated_at": now,
            "evidence_refs": list(evidence_by_id.values()),
            "inferences": [*signal.inferences, decision_inference],
            "status": new_status,
            "evidence_level": evidence_level,
            "confidence": confidence,
            "user_confirmation_ref": decision_ref.source_id,
        }
    )
    # Re-validate invariants after model_copy because model_copy itself does not rerun validators.
    updated = SelfSignal.model_validate(updated.model_dump(mode="python"))
    after = updated.model_dump(mode="json")

    batch_id = f"self_decision_{uuid.uuid4().hex}"
    change = append_graph_change(
        session,
        object_id=record.object_id,
        object_type="self_signal",
        before_payload=before,
        after_payload=after,
        effective_at=now,
        batch_id=batch_id,
    )

    record.payload = after
    record.evidence_count = len(updated.evidence_refs)
    # An explicit user decision is itself the newest meaningful observation for this signal.
    # Assign directly instead of comparing timezone-aware Python values with SQLite values,
    # which may be returned without tzinfo depending on the test/runtime dialect.
    record.last_seen_at = now
    record.updated_at = now
    session.commit()

    return SelfSignalDecisionResult(
        object_id=record.object_id,
        action=action,
        previous_status=previous_status,
        new_status=updated.status,
        evidence_level=updated.evidence_level,
        decision_reference=decision_ref.source_id,
        change_recorded=change is not None,
    )
