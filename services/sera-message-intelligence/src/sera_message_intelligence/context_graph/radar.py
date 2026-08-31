from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, Field

from sera_message_intelligence.models import ContextGraphObject

from .schemas import Commitment, Opportunity


ACTIVE_OPPORTUNITY_STAGES = {"signal", "qualified", "exploring", "negotiating"}
ACTIVE_COMMITMENT_STATUSES = {"open", "unknown", "overdue"}


class OpportunityRadarItem(BaseModel):
    object_id: str
    title: str
    opportunity_type: str
    stage: str
    is_active: bool
    person_ids: list[str] = Field(default_factory=list)
    project_ids: list[str] = Field(default_factory=list)
    first_seen_at: datetime
    last_signal_at: datetime
    days_since_signal: int = Field(ge=0)
    urgency: float = Field(ge=0, le=1)
    fit: float = Field(ge=0, le=1)
    probability: float = Field(ge=0, le=1)
    freshness_score: float = Field(ge=0, le=1)
    evidence_score: float = Field(ge=0, le=1)
    opportunity_score: float = Field(ge=0, le=1)
    evidence_count: int = Field(ge=0)
    next_actions: list[str] = Field(default_factory=list)
    reasons: list[str] = Field(default_factory=list)


class CommitmentRadarItem(BaseModel):
    object_id: str
    summary: str
    owner_person_id: str
    beneficiary_person_ids: list[str] = Field(default_factory=list)
    related_opportunity_ids: list[str] = Field(default_factory=list)
    status: str
    is_active: bool
    due_at: datetime | None = None
    due_in_days: int | None = None
    overdue: bool = False
    conflict_count: int = Field(ge=0)
    confidence: float = Field(ge=0, le=1)
    evidence_count: int = Field(ge=0)
    evidence_score: float = Field(ge=0, le=1)
    due_pressure_score: float = Field(ge=0, le=1)
    attention_score: float = Field(ge=0, le=1)
    reasons: list[str] = Field(default_factory=list)


class ContextRadar(BaseModel):
    generated_at: datetime
    opportunities: list[OpportunityRadarItem] = Field(default_factory=list)
    commitments: list[CommitmentRadarItem] = Field(default_factory=list)


def _utc_now(now: datetime | None) -> datetime:
    value = now or datetime.now(timezone.utc)
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _days_since(then: datetime, now: datetime) -> int:
    then_utc = then if then.tzinfo is not None else then.replace(tzinfo=timezone.utc)
    delta = now - then_utc.astimezone(timezone.utc)
    return max(0, int(delta.total_seconds() // 86400))


def _freshness_score(days_since: int) -> float:
    # Linear decay keeps the ranking easy to inspect and tune.
    return round(max(0.0, 1.0 - days_since / 30.0), 4)


def _evidence_score(evidence_count: int) -> float:
    # Five distinct evidence refs are enough to saturate the first-pass score.
    return round(min(1.0, max(0, evidence_count) / 5.0), 4)


def _opportunity_reasons(
    *,
    opportunity: Opportunity,
    days_since_signal: int,
    evidence_count: int,
) -> list[str]:
    reasons: list[str] = []
    if opportunity.fit >= 0.8:
        reasons.append("high_fit")
    if opportunity.urgency >= 0.8:
        reasons.append("high_urgency")
    if opportunity.probability >= 0.65:
        reasons.append("high_probability")
    if days_since_signal <= 3:
        reasons.append("fresh_signal")
    elif days_since_signal >= 30:
        reasons.append("stale_signal")
    if evidence_count >= 3:
        reasons.append("repeated_evidence")
    if opportunity.next_actions:
        reasons.append("has_next_action")
    if opportunity.stage in {"won", "lost", "parked"}:
        reasons.append(f"terminal_stage:{opportunity.stage}")
    return reasons


def opportunity_radar_item(
    record: ContextGraphObject,
    *,
    now: datetime | None = None,
) -> OpportunityRadarItem:
    if record.object_type != "opportunity":
        raise ValueError("opportunity_radar_item requires an opportunity record")
    current = _utc_now(now)
    opportunity = Opportunity.model_validate(record.payload)
    days_since_signal = _days_since(opportunity.last_signal_at, current)
    freshness = _freshness_score(days_since_signal)
    evidence = _evidence_score(record.evidence_count)
    score = round(
        0.30 * opportunity.fit
        + 0.25 * opportunity.urgency
        + 0.20 * opportunity.probability
        + 0.15 * freshness
        + 0.10 * evidence,
        4,
    )
    return OpportunityRadarItem(
        object_id=record.object_id,
        title=opportunity.title,
        opportunity_type=opportunity.opportunity_type,
        stage=opportunity.stage,
        is_active=opportunity.stage in ACTIVE_OPPORTUNITY_STAGES,
        person_ids=opportunity.person_ids,
        project_ids=opportunity.project_ids,
        first_seen_at=opportunity.first_seen_at,
        last_signal_at=opportunity.last_signal_at,
        days_since_signal=days_since_signal,
        urgency=opportunity.urgency,
        fit=opportunity.fit,
        probability=opportunity.probability,
        freshness_score=freshness,
        evidence_score=evidence,
        opportunity_score=score,
        evidence_count=record.evidence_count,
        next_actions=opportunity.next_actions,
        reasons=_opportunity_reasons(
            opportunity=opportunity,
            days_since_signal=days_since_signal,
            evidence_count=record.evidence_count,
        ),
    )


def _due_state(due_at: datetime | None, now: datetime) -> tuple[int | None, bool, float]:
    if due_at is None:
        return None, False, 0.30
    due = due_at if due_at.tzinfo is not None else due_at.replace(tzinfo=timezone.utc)
    seconds = (due.astimezone(timezone.utc) - now).total_seconds()
    due_in_days = int(seconds // 86400)
    if seconds < 0:
        return due_in_days, True, 1.0
    if seconds <= 86400:
        return due_in_days, False, 0.95
    if seconds <= 3 * 86400:
        return due_in_days, False, 0.85
    if seconds <= 7 * 86400:
        return due_in_days, False, 0.70
    if seconds <= 14 * 86400:
        return due_in_days, False, 0.50
    return due_in_days, False, 0.30


def _commitment_conflict_count(commitment: Commitment) -> int:
    return sum(
        1
        for inference in commitment.inferences
        if inference.statement.startswith("Conflicting commitment due dates observed")
        and inference.status not in {"rejected_by_user", "superseded"}
    )


def commitment_radar_item(
    record: ContextGraphObject,
    *,
    now: datetime | None = None,
) -> CommitmentRadarItem:
    if record.object_type != "commitment":
        raise ValueError("commitment_radar_item requires a commitment record")
    current = _utc_now(now)
    commitment = Commitment.model_validate(record.payload)
    is_active = commitment.status in ACTIVE_COMMITMENT_STATUSES
    due_in_days, overdue, due_pressure = _due_state(commitment.due_at, current)
    if not is_active:
        overdue = False
        due_pressure = 0.0
    evidence = _evidence_score(record.evidence_count)
    conflicts = _commitment_conflict_count(commitment)
    conflict_score = 1.0 if conflicts else 0.0
    attention = 0.0
    if is_active:
        attention = round(
            0.45 * due_pressure
            + 0.25 * commitment.confidence
            + 0.15 * evidence
            + 0.15 * conflict_score,
            4,
        )

    reasons: list[str] = []
    if overdue:
        reasons.append("overdue")
    elif due_in_days is not None and due_in_days <= 3:
        reasons.append("due_soon")
    if commitment.due_at is None and is_active:
        reasons.append("no_due_date")
    if conflicts:
        reasons.append("has_conflict")
    if record.evidence_count >= 3:
        reasons.append("repeated_evidence")
    if commitment.related_opportunity_ids:
        reasons.append("linked_opportunity")
    if not is_active:
        reasons.append(f"terminal_status:{commitment.status}")

    return CommitmentRadarItem(
        object_id=record.object_id,
        summary=commitment.summary,
        owner_person_id=commitment.owner_person_id,
        beneficiary_person_ids=commitment.beneficiary_person_ids,
        related_opportunity_ids=commitment.related_opportunity_ids,
        status=commitment.status,
        is_active=is_active,
        due_at=commitment.due_at,
        due_in_days=due_in_days,
        overdue=overdue,
        conflict_count=conflicts,
        confidence=commitment.confidence,
        evidence_count=record.evidence_count,
        evidence_score=evidence,
        due_pressure_score=due_pressure,
        attention_score=attention,
        reasons=reasons,
    )


def build_context_radar(
    *,
    opportunity_records: list[ContextGraphObject],
    commitment_records: list[ContextGraphObject],
    now: datetime | None = None,
) -> ContextRadar:
    current = _utc_now(now)
    opportunities = [
        opportunity_radar_item(record, now=current) for record in opportunity_records
    ]
    opportunities.sort(
        key=lambda item: (
            not item.is_active,
            -item.opportunity_score,
            item.days_since_signal,
            item.object_id,
        )
    )

    commitments = [
        commitment_radar_item(record, now=current) for record in commitment_records
    ]
    commitments.sort(
        key=lambda item: (
            not item.is_active,
            not item.overdue,
            -item.attention_score,
            item.due_at is None,
            item.due_at or datetime.max.replace(tzinfo=timezone.utc),
            item.object_id,
        )
    )

    return ContextRadar(
        generated_at=current,
        opportunities=opportunities,
        commitments=commitments,
    )


def render_context_radar_markdown(radar: ContextRadar) -> str:
    lines = [
        "# Personal Context Radar",
        "",
        f"Generated: {radar.generated_at.isoformat()}",
        "",
        "## Opportunity Radar",
        "",
    ]
    if not radar.opportunities:
        lines.append("No durable opportunities yet.")
    else:
        for index, item in enumerate(radar.opportunities, start=1):
            active = "active" if item.is_active else "archived"
            lines.extend(
                [
                    f"### {index}. {item.title}",
                    f"- Score: {item.opportunity_score:.3f} | Stage: {item.stage} | {active}",
                    f"- Fit: {item.fit:.2f} | Urgency: {item.urgency:.2f} | Probability: {item.probability:.2f}",
                    f"- Last signal: {item.last_signal_at.isoformat()} ({item.days_since_signal}d ago)",
                    f"- Evidence: {item.evidence_count} | Reasons: {', '.join(item.reasons) or '-'}",
                    f"- Next: {'; '.join(item.next_actions) or '-'}",
                    "",
                ]
            )

    lines.extend(["## Commitment Tracker", ""])
    if not radar.commitments:
        lines.append("No durable commitments yet.")
    else:
        for index, item in enumerate(radar.commitments, start=1):
            due = item.due_at.isoformat() if item.due_at else "not set"
            lines.extend(
                [
                    f"### {index}. {item.summary}",
                    f"- Attention: {item.attention_score:.3f} | Status: {item.status} | Overdue: {'yes' if item.overdue else 'no'}",
                    f"- Due: {due} | Due in days: {item.due_in_days if item.due_in_days is not None else '-'}",
                    f"- Owner: {item.owner_person_id} | Beneficiaries: {', '.join(item.beneficiary_person_ids) or '-'}",
                    f"- Evidence: {item.evidence_count} | Conflicts: {item.conflict_count} | Reasons: {', '.join(item.reasons) or '-'}",
                    "",
                ]
            )
    return "\n".join(lines).rstrip() + "\n"
