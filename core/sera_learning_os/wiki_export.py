"""Materialize Learning OS runtime state into a SeraContextHub checkout.

Runtime SQLite is an operational materialization, not an unaudited second source of
truth. This exporter writes deterministic human-readable snapshots under 08_Wiki/.
It does not commit or push Git by itself.
"""

from __future__ import annotations

import json
import os
import re
import sqlite3
from typing import Any, Optional

from .daily_review import build_daily_review, render_daily_review_markdown
from .learning import get_pattern, list_patterns


def _decode(value: Any) -> dict:
    if isinstance(value, dict):
        return value
    if not value:
        return {}
    try:
        parsed = json.loads(value)
        return parsed if isinstance(parsed, dict) else {}
    except (TypeError, json.JSONDecodeError):
        return {}


def _safe_name(value: str) -> str:
    value = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip())
    return value[:180] or "unnamed"


def _yaml_scalar(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    return json.dumps(str(value), ensure_ascii=False)


def render_pattern_markdown(pattern: dict) -> str:
    body = _decode(pattern.get("body"))
    evidence = pattern.get("evidence") or []
    lines = [
        "---",
        f"pattern_id: {_yaml_scalar(pattern.get('pattern_id'))}",
        f"type: {_yaml_scalar(pattern.get('pattern_type'))}",
        f"status: {_yaml_scalar(pattern.get('status'))}",
        f"scope: {_yaml_scalar(pattern.get('scope'))}",
        f"confidence: {_yaml_scalar(pattern.get('confidence'))}",
        f"created_at: {_yaml_scalar(pattern.get('created_at'))}",
        f"updated_at: {_yaml_scalar(pattern.get('updated_at'))}",
        "generated_from_runtime: true",
        "---",
        "",
        f"# {pattern.get('title') or pattern.get('pattern_id')}",
        "",
        "> Runtime materialization snapshot. Durable history remains auditable through Git; do not delete rejected/obsolete knowledge merely because a Skill rolls back.",
        "",
        "## Basis",
        "",
        f"- basis_kind: `{body.get('basis_kind') or 'unknown'}`",
        f"- basis: {body.get('basis') or '—'}",
        f"- verification_blocked: `{bool(body.get('verification_blocked'))}`",
        f"- evidence_count: **{body.get('evidence_count', len(evidence))}**",
        f"- independent_context_count: **{body.get('independent_context_count', 0)}**",
        "",
    ]
    if body.get("root_cause"):
        lines.extend(["## Root Cause", "", str(body["root_cause"]), ""])
    if body.get("failure_mode"):
        lines.extend(["## Failure Mode", "", str(body["failure_mode"]), ""])
    if body.get("success_mechanism"):
        lines.extend(["## Success Mechanism", "", str(body["success_mechanism"]), ""])
    if body.get("recommended_action"):
        lines.extend(["## Recommended Action", "", str(body["recommended_action"]), ""])

    lines.extend(["## Portability Evidence", ""])
    lines.append(f"- Agents: {', '.join(body.get('source_agents', [])) or '—'}")
    lines.append(f"- Models: {', '.join(body.get('source_models', [])) or '—'}")
    lines.append(f"- Projects: {', '.join(body.get('projects', [])) or '—'}")
    lines.append("")

    lines.extend(["## Affected Skills", ""])
    affected = body.get("affected_skills") or []
    if not affected:
        lines.append("- None declared.")
    else:
        for skill in affected:
            if isinstance(skill, str):
                lines.append(f"- `{skill}`")
            else:
                details = [f"`{skill.get('path')}`"]
                if skill.get("baseline_version"):
                    details.append(f"baseline `{skill['baseline_version']}`")
                if skill.get("portability"):
                    details.append(f"portability `{skill['portability']}`")
                lines.append("- " + " · ".join(details))
    lines.append("")

    lines.extend(["## Evidence", ""])
    if not evidence:
        lines.append("- No evidence rows exported.")
    else:
        for item in evidence:
            ref = item.get("evidence_ref") if isinstance(item, dict) else str(item)
            kind = item.get("kind", "trace") if isinstance(item, dict) else "trace"
            at = item.get("at") if isinstance(item, dict) else None
            suffix = f" · {at}" if at else ""
            lines.append(f"- `{ref}` · {kind}{suffix}")
    lines.append("")

    lines.extend([
        "## Governance",
        "",
        "- This Pattern is knowledge, not an executable instruction by itself.",
        "- `verified` means the evidence threshold was met; it does not authorize a production Skill write.",
        "- Contradictory evidence should move the Pattern to `contested`, not delete its history.",
        "",
    ])
    return "\n".join(lines)


def _proposal_rows(conn: sqlite3.Connection) -> list[dict]:
    cursor = conn.execute("SELECT * FROM skill_evolution_proposals ORDER BY updated_at DESC")
    columns = [d[0] for d in cursor.description]
    out = []
    for row in cursor.fetchall():
        item = dict(row) if isinstance(row, sqlite3.Row) else dict(zip(columns, row))
        item["body"] = _decode(item.get("body"))
        eval_cursor = conn.execute(
            "SELECT * FROM skill_evaluations WHERE proposal_id=? ORDER BY at ASC", (item["proposal_id"],)
        )
        eval_columns = [d[0] for d in eval_cursor.description]
        item["evaluations"] = [
            dict(r) if isinstance(r, sqlite3.Row) else dict(zip(eval_columns, r)) for r in eval_cursor.fetchall()
        ]
        out.append(item)
    return out


def render_proposal_markdown(proposal: dict) -> str:
    body = _decode(proposal.get("body"))
    lines = [
        "---",
        f"proposal_id: {_yaml_scalar(proposal.get('proposal_id'))}",
        f"status: {_yaml_scalar(proposal.get('status'))}",
        f"skill_path: {_yaml_scalar(proposal.get('skill_path'))}",
        f"baseline_version: {_yaml_scalar(proposal.get('baseline_version'))}",
        f"candidate_version: {_yaml_scalar(proposal.get('candidate_version'))}",
        f"portability: {_yaml_scalar(proposal.get('portability'))}",
        "generated_from_runtime: true",
        "---",
        "",
        f"# Skill Evolution Proposal — {proposal.get('proposal_id')}",
        "",
        f"**Skill:** `{proposal.get('skill_path')}`  ",
        f"**Version:** `{proposal.get('baseline_version')}` → `{proposal.get('candidate_version')}`  ",
        f"**Status:** `{proposal.get('status')}`",
        "",
        "## Why",
        "",
        str(body.get("why") or "—"),
        "",
        "## Recommended Changes",
        "",
        str(body.get("recommended_changes") or "—"),
        "",
        "## Evidence",
        "",
        f"- Source Patterns: {', '.join(body.get('source_patterns', [])) or '—'}",
        f"- Evidence Count: {body.get('evidence_count', 0)}",
        f"- Independent Contexts: {body.get('independent_context_count', 0)}",
        f"- Observed Models: {', '.join(body.get('tested_models_observed', [])) or '—'}",
        f"- Observed Agents: {', '.join(body.get('tested_agents_observed', [])) or '—'}",
        "",
        "## Release Safety",
        "",
        f"- Rollback target: `{body.get('rollback_target') or proposal.get('baseline_version')}`",
        "- Production write allowed by this proposal: **false**",
        "- A separate Policy / Authority Gate must approve release.",
        "",
        "## Evaluations",
        "",
    ]
    evaluations = proposal.get("evaluations") or []
    if not evaluations:
        lines.append("- Not evaluated yet.")
    else:
        for item in evaluations:
            metrics = _decode(item.get("metrics"))
            lines.append(f"- **{item.get('decision')}** · `{item.get('eval_id')}` · {item.get('at')}")
            if item.get("notes"):
                lines.append(f"  - {item['notes']}")
            if metrics:
                lines.append(f"  - metrics: `{json.dumps(metrics, ensure_ascii=False, sort_keys=True)}`")
    lines.append("")
    return "\n".join(lines)


def export_context_hub_snapshot(
    conn: sqlite3.Connection,
    context_hub_root: str,
    day: Optional[str] = None,
) -> dict:
    """Export current Wiki/Skill evolution state to an existing Context Hub checkout."""
    root = os.path.abspath(context_hub_root)
    wiki_root = os.path.join(root, "08_Wiki")
    patterns_dir = os.path.join(wiki_root, "patterns")
    proposals_dir = os.path.join(wiki_root, "proposals")
    daily_dir = os.path.join(wiki_root, "daily")
    for path in (patterns_dir, proposals_dir, daily_dir):
        os.makedirs(path, exist_ok=True)

    pattern_files = []
    for summary in list_patterns(conn, limit=5000):
        pattern = get_pattern(conn, summary["pattern_id"])
        filename = _safe_name(pattern["pattern_id"]) + ".md"
        path = os.path.join(patterns_dir, filename)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(render_pattern_markdown(pattern))
        pattern_files.append(path)

    proposal_files = []
    for proposal in _proposal_rows(conn):
        filename = _safe_name(proposal["proposal_id"]) + ".md"
        path = os.path.join(proposals_dir, filename)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(render_proposal_markdown(proposal))
        proposal_files.append(path)

    review = build_daily_review(conn, day=day)
    daily_path = os.path.join(daily_dir, f"{review['day']}.md")
    with open(daily_path, "w", encoding="utf-8") as fh:
        fh.write(render_daily_review_markdown(review))

    return {
        "context_hub_root": root,
        "patterns_exported": len(pattern_files),
        "proposals_exported": len(proposal_files),
        "daily_review": daily_path,
        "git_commit_performed": False,
    }
