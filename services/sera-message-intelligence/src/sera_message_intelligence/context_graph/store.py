from __future__ import annotations

import hashlib
import re
import unicodedata
import uuid
from datetime import datetime, timezone
from typing import Literal, TypeAlias

from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from sera_message_intelligence.models import ContextGraphChange, ContextGraphObject

from .change_history import append_graph_change
from .extraction import ContextExtractionResult
from .schemas import (
    Commitment,
    ContextEvidenceRef,
    ContextEvent,
    ContextInference,
    Opportunity,
    Person,
)


PersistableObject: TypeAlias = Person | ContextEvent | Opportunity | Commitment
ObjectType = Literal["person", "event", "opportunity", "commitment"]


class GraphUpsertSummary(BaseModel):
    created: int = 0
    updated: int = 0
    changes_recorded: int = 0
    batch_id: str | None = None
    resolved_ids: dict[str, str] = Field(default_factory=dict)


def _normalized_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value).casefold().strip()
    return re.sub(r"[\W_]+", " ", normalized, flags=re.UNICODE).strip()


def _digest(*parts: str) -> str:
    raw = "|".join(parts)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:32]


def object_type_for(obj: PersistableObject) -> ObjectType:
    if isinstance(obj, Person):
        return "person"
    if isinstance(obj, ContextEvent):
        return "event"
    if isinstance(obj, Opportunity):
        return "opportunity"
    if isinstance(obj, Commitment):
        return "commitment"
    raise TypeError(f"unsupported graph object: {type(obj)!r}")


def canonical_key_for(obj: PersistableObject) -> str:
    """Build a deliberately conservative identity key.

    We merge only exact stable identities or exact normalized semantic signatures.
    This intentionally produces false negatives rather than false-positive merges.
    """

    if isinstance(obj, Person):
        return f"person:{_digest(obj.id)}"
    if isinstance(obj, ContextEvent):
        return f"event:{_digest(obj.id)}"
    if isinstance(obj, Opportunity):
        return "opportunity:" + _digest(
            obj.opportunity_type,
            _normalized_text(obj.title),
            *sorted(obj.person_ids),
        )
    if isinstance(obj, Commitment):
        return "commitment:" + _digest(
            obj.owner_person_id,
            *sorted(obj.beneficiary_person_ids),
            _normalized_text(obj.summary),
        )
    raise TypeError(f"unsupported graph object: {type(obj)!r}")


def _model_for_record(record: ContextGraphObject) -> PersistableObject:
    model_type = {
        "person": Person,
        "event": ContextEvent,
        "opportunity": Opportunity,
        "commitment": Commitment,
    }.get(record.object_type)
    if model_type is None:
        raise ValueError(f"unsupported stored graph object type: {record.object_type}")
    return model_type.model_validate(record.payload)


def _merge_evidence(
    existing: list[ContextEvidenceRef], incoming: list[ContextEvidenceRef]
) -> list[ContextEvidenceRef]:
    refs = {ref.source_id: ref for ref in existing}
    refs.update({ref.source_id: ref for ref in incoming})
    return sorted(
        refs.values(),
        key=lambda ref: (
            ref.occurred_at.isoformat() if ref.occurred_at else "",
            ref.source_id,
        ),
    )


def _merge_inferences(
    existing: list[ContextInference], incoming: list[ContextInference]
) -> list[ContextInference]:
    merged: dict[tuple[str, tuple[str, ...], str], ContextInference] = {}
    for inference in [*existing, *incoming]:
        key = (
            inference.statement,
            tuple(sorted(inference.supporting_evidence_ids)),
            inference.status,
        )
        previous = merged.get(key)
        if previous is None or inference.confidence > previous.confidence:
            merged[key] = inference
    return list(merged.values())


def _union(existing: list[str], incoming: list[str]) -> list[str]:
    return list(dict.fromkeys([*existing, *incoming]))


def _latest_datetime(*values: datetime | None) -> datetime | None:
    available = [value for value in values if value is not None]
    return max(available) if available else None


def _merge_person(existing: Person, incoming: Person) -> Person:
    existing_last = existing.last_meaningful_interaction_at
    incoming_last = incoming.last_meaningful_interaction_at
    use_incoming_name = incoming_last is not None and (
        existing_last is None or incoming_last >= existing_last
    )
    display_name = incoming.display_name if use_incoming_name else existing.display_name
    aliases = _union(existing.aliases, incoming.aliases)
    for name in (existing.display_name, incoming.display_name):
        if name != display_name and name not in aliases:
            aliases.append(name)

    identities = {key: list(values) for key, values in existing.identities.items()}
    for platform, values in incoming.identities.items():
        identities[platform] = _union(identities.get(platform, []), values)

    return existing.model_copy(
        update={
            "created_at": min(existing.created_at, incoming.created_at),
            "updated_at": max(existing.updated_at, incoming.updated_at),
            "evidence_refs": _merge_evidence(existing.evidence_refs, incoming.evidence_refs),
            "observations": _union(existing.observations, incoming.observations),
            "inferences": _merge_inferences(existing.inferences, incoming.inferences),
            "display_name": display_name,
            "aliases": aliases,
            "identities": identities,
            "relationship_ids": _union(existing.relationship_ids, incoming.relationship_ids),
            "opportunity_ids": _union(existing.opportunity_ids, incoming.opportunity_ids),
            "project_ids": _union(existing.project_ids, incoming.project_ids),
            "commitment_ids": _union(existing.commitment_ids, incoming.commitment_ids),
            "last_meaningful_interaction_at": _latest_datetime(existing_last, incoming_last),
            "confidence": max(existing.confidence, incoming.confidence),
        }
    )


def _merge_event(existing: ContextEvent, incoming: ContextEvent) -> ContextEvent:
    return existing.model_copy(
        update={
            "created_at": min(existing.created_at, incoming.created_at),
            "updated_at": max(existing.updated_at, incoming.updated_at),
            "evidence_refs": _merge_evidence(existing.evidence_refs, incoming.evidence_refs),
            "observations": _union(existing.observations, incoming.observations),
            "inferences": _merge_inferences(existing.inferences, incoming.inferences),
            "actor_person_ids": _union(existing.actor_person_ids, incoming.actor_person_ids),
            "related_object_ids": _union(existing.related_object_ids, incoming.related_object_ids),
            "observed_facts": _union(existing.observed_facts, incoming.observed_facts),
            "confidence": max(existing.confidence, incoming.confidence),
        }
    )


_STAGE_RANK = {
    "signal": 0,
    "qualified": 1,
    "exploring": 2,
    "negotiating": 3,
    "won": 4,
    "lost": 4,
    "parked": 4,
}


def _merge_opportunity(existing: Opportunity, incoming: Opportunity) -> Opportunity:
    incoming_is_newer = incoming.last_signal_at >= existing.last_signal_at
    stage = existing.stage
    if _STAGE_RANK[incoming.stage] > _STAGE_RANK[existing.stage]:
        stage = incoming.stage

    return existing.model_copy(
        update={
            "created_at": min(existing.created_at, incoming.created_at),
            "updated_at": max(existing.updated_at, incoming.updated_at),
            "evidence_refs": _merge_evidence(existing.evidence_refs, incoming.evidence_refs),
            "observations": _union(existing.observations, incoming.observations),
            "inferences": _merge_inferences(existing.inferences, incoming.inferences),
            "title": incoming.title if incoming_is_newer else existing.title,
            "stage": stage,
            "person_ids": _union(existing.person_ids, incoming.person_ids),
            "organization_ids": _union(existing.organization_ids, incoming.organization_ids),
            "project_ids": _union(existing.project_ids, incoming.project_ids),
            "problem": (incoming.problem or existing.problem) if incoming_is_newer else (existing.problem or incoming.problem),
            "proposed_value": (incoming.proposed_value or existing.proposed_value) if incoming_is_newer else (existing.proposed_value or incoming.proposed_value),
            "estimated_value": incoming.estimated_value if incoming_is_newer and incoming.estimated_value is not None else existing.estimated_value,
            "currency": incoming.currency if incoming_is_newer and incoming.currency else existing.currency,
            "urgency": incoming.urgency if incoming_is_newer else existing.urgency,
            "fit": incoming.fit if incoming_is_newer else existing.fit,
            "probability": incoming.probability if incoming_is_newer else existing.probability,
            "next_actions": _union(existing.next_actions, incoming.next_actions),
            "risk_ids": _union(existing.risk_ids, incoming.risk_ids),
            "first_seen_at": min(existing.first_seen_at, incoming.first_seen_at),
            "last_signal_at": max(existing.last_signal_at, incoming.last_signal_at),
        }
    )


def _merge_commitment(existing: Commitment, incoming: Commitment) -> Commitment:
    inferences = _merge_inferences(existing.inferences, incoming.inferences)
    due_at = existing.due_at or incoming.due_at
    if existing.due_at and incoming.due_at and existing.due_at != incoming.due_at:
        evidence_ids = [ref.source_id for ref in incoming.evidence_refs]
        conflict = ContextInference(
            statement=(
                "Conflicting commitment due dates observed: "
                f"{existing.due_at.isoformat()} vs {incoming.due_at.isoformat()}"
            ),
            confidence=incoming.confidence,
            status="hypothesis",
            supporting_evidence_ids=evidence_ids,
        )
        inferences = _merge_inferences(inferences, [conflict])

    status = existing.status
    if existing.status in {"unknown", "open"} and incoming.status not in {"unknown", "open"}:
        status = incoming.status

    return existing.model_copy(
        update={
            "created_at": min(existing.created_at, incoming.created_at),
            "updated_at": max(existing.updated_at, incoming.updated_at),
            "evidence_refs": _merge_evidence(existing.evidence_refs, incoming.evidence_refs),
            "observations": _union(existing.observations, incoming.observations),
            "inferences": inferences,
            "status": status,
            "due_at": due_at,
            "beneficiary_person_ids": _union(existing.beneficiary_person_ids, incoming.beneficiary_person_ids),
            "related_person_ids": _union(existing.related_person_ids, incoming.related_person_ids),
            "related_project_ids": _union(existing.related_project_ids, incoming.related_project_ids),
            "related_opportunity_ids": _union(existing.related_opportunity_ids, incoming.related_opportunity_ids),
            "confidence": max(existing.confidence, incoming.confidence),
        }
    )


def merge_graph_object(existing: PersistableObject, incoming: PersistableObject) -> PersistableObject:
    if type(existing) is not type(incoming):
        raise TypeError("cannot merge different graph object types")
    if isinstance(existing, Person) and isinstance(incoming, Person):
        return _merge_person(existing, incoming)
    if isinstance(existing, ContextEvent) and isinstance(incoming, ContextEvent):
        return _merge_event(existing, incoming)
    if isinstance(existing, Opportunity) and isinstance(incoming, Opportunity):
        return _merge_opportunity(existing, incoming)
    if isinstance(existing, Commitment) and isinstance(incoming, Commitment):
        return _merge_commitment(existing, incoming)
    raise TypeError(f"unsupported graph object: {type(existing)!r}")


def _object_bounds(obj: PersistableObject) -> tuple[datetime, datetime]:
    if isinstance(obj, ContextEvent):
        return obj.occurred_at, obj.occurred_at
    if isinstance(obj, Opportunity):
        return obj.first_seen_at, obj.last_signal_at
    evidence_times = [ref.occurred_at for ref in obj.evidence_refs if ref.occurred_at is not None]
    if evidence_times:
        return min(evidence_times), max(evidence_times)
    return obj.created_at, obj.updated_at


def upsert_graph_object(
    session: Session,
    obj: PersistableObject,
    *,
    batch_id: str | None = None,
) -> tuple[ContextGraphObject, bool]:
    object_type = object_type_for(obj)
    canonical_key = canonical_key_for(obj)
    record = session.scalar(
        select(ContextGraphObject).where(
            ContextGraphObject.object_type == object_type,
            ContextGraphObject.canonical_key == canonical_key,
        )
    )

    now = datetime.now(timezone.utc)
    if record is None:
        first_seen, last_seen = _object_bounds(obj)
        after_payload = obj.model_dump(mode="json")
        record = ContextGraphObject(
            object_id=obj.id,
            object_type=object_type,
            canonical_key=canonical_key,
            payload=after_payload,
            first_seen_at=first_seen,
            last_seen_at=last_seen,
            evidence_count=len(obj.evidence_refs),
            created_at=now,
            updated_at=now,
        )
        session.add(record)
        session.flush()
        append_graph_change(
            session,
            object_id=record.object_id,
            object_type=object_type,
            before_payload=None,
            after_payload=after_payload,
            effective_at=last_seen,
            batch_id=batch_id,
        )
        return record, True

    existing = _model_for_record(record)
    before_payload = existing.model_dump(mode="json")
    incoming = obj if obj.id == record.object_id else obj.model_copy(update={"id": record.object_id})
    merged = merge_graph_object(existing, incoming)
    after_payload = merged.model_dump(mode="json")
    first_seen, last_seen = _object_bounds(merged)

    change = append_graph_change(
        session,
        object_id=record.object_id,
        object_type=object_type,
        before_payload=before_payload,
        after_payload=after_payload,
        effective_at=last_seen,
        batch_id=batch_id,
    )
    if change is None:
        return record, False

    record.payload = after_payload
    record.first_seen_at = first_seen
    record.last_seen_at = last_seen
    record.evidence_count = len(merged.evidence_refs)
    record.updated_at = now
    session.flush()
    return record, False


def upsert_context_result(
    session: Session,
    extracted: ContextExtractionResult,
) -> GraphUpsertSummary:
    """Resolve conservative exact matches and persist one extraction result.

    Opportunity IDs are remapped before commitments are persisted so a commitment
    points at the durable opportunity object rather than a transient candidate ID.
    Every call receives a batch ID so one extraction run can later be reconstructed.
    """

    batch_id = f"ctx_{uuid.uuid4().hex}"
    summary = GraphUpsertSummary(batch_id=batch_id)

    for obj in [*extracted.persons, *extracted.events, *extracted.opportunities]:
        record, created = upsert_graph_object(session, obj, batch_id=batch_id)
        summary.resolved_ids[obj.id] = record.object_id
        if created:
            summary.created += 1
        else:
            summary.updated += 1

    for commitment in extracted.commitments:
        remapped_opportunities = [
            summary.resolved_ids.get(object_id, object_id)
            for object_id in commitment.related_opportunity_ids
        ]
        candidate = commitment.model_copy(
            update={"related_opportunity_ids": remapped_opportunities}
        )
        record, created = upsert_graph_object(session, candidate, batch_id=batch_id)
        summary.resolved_ids[commitment.id] = record.object_id
        if created:
            summary.created += 1
        else:
            summary.updated += 1

    summary.changes_recorded = int(
        session.scalar(
            select(func.count())
            .select_from(ContextGraphChange)
            .where(ContextGraphChange.batch_id == batch_id)
        )
        or 0
    )
    session.commit()
    return summary


def list_graph_objects(
    session: Session,
    object_type: ObjectType | None = None,
) -> list[ContextGraphObject]:
    stmt = select(ContextGraphObject)
    if object_type is not None:
        stmt = stmt.where(ContextGraphObject.object_type == object_type)
    stmt = stmt.order_by(ContextGraphObject.last_seen_at.desc(), ContextGraphObject.object_id.asc())
    return list(session.scalars(stmt).all())
