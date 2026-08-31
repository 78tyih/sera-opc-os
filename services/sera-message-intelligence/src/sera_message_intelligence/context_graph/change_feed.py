from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field

from sera_message_intelligence.models import ContextGraphChange


ChangeCategory = Literal[
    "new_opportunity",
    "opportunity_change",
    "commitment_change",
    "people_change",
    "event_change",
]


class WorldChangeItem(BaseModel):
    change_id: int
    object_id: str
    object_type: str
    category: ChangeCategory
    title: str
    summary: str
    effective_at: datetime
    priority_score: float = Field(ge=0, le=1)
    semantic_changes: list[str] = Field(default_factory=list)
    changed_fields: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)


class WorldChangeBrief(BaseModel):
    generated_at: datetime
    window_start: datetime
    window_end: datetime
    executive_summary: str
    new_opportunities: list[WorldChangeItem] = Field(default_factory=list)
    opportunity_changes: list[WorldChangeItem] = Field(default_factory=list)
    commitment_changes: list[WorldChangeItem] = Field(default_factory=list)
    people_changes: list[WorldChangeItem] = Field(default_factory=list)
    event_changes: list[WorldChangeItem] = Field(default_factory=list)

    @property
    def total_changes(self) -> int:
        return sum(
            len(items)
            for items in (
                self.new_opportunities,
                self.opportunity_changes,
                self.commitment_changes,
                self.people_changes,
                self.event_changes,
            )
        )


def _title(change: ContextGraphChange) -> str:
    payload = change.after_payload or {}
    if change.object_type == "person":
        return str(payload.get("display_name") or change.object_id)
    if change.object_type == "opportunity":
        return str(payload.get("title") or change.object_id)
    if change.object_type == "commitment":
        return str(payload.get("summary") or change.object_id)
    if change.object_type == "event":
        return str(payload.get("summary") or change.object_id)
    return change.object_id


def _value(payload: dict[str, Any] | None, key: str) -> Any:
    return payload.get(key) if payload else None


def _format_value(value: Any) -> str:
    if value is None:
        return "none"
    if isinstance(value, float):
        return f"{value:.0%}"
    return str(value)


def _category(change: ContextGraphChange) -> ChangeCategory:
    if change.object_type == "opportunity":
        if change.change_kind == "created":
            return "new_opportunity"
        return "opportunity_change"
    if change.object_type == "commitment":
        return "commitment_change"
    if change.object_type == "person":
        return "people_change"
    return "event_change"


def _summary(change: ContextGraphChange) -> str:
    before = change.before_payload or {}
    after = change.after_payload or {}
    title = _title(change)
    semantics = set(change.semantic_changes or [])

    if change.change_kind == "created":
        labels = {
            "opportunity": "New opportunity",
            "commitment": "New commitment",
            "person": "New person observed",
            "event": "New event",
        }
        return f"{labels.get(change.object_type, 'New context object')}: {title}."

    details: list[str] = []
    if "opportunity_stage_changed" in semantics:
        details.append(
            f"stage {_format_value(before.get('stage'))} → {_format_value(after.get('stage'))}"
        )
    if "opportunity_signal_changed" in semantics:
        for field in ("probability", "urgency", "fit"):
            if before.get(field) != after.get(field):
                details.append(
                    f"{field} {_format_value(before.get(field))} → {_format_value(after.get(field))}"
                )
    if "next_actions_changed" in semantics:
        details.append("next actions changed")
    if "commitment_status_changed" in semantics:
        details.append(
            f"status {_format_value(before.get('status'))} → {_format_value(after.get('status'))}"
        )
    if "commitment_deadline_changed" in semantics:
        details.append(
            f"deadline {_format_value(before.get('due_at'))} → {_format_value(after.get('due_at'))}"
        )
    if "conflict_added" in semantics:
        details.append("new conflicting evidence requires review")
    if "meaningful_interaction" in semantics:
        details.append("new meaningful interaction")
    if "person_context_changed" in semantics:
        details.append("person context changed")
    if "identity_label_changed" in semantics:
        details.append("identity label changed")
    if "new_evidence" in semantics and not details:
        details.append("new supporting evidence")

    if not details:
        details = [label.replace("_", " ") for label in change.semantic_changes]
    return f"{title}: " + "; ".join(details) + "."


def _due_pressure(payload: dict[str, Any], as_of: datetime) -> float:
    if payload.get("status") in {"done", "cancelled"}:
        return 0.0
    raw = payload.get("due_at")
    if not raw:
        return 0.25
    try:
        due = datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
    except ValueError:
        return 0.25
    if due.tzinfo is None:
        due = due.replace(tzinfo=timezone.utc)
    seconds = (due - as_of).total_seconds()
    if seconds < 0:
        return 1.0
    days = seconds / 86400
    if days <= 1:
        return 0.9
    if days <= 3:
        return 0.75
    if days <= 7:
        return 0.55
    return 0.3


def _priority(change: ContextGraphChange, as_of: datetime) -> float:
    after = change.after_payload or {}
    semantics = set(change.semantic_changes or [])
    evidence_strength = min(1.0, len(change.evidence_ids or []) / 3.0)

    if change.object_type == "opportunity":
        fit = float(after.get("fit") or 0.0)
        urgency = float(after.get("urgency") or 0.0)
        probability = float(after.get("probability") or 0.0)
        base = 0.30 * fit + 0.25 * urgency + 0.20 * probability + 0.10 * evidence_strength
        if change.change_kind == "created":
            base += 0.10
        if "opportunity_stage_changed" in semantics:
            base += 0.10
        if "opportunity_signal_changed" in semantics:
            base += 0.05
        return round(min(1.0, base), 4)

    if change.object_type == "commitment":
        pressure = _due_pressure(after, as_of)
        confidence = float(after.get("confidence") or 0.0)
        base = 0.45 * pressure + 0.25 * confidence + 0.15 * evidence_strength
        if "conflict_added" in semantics:
            base += 0.15
        elif "commitment_status_changed" in semantics or "commitment_deadline_changed" in semantics:
            base += 0.10
        return round(min(1.0, base), 4)

    if change.object_type == "person":
        base = 0.15 + 0.15 * evidence_strength
        if "meaningful_interaction" in semantics:
            base += 0.35
        if "person_context_changed" in semantics:
            base += 0.20
        if "identity_label_changed" in semantics:
            base += 0.05
        return round(min(1.0, base), 4)

    base = 0.35 + 0.20 * evidence_strength
    if change.change_kind == "created":
        base += 0.10
    return round(min(1.0, base), 4)


def _item(change: ContextGraphChange, as_of: datetime) -> WorldChangeItem:
    return WorldChangeItem(
        change_id=change.change_id,
        object_id=change.object_id,
        object_type=change.object_type,
        category=_category(change),
        title=_title(change),
        summary=_summary(change),
        effective_at=change.effective_at,
        priority_score=_priority(change, as_of),
        semantic_changes=list(change.semantic_changes or []),
        changed_fields=list(change.changed_fields or []),
        evidence_ids=list(change.evidence_ids or []),
    )


def build_world_change_brief(
    *,
    changes: list[ContextGraphChange],
    window_start: datetime,
    window_end: datetime,
    as_of: datetime | None = None,
) -> WorldChangeBrief:
    as_of = as_of or datetime.now(timezone.utc)
    buckets: dict[ChangeCategory, list[WorldChangeItem]] = {
        "new_opportunity": [],
        "opportunity_change": [],
        "commitment_change": [],
        "people_change": [],
        "event_change": [],
    }
    for change in changes:
        item = _item(change, as_of)
        buckets[item.category].append(item)

    for items in buckets.values():
        items.sort(key=lambda item: (-item.priority_score, item.effective_at, item.object_id))

    counts = {
        "new opportunities": len(buckets["new_opportunity"]),
        "opportunity updates": len(buckets["opportunity_change"]),
        "commitment changes": len(buckets["commitment_change"]),
        "people changes": len(buckets["people_change"]),
        "events": len(buckets["event_change"]),
    }
    material = [f"{count} {label}" for label, count in counts.items() if count]
    executive = (
        "No material Personal Context Graph changes were recorded in this window."
        if not material
        else "What changed: " + ", ".join(material) + "."
    )

    return WorldChangeBrief(
        generated_at=datetime.now(timezone.utc),
        window_start=window_start,
        window_end=window_end,
        executive_summary=executive,
        new_opportunities=buckets["new_opportunity"],
        opportunity_changes=buckets["opportunity_change"],
        commitment_changes=buckets["commitment_change"],
        people_changes=buckets["people_change"],
        event_changes=buckets["event_change"],
    )


def render_world_change_markdown(brief: WorldChangeBrief) -> str:
    lines = [
        "# Personal Intelligence Brief V2 — World Changes",
        "",
        brief.executive_summary,
        "",
    ]
    sections = [
        ("New Opportunities", brief.new_opportunities),
        ("Opportunity Changes", brief.opportunity_changes),
        ("Commitments", brief.commitment_changes),
        ("People / Relationships", brief.people_changes),
        ("Other Events", brief.event_changes),
    ]
    for heading, items in sections:
        lines.append(f"## {heading}")
        if not items:
            lines.append("- None")
        else:
            for item in items:
                lines.append(
                    f"- **{item.title}** · score {item.priority_score:.2f} — {item.summary}"
                )
                if item.evidence_ids:
                    lines.append("  - Evidence: " + ", ".join(item.evidence_ids))
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"
