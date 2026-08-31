"""Export Skill portability probes and assessment snapshots for Git audit."""

from __future__ import annotations

import os
import re
import sqlite3

from .portability import assess_portability, init_portability_schema, list_portability_probes


def _safe_name(value: str) -> str:
    value = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip())
    return value[:180] or "unnamed"


def render_portability_markdown(proposal_id: str, probes: list[dict], assessment: dict) -> str:
    lines = [
        f"# Skill Portability Evaluation — {proposal_id}",
        "",
        "> Cross-model baseline/candidate evidence. This is an Evaluation Gate artifact, not a production release authorization.",
        "",
        "## Assessment",
        "",
        f"- decision: `{assessment.get('decision')}`",
        f"- recommended_portability: `{assessment.get('recommended_portability')}`",
        f"- reason: `{assessment.get('reason')}`",
        f"- average_delta: `{assessment.get('average_delta')}`",
        "",
        "## Model Summary",
        "",
    ]
    models = assessment.get("models") or {}
    if not models:
        lines.append("- No model evidence.")
    else:
        for model, stats in sorted(models.items()):
            lines.append(
                f"- **{model}** · probes={stats.get('probe_count')} · mean_delta={stats.get('mean_delta'):.4f} "
                f"· min={stats.get('min_delta'):.4f} · max={stats.get('max_delta'):.4f}"
            )
            if stats.get("model_family"):
                lines.append(f"  - family: `{stats['model_family']}`")

    lines.extend(["", "## Probe Evidence", ""])
    for probe in probes:
        lines.extend([
            f"### {probe.get('probe_id')}",
            "",
            f"- model: `{probe.get('model')}`",
            f"- model_family: `{probe.get('model_family')}`",
            f"- agent_shell: `{probe.get('agent_shell')}`",
            f"- environment: `{probe.get('environment')}`",
            f"- metric: `{probe.get('metric_name')}`",
            f"- baseline: `{probe.get('baseline_score')}`",
            f"- candidate: `{probe.get('candidate_score')}`",
            f"- delta: `{probe.get('delta')}`",
            f"- at: `{probe.get('at')}`",
            "",
        ])

    lines.extend([
        "## Governance",
        "",
        "- A single-model improvement cannot justify `universal` portability.",
        "- Material negative transfer blocks a universal claim.",
        "- Evaluation `accepted` still does not authorize production Skill release.",
        "- Release requires the separate Policy / Authority Gate and a rollback target.",
        "",
    ])
    return "\n".join(lines)


def export_portability_snapshot(conn: sqlite3.Connection, context_hub_root: str) -> dict:
    init_portability_schema(conn)
    root = os.path.abspath(context_hub_root)
    output_dir = os.path.join(root, "08_Wiki", "evaluations")
    os.makedirs(output_dir, exist_ok=True)

    proposal_rows = conn.execute(
        "SELECT DISTINCT proposal_id FROM skill_portability_probes ORDER BY proposal_id"
    ).fetchall()
    exported = []
    for row in proposal_rows:
        proposal_id = row["proposal_id"] if isinstance(row, sqlite3.Row) else row[0]
        probes = list_portability_probes(conn, proposal_id)
        assessment = assess_portability(conn, proposal_id)
        path = os.path.join(output_dir, _safe_name(proposal_id) + ".portability.md")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(render_portability_markdown(proposal_id, probes, assessment))
        exported.append(path)

    return {
        "portability_files_exported": len(exported),
        "portability_files": exported,
        "git_commit_performed": False,
    }
