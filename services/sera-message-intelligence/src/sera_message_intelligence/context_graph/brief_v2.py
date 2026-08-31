from __future__ import annotations

import html
from datetime import date, datetime, timezone

from pydantic import BaseModel, Field

from sera_message_intelligence.models import ContextGraphChange, ContextGraphObject

from .change_feed import WorldChangeBrief, build_world_change_brief
from .people_radar import (
    PeopleRelationshipRadar,
    PersonRadarItem,
    RelationshipRadarItem,
    build_people_relationship_radar,
)
from .radar import (
    CommitmentRadarItem,
    ContextRadar,
    OpportunityRadarItem,
    build_context_radar,
)
from .schemas import SelfSignal


class SelfInsightItem(BaseModel):
    object_id: str
    signal_type: str
    statement: str
    status: str
    evidence_level: int = Field(ge=0, le=4)
    confidence: float = Field(ge=0, le=1)
    source_diversity: int = Field(ge=1)
    window_start: datetime
    window_end: datetime
    user_confirmed: bool


class PersonalIntelligenceBriefV2(BaseModel):
    date: date
    generated_at: datetime
    window_start: datetime
    window_end: datetime
    executive_summary: str
    world_changes: WorldChangeBrief
    top_opportunities: list[OpportunityRadarItem] = Field(default_factory=list)
    commitments_need_attention: list[CommitmentRadarItem] = Field(default_factory=list)
    people_to_focus: list[PersonRadarItem] = Field(default_factory=list)
    relationships_to_watch: list[RelationshipRadarItem] = Field(default_factory=list)
    self_insights: list[SelfInsightItem] = Field(default_factory=list)


def _utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _self_insight_items(records: list[ContextGraphObject]) -> list[SelfInsightItem]:
    items: list[SelfInsightItem] = []
    for record in records:
        if record.object_type != "self_signal":
            continue
        signal = SelfSignal.model_validate(record.payload)
        if signal.status in {"rejected_by_user", "superseded"}:
            continue
        items.append(
            SelfInsightItem(
                object_id=record.object_id,
                signal_type=signal.signal_type,
                statement=signal.statement,
                status=signal.status,
                evidence_level=signal.evidence_level,
                confidence=signal.confidence,
                source_diversity=signal.source_diversity,
                window_start=signal.window_start,
                window_end=signal.window_end,
                user_confirmed=signal.status == "confirmed_by_user",
            )
        )
    items.sort(
        key=lambda item: (
            not item.user_confirmed,
            -item.evidence_level,
            -item.confidence,
            -_utc(item.window_end).timestamp(),
            item.object_id,
        )
    )
    return items


def _executive_summary(
    *,
    world: WorldChangeBrief,
    context: ContextRadar,
    people: PeopleRelationshipRadar,
    self_items: list[SelfInsightItem],
) -> str:
    active_opportunities = [item for item in context.opportunities if item.is_active]
    overdue = [item for item in context.commitments if item.is_active and item.overdue]
    due_soon = [
        item
        for item in context.commitments
        if item.is_active
        and not item.overdue
        and item.due_in_days is not None
        and item.due_in_days <= 3
    ]
    parts = [f"{world.total_changes} material context changes"]
    if world.new_opportunities:
        parts.append(f"{len(world.new_opportunities)} new opportunities")
    if active_opportunities:
        parts.append(f"{len(active_opportunities)} active opportunities")
    if overdue:
        parts.append(f"{len(overdue)} overdue commitments")
    elif due_soon:
        parts.append(f"{len(due_soon)} commitments due within 3 days")
    if people.people:
        parts.append(f"highest people attention: {people.people[0].display_name}")
    supported_self = [
        item for item in self_items if item.status in {"supported", "confirmed_by_user"}
    ]
    if supported_self:
        parts.append(f"{len(supported_self)} supported/confirmed self signals")
    return "Today: " + "; ".join(parts) + "."


def build_personal_intelligence_brief_v2(
    *,
    report_date: date,
    changes: list[ContextGraphChange],
    opportunity_records: list[ContextGraphObject],
    commitment_records: list[ContextGraphObject],
    person_records: list[ContextGraphObject],
    self_signal_records: list[ContextGraphObject],
    window_start: datetime,
    window_end: datetime,
    as_of: datetime | None = None,
    top_n: int = 5,
) -> PersonalIntelligenceBriefV2:
    current = _utc(as_of or datetime.now(timezone.utc))
    world = build_world_change_brief(
        changes=changes,
        window_start=window_start,
        window_end=window_end,
        as_of=current,
    )
    context = build_context_radar(
        opportunity_records=opportunity_records,
        commitment_records=commitment_records,
        now=current,
    )
    people = build_people_relationship_radar(
        person_records=person_records,
        opportunity_records=opportunity_records,
        commitment_records=commitment_records,
        now=current,
    )
    self_items = _self_insight_items(self_signal_records)

    opportunities = [item for item in context.opportunities if item.is_active][:top_n]
    commitments = [item for item in context.commitments if item.is_active][:top_n]
    people_items = people.people[:top_n]
    relationships = people.relationships[:top_n]

    return PersonalIntelligenceBriefV2(
        date=report_date,
        generated_at=current,
        window_start=window_start,
        window_end=window_end,
        executive_summary=_executive_summary(
            world=world,
            context=context,
            people=people,
            self_items=self_items,
        ),
        world_changes=world,
        top_opportunities=opportunities,
        commitments_need_attention=commitments,
        people_to_focus=people_items,
        relationships_to_watch=relationships,
        self_insights=self_items[:top_n],
    )


def render_personal_intelligence_brief_v2_markdown(
    brief: PersonalIntelligenceBriefV2,
) -> str:
    lines = [
        f"# Personal Intelligence Brief V2 — {brief.date.isoformat()}",
        "",
        brief.executive_summary,
        "",
        "## What Changed Today",
        "",
    ]

    change_groups = [
        ("New opportunity", brief.world_changes.new_opportunities),
        ("Opportunity change", brief.world_changes.opportunity_changes),
        ("Commitment change", brief.world_changes.commitment_changes),
        ("People change", brief.world_changes.people_changes),
        ("Self change", brief.world_changes.self_changes),
    ]
    has_change = False
    for label, items in change_groups:
        for item in items[:5]:
            has_change = True
            lines.append(f"- **{label}: {item.title}** — {item.summary}")
    if not has_change:
        lines.append("- No material changes recorded in this window.")

    lines.extend(["", "## Opportunity Radar", ""])
    if not brief.top_opportunities:
        lines.append("- No active durable opportunities.")
    else:
        for item in brief.top_opportunities:
            next_action = "; ".join(item.next_actions) or "No next action recorded"
            lines.append(
                f"- **{item.title}** · {item.stage} · score {item.opportunity_score:.2f} · "
                f"probability {item.probability:.0%} — Next: {next_action}"
            )

    lines.extend(["", "## Commitments Needing Attention", ""])
    if not brief.commitments_need_attention:
        lines.append("- No active durable commitments.")
    else:
        for item in brief.commitments_need_attention:
            state = "OVERDUE" if item.overdue else (
                f"due in {item.due_in_days}d" if item.due_in_days is not None else "no due date"
            )
            lines.append(
                f"- **{item.summary}** · attention {item.attention_score:.2f} · {state}"
            )

    lines.extend(["", "## People to Focus", ""])
    if not brief.people_to_focus:
        lines.append("- No durable people context yet.")
    else:
        for item in brief.people_to_focus:
            lines.append(
                f"- **{item.display_name}** · attention {item.attention_score:.2f} · "
                f"opportunities {len(item.active_opportunity_ids)} · commitments {len(item.open_commitment_ids)}"
            )

    lines.extend(["", "## Relationships to Watch", ""])
    if not brief.relationships_to_watch:
        lines.append("- No evidence-grounded relationship edges currently require attention.")
    else:
        for item in brief.relationships_to_watch:
            lines.append(
                f"- **{item.person_a_name} ↔ {item.person_b_name}** · attention {item.attention_score:.2f} · "
                f"{', '.join(item.contexts)}"
            )

    lines.extend(["", "## Self Intelligence", ""])
    if not brief.self_insights:
        lines.append("- No active SelfSignals yet.")
    else:
        for item in brief.self_insights:
            marker = "USER CONFIRMED" if item.user_confirmed else item.status.upper()
            lines.append(
                f"- **{item.signal_type.replace('_', ' ').title()} · L{item.evidence_level} · {marker}** — "
                f"{item.statement} (confidence {item.confidence:.2f})"
            )

    lines.extend(
        [
            "",
            "---",
            "This brief separates observed context, model inference and user-confirmed self-knowledge. "
            "Evidence remains available in the underlying graph/change records.",
            "",
        ]
    )
    return "\n".join(lines)


def render_personal_intelligence_brief_v2_html(
    brief: PersonalIntelligenceBriefV2,
) -> str:
    def esc(value: object) -> str:
        return html.escape(str(value))

    def cards(items: list[str]) -> str:
        if not items:
            return '<div class="empty">None</div>'
        return "".join(f'<div class="card">{item}</div>' for item in items)

    changes: list[str] = []
    for group in (
        brief.world_changes.new_opportunities,
        brief.world_changes.opportunity_changes,
        brief.world_changes.commitment_changes,
        brief.world_changes.people_changes,
        brief.world_changes.self_changes,
    ):
        for item in group[:5]:
            changes.append(f"<strong>{esc(item.title)}</strong><br>{esc(item.summary)}")

    opportunities = [
        f"<strong>{esc(item.title)}</strong><br>{esc(item.stage)} · score {item.opportunity_score:.2f} · "
        f"probability {item.probability:.0%}<br><span>{esc('; '.join(item.next_actions) or 'No next action')}</span>"
        for item in brief.top_opportunities
    ]
    commitments = [
        f"<strong>{esc(item.summary)}</strong><br>attention {item.attention_score:.2f} · "
        + ("OVERDUE" if item.overdue else (f"due in {item.due_in_days}d" if item.due_in_days is not None else "no due date"))
        for item in brief.commitments_need_attention
    ]
    people = [
        f"<strong>{esc(item.display_name)}</strong><br>attention {item.attention_score:.2f} · "
        f"{len(item.active_opportunity_ids)} opportunities · {len(item.open_commitment_ids)} commitments"
        for item in brief.people_to_focus
    ]
    self_items = [
        f"<strong>{esc(item.signal_type.replace('_', ' ').title())} · L{item.evidence_level}</strong><br>"
        f"{esc(item.statement)}<br><span>{esc(item.status)} · confidence {item.confidence:.2f}</span>"
        for item in brief.self_insights
    ]

    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Personal Intelligence Brief V2 — {esc(brief.date.isoformat())}</title>
<style>
body{{font-family:Inter,-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;margin:0;background:#f6f6f4;color:#191919}}
main{{max-width:980px;margin:auto;padding:48px 24px 80px}}h1{{font-size:34px;margin:0 0 12px}}h2{{margin-top:38px;font-size:20px}}
.summary{{font-size:18px;line-height:1.6;padding:20px;border:1px solid #ddd;border-radius:14px;background:white}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:12px}}
.card{{background:white;border:1px solid #e2e2df;border-radius:12px;padding:16px;line-height:1.5}}.card span{{color:#666;font-size:13px}}.empty{{color:#777}}
footer{{margin-top:48px;color:#777;font-size:13px;line-height:1.5}}
</style></head><body><main>
<h1>Personal Intelligence Brief V2</h1><div>{esc(brief.date.isoformat())}</div>
<div class="summary">{esc(brief.executive_summary)}</div>
<h2>What Changed Today</h2><div class="grid">{cards(changes)}</div>
<h2>Opportunity Radar</h2><div class="grid">{cards(opportunities)}</div>
<h2>Commitments</h2><div class="grid">{cards(commitments)}</div>
<h2>People to Focus</h2><div class="grid">{cards(people)}</div>
<h2>Self Intelligence</h2><div class="grid">{cards(self_items)}</div>
<footer>Observed context, model inference and user-confirmed self-knowledge remain separate. Evidence is retained in the underlying Personal Context Graph.</footer>
</main></body></html>"""
