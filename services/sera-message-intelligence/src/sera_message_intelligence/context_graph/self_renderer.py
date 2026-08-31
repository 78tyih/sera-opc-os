from __future__ import annotations

from datetime import datetime

from .self_intelligence import SelfIntelligenceResult


def render_self_intelligence_markdown(
    result: SelfIntelligenceResult,
    *,
    window_start: datetime,
    window_end: datetime,
) -> str:
    lines = [
        "# Self Intelligence",
        "",
        f"Window: {window_start.isoformat()} → {window_end.isoformat()}",
        "",
        "> These are evidence-gated, time-bounded signals. They are not permanent personality facts. Level 4 requires explicit user confirmation.",
        "",
    ]

    if not result.signals:
        lines.append("No validated self-intelligence signals were produced for this window.")
    else:
        for signal in sorted(
            result.signals,
            key=lambda item: (-item.evidence_level, -item.confidence, item.signal_type, item.id),
        ):
            lines.extend(
                [
                    f"## {signal.signal_type.replace('_', ' ').title()}",
                    "",
                    signal.statement,
                    "",
                    f"- Evidence level: L{signal.evidence_level}",
                    f"- Status: {signal.status}",
                    f"- Confidence: {signal.confidence:.2f}",
                    f"- Source diversity: {signal.source_diversity}",
                    "- Supporting graph changes: "
                    + (", ".join(str(item) for item in signal.supporting_change_ids) or "None"),
                    "- Contradicting graph changes: "
                    + (", ".join(str(item) for item in signal.contradicting_change_ids) or "None"),
                    "",
                ]
            )

    if result.rejected_candidates:
        lines.extend(["## Rejected candidates", ""])
        for item in result.rejected_candidates:
            lines.append(f"- {item}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"
