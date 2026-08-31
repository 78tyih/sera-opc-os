from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from itertools import combinations

from pydantic import BaseModel, Field

from sera_message_intelligence.models import ContextGraphObject

from .radar import CommitmentRadarItem, OpportunityRadarItem, build_context_radar
from .schemas import Person


class PersonRadarItem(BaseModel):
    person_id: str
    display_name: str
    aliases: list[str] = Field(default_factory=list)
    organization: str | None = None
    roles: list[str] = Field(default_factory=list)
    last_interaction_at: datetime | None = None
    days_since_interaction: int | None = None
    evidence_count: int = Field(ge=0)
    recency_score: float = Field(ge=0, le=1)
    evidence_score: float = Field(ge=0, le=1)
    active_opportunity_ids: list[str] = Field(default_factory=list)
    open_commitment_ids: list[str] = Field(default_factory=list)
    overdue_commitment_ids: list[str] = Field(default_factory=list)
    opportunity_signal_score: float = Field(ge=0, le=1)
    commitment_attention_score: float = Field(ge=0, le=1)
    attention_score: float = Field(ge=0, le=1)
    reasons: list[str] = Field(default_factory=list)


class RelationshipRadarItem(BaseModel):
    person_a_id: str
    person_b_id: str
    person_a_name: str
    person_b_name: str
    contexts: list[str] = Field(default_factory=list)
    shared_opportunity_ids: list[str] = Field(default_factory=list)
    open_commitment_ids: list[str] = Field(default_factory=list)
    overdue_commitment_ids: list[str] = Field(default_factory=list)
    last_signal_at: datetime | None = None
    days_since_signal: int | None = None
    recency_score: float = Field(ge=0, le=1)
    opportunity_signal_score: float = Field(ge=0, le=1)
    commitment_attention_score: float = Field(ge=0, le=1)
    attention_score: float = Field(ge=0, le=1)
    reasons: list[str] = Field(default_factory=list)


class PeopleRelationshipRadar(BaseModel):
    generated_at: datetime
    people: list[PersonRadarItem] = Field(default_factory=list)
    relationships: list[RelationshipRadarItem] = Field(default_factory=list)


def _utc_now(now: datetime | None) -> datetime:
    value = now or datetime.now(timezone.utc)
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _days_since(value: datetime | None, now: datetime) -> int | None:
    if value is None:
        return None
    current = value if value.tzinfo is not None else value.replace(tzinfo=timezone.utc)
    return max(0, int((now - current.astimezone(timezone.utc)).total_seconds() // 86400))


def _relationship_recency(days_since: int | None) -> float:
    if days_since is None:
        return 0.0
    # Relationship context decays more slowly than an individual opportunity.
    return round(max(0.0, 1.0 - days_since / 60.0), 4)


def _people_evidence_score(evidence_count: int) -> float:
    # Interaction volume is intentionally low-weight and saturates quickly.
    return round(min(1.0, max(0, evidence_count) / 10.0), 4)


def _max_score(items: list[OpportunityRadarItem | CommitmentRadarItem], attr: str) -> float:
    if not items:
        return 0.0
    return max(float(getattr(item, attr)) for item in items)


def build_people_relationship_radar(
    *,
    person_records: list[ContextGraphObject],
    opportunity_records: list[ContextGraphObject],
    commitment_records: list[ContextGraphObject],
    now: datetime | None = None,
) -> PeopleRelationshipRadar:
    """Build factual people/relationship attention views without inferring intimacy.

    A relationship edge is created only when two people share an explicit durable
    opportunity or are linked by a commitment. Mere co-presence in a group chat
    is not treated as a relationship signal.
    """

    current = _utc_now(now)
    context_radar = build_context_radar(
        opportunity_records=opportunity_records,
        commitment_records=commitment_records,
        now=current,
    )
    opportunity_by_id = {item.object_id: item for item in context_radar.opportunities}
    commitment_by_id = {item.object_id: item for item in context_radar.commitments}

    people_models: dict[str, Person] = {}
    person_record_by_id: dict[str, ContextGraphObject] = {}
    for record in person_records:
        if record.object_type != "person":
            continue
        person = Person.model_validate(record.payload)
        people_models[person.id] = person
        person_record_by_id[person.id] = record

    opportunities_by_person: dict[str, list[OpportunityRadarItem]] = defaultdict(list)
    for item in context_radar.opportunities:
        if not item.is_active:
            continue
        for person_id in item.person_ids:
            opportunities_by_person[person_id].append(item)

    commitments_by_person: dict[str, list[CommitmentRadarItem]] = defaultdict(list)
    for item in context_radar.commitments:
        if not item.is_active:
            continue
        linked_people = {item.owner_person_id, *item.beneficiary_person_ids}
        for person_id in linked_people:
            commitments_by_person[person_id].append(item)

    people: list[PersonRadarItem] = []
    for person_id, person in people_models.items():
        record = person_record_by_id[person_id]
        days_since = _days_since(person.last_meaningful_interaction_at, current)
        recency = _relationship_recency(days_since)
        evidence = _people_evidence_score(record.evidence_count)
        active_opportunities = opportunities_by_person.get(person_id, [])
        open_commitments = commitments_by_person.get(person_id, [])
        opportunity_score = _max_score(active_opportunities, "opportunity_score")
        commitment_score = _max_score(open_commitments, "attention_score")
        attention = round(
            0.40 * opportunity_score
            + 0.30 * commitment_score
            + 0.20 * recency
            + 0.10 * evidence,
            4,
        )
        overdue_ids = [item.object_id for item in open_commitments if item.overdue]
        reasons: list[str] = []
        if active_opportunities:
            reasons.append("active_opportunity")
        if open_commitments:
            reasons.append("open_commitment")
        if overdue_ids:
            reasons.append("overdue_commitment")
        if days_since is not None and days_since <= 7:
            reasons.append("recent_interaction")
        if days_since is not None and days_since >= 60:
            reasons.append("stale_contact")
        if record.evidence_count >= 5:
            reasons.append("repeated_interaction")

        people.append(
            PersonRadarItem(
                person_id=person_id,
                display_name=person.display_name,
                aliases=person.aliases,
                organization=person.organization,
                roles=person.roles,
                last_interaction_at=person.last_meaningful_interaction_at,
                days_since_interaction=days_since,
                evidence_count=record.evidence_count,
                recency_score=recency,
                evidence_score=evidence,
                active_opportunity_ids=[item.object_id for item in active_opportunities],
                open_commitment_ids=[item.object_id for item in open_commitments],
                overdue_commitment_ids=overdue_ids,
                opportunity_signal_score=opportunity_score,
                commitment_attention_score=commitment_score,
                attention_score=attention,
                reasons=reasons,
            )
        )

    people.sort(
        key=lambda item: (
            -item.attention_score,
            item.days_since_interaction is None,
            item.days_since_interaction if item.days_since_interaction is not None else 10**9,
            item.person_id,
        )
    )

    pair_contexts: dict[tuple[str, str], set[str]] = defaultdict(set)
    pair_opportunities: dict[tuple[str, str], set[str]] = defaultdict(set)
    pair_commitments: dict[tuple[str, str], set[str]] = defaultdict(set)
    pair_overdue: dict[tuple[str, str], set[str]] = defaultdict(set)
    pair_last_signal: dict[tuple[str, str], datetime] = {}

    opportunity_record_by_id = {record.object_id: record for record in opportunity_records}
    commitment_record_by_id = {record.object_id: record for record in commitment_records}

    for item in context_radar.opportunities:
        if not item.is_active:
            continue
        known_people = sorted({person_id for person_id in item.person_ids if person_id in people_models})
        for person_a, person_b in combinations(known_people, 2):
            key = (person_a, person_b)
            pair_contexts[key].add("shared_opportunity")
            pair_opportunities[key].add(item.object_id)
            signal_at = opportunity_record_by_id[item.object_id].last_seen_at
            previous = pair_last_signal.get(key)
            if previous is None or signal_at > previous:
                pair_last_signal[key] = signal_at

    for item in context_radar.commitments:
        if not item.is_active or item.owner_person_id not in people_models:
            continue
        for beneficiary_id in sorted(set(item.beneficiary_person_ids)):
            if beneficiary_id not in people_models or beneficiary_id == item.owner_person_id:
                continue
            key = tuple(sorted((item.owner_person_id, beneficiary_id)))
            pair_contexts[key].add("commitment")
            pair_commitments[key].add(item.object_id)
            if item.overdue:
                pair_overdue[key].add(item.object_id)
            signal_at = commitment_record_by_id[item.object_id].last_seen_at
            previous = pair_last_signal.get(key)
            if previous is None or signal_at > previous:
                pair_last_signal[key] = signal_at

    relationships: list[RelationshipRadarItem] = []
    for key, contexts in pair_contexts.items():
        person_a, person_b = key
        opportunity_items = [opportunity_by_id[item_id] for item_id in pair_opportunities[key]]
        commitment_items = [commitment_by_id[item_id] for item_id in pair_commitments[key]]
        opportunity_score = _max_score(opportunity_items, "opportunity_score")
        commitment_score = _max_score(commitment_items, "attention_score")
        last_signal_at = pair_last_signal.get(key)
        days_since = _days_since(last_signal_at, current)
        recency = _relationship_recency(days_since)
        attention = round(
            0.45 * opportunity_score
            + 0.35 * commitment_score
            + 0.20 * recency,
            4,
        )
        reasons: list[str] = []
        if pair_opportunities[key]:
            reasons.append("shared_active_opportunity")
        if pair_commitments[key]:
            reasons.append("open_commitment_link")
        if pair_overdue[key]:
            reasons.append("overdue_commitment_link")
        if days_since is not None and days_since <= 7:
            reasons.append("recent_signal")

        relationships.append(
            RelationshipRadarItem(
                person_a_id=person_a,
                person_b_id=person_b,
                person_a_name=people_models[person_a].display_name,
                person_b_name=people_models[person_b].display_name,
                contexts=sorted(contexts),
                shared_opportunity_ids=sorted(pair_opportunities[key]),
                open_commitment_ids=sorted(pair_commitments[key]),
                overdue_commitment_ids=sorted(pair_overdue[key]),
                last_signal_at=last_signal_at,
                days_since_signal=days_since,
                recency_score=recency,
                opportunity_signal_score=opportunity_score,
                commitment_attention_score=commitment_score,
                attention_score=attention,
                reasons=reasons,
            )
        )

    relationships.sort(
        key=lambda item: (
            -item.attention_score,
            item.days_since_signal is None,
            item.days_since_signal if item.days_since_signal is not None else 10**9,
            item.person_a_id,
            item.person_b_id,
        )
    )

    return PeopleRelationshipRadar(
        generated_at=current,
        people=people,
        relationships=relationships,
    )


def render_people_radar_markdown(radar: PeopleRelationshipRadar) -> str:
    lines = [
        "# People / Relationship Radar",
        "",
        f"Generated: {radar.generated_at.isoformat()}",
        "",
        "## People Radar",
        "",
    ]
    if not radar.people:
        lines.append("No durable people yet.")
    else:
        for index, item in enumerate(radar.people, start=1):
            lines.extend(
                [
                    f"### {index}. {item.display_name}",
                    f"- Attention: {item.attention_score:.3f} | Last interaction: {item.last_interaction_at.isoformat() if item.last_interaction_at else '-'}",
                    f"- Active opportunities: {len(item.active_opportunity_ids)} | Open commitments: {len(item.open_commitment_ids)} | Overdue: {len(item.overdue_commitment_ids)}",
                    f"- Evidence: {item.evidence_count} | Reasons: {', '.join(item.reasons) or '-'}",
                    "",
                ]
            )

    lines.extend(["## Relationship Radar", ""])
    if not radar.relationships:
        lines.append("No evidence-grounded relationship edges yet.")
    else:
        for index, item in enumerate(radar.relationships, start=1):
            lines.extend(
                [
                    f"### {index}. {item.person_a_name} ↔ {item.person_b_name}",
                    f"- Attention: {item.attention_score:.3f} | Contexts: {', '.join(item.contexts)}",
                    f"- Shared opportunities: {len(item.shared_opportunity_ids)} | Open commitments: {len(item.open_commitment_ids)} | Overdue: {len(item.overdue_commitment_ids)}",
                    f"- Last signal: {item.last_signal_at.isoformat() if item.last_signal_at else '-'} | Reasons: {', '.join(item.reasons) or '-'}",
                    "",
                ]
            )
    return "\n".join(lines).rstrip() + "\n"
