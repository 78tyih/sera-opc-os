"""Daily Learning Review for Sera Learning OS."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from typing import Optional


def _date_prefix(day: Optional[str] = None) -> str:
    if day:
        return day
    return datetime.now(timezone.utc).date().isoformat()


def _decode(value):
    if not value:
        return {}
    if isinstance(value, dict):
        return value
    try:
        parsed = json.loads(value)
        return parsed if isinstance(parsed, dict) else {}
    except (TypeError, json.JSONDecodeError):
        return {}


def build_daily_review(conn: sqlite3.Connection, day: Optional[str] = None) -> dict:
    """Return a structured daily learning review for one UTC date."""
    prefix = _date_prefix(day)
    raw_rows = conn.execute(
        "SELECT outcome, COUNT(*) AS n FROM learning_raw_signals WHERE at LIKE ? GROUP BY outcome",
        (f"{prefix}%",),
    ).fetchall()
    outcomes = {row[0]: row[1] for row in raw_rows}

    event_rows = conn.execute(
        "SELECT event_type, COUNT(*) AS n FROM learning_events WHERE at LIKE ? GROUP BY event_type",
        (f"{prefix}%",),
    ).fetchall()
    events = {row[0]: row[1] for row in event_rows}

    patterns = []
    for row in conn.execute(
        "SELECT * FROM wiki_patterns WHERE updated_at LIKE ? ORDER BY updated_at DESC",
        (f"{prefix}%",),
    ).fetchall():
        item = dict(row) if isinstance(row, sqlite3.Row) else {
            "pattern_id": row[0], "title": row[1], "pattern_type": row[2], "status": row[3],
            "scope": row[4], "confidence": row[5], "body": row[6], "created_at": row[7], "updated_at": row[8]
        }
        item["body"] = _decode(item.get("body"))
        patterns.append(item)

    proposals = []
    for row in conn.execute(
        "SELECT * FROM skill_evolution_proposals WHERE created_at LIKE ? OR updated_at LIKE ? ORDER BY updated_at DESC",
        (f"{prefix}%", f"{prefix}%"),
    ).fetchall():
        item = dict(row) if isinstance(row, sqlite3.Row) else {
            "proposal_id": row[0], "skill_path": row[1], "baseline_version": row[2],
            "candidate_version": row[3], "status": row[4], "portability": row[5], "body": row[6],
            "created_at": row[7], "updated_at": row[8]
        }
        item["body"] = _decode(item.get("body"))
        proposals.append(item)

    evaluations = []
    for row in conn.execute(
        "SELECT * FROM skill_evaluations WHERE at LIKE ? ORDER BY at DESC",
        (f"{prefix}%",),
    ).fetchall():
        item = dict(row) if isinstance(row, sqlite3.Row) else {
            "eval_id": row[0], "proposal_id": row[1], "decision": row[2], "metrics": row[3],
            "notes": row[4], "actor": row[5], "at": row[6]
        }
        item["metrics"] = _decode(item.get("metrics"))
        evaluations.append(item)

    verified = [p for p in patterns if p.get("status") == "verified"]
    supported = [p for p in patterns if p.get("status") == "supported"]
    provisional = [p for p in patterns if p.get("status") == "provisional"]
    rejected = [e for e in evaluations if e.get("decision") == "rejected"]
    accepted = [e for e in evaluations if e.get("decision") == "accepted"]

    return {
        "day": prefix,
        "raw_signals": sum(outcomes.values()),
        "outcomes": outcomes,
        "events": events,
        "patterns_updated": len(patterns),
        "verified_patterns": len(verified),
        "supported_patterns": len(supported),
        "provisional_patterns": len(provisional),
        "skill_proposals_touched": len(proposals),
        "evaluations": len(evaluations),
        "accepted_evaluations": len(accepted),
        "rejected_evaluations": len(rejected),
        "patterns": patterns,
        "proposals": proposals,
        "evaluation_items": evaluations,
    }


def render_daily_review_markdown(review: dict) -> str:
    """Render a human-readable Daily Learning Review."""
    lines = [
        f"# Sera Daily Learning Review — {review['day']}",
        "",
        "> 这份报告回答：系统今天从执行中学到了什么，而不是今天做了什么。",
        "",
        "## Summary",
        "",
        f"- Raw learning signals: **{review['raw_signals']}**",
        f"- Patterns updated: **{review['patterns_updated']}**",
        f"- Verified patterns: **{review['verified_patterns']}**",
        f"- Supported patterns: **{review['supported_patterns']}**",
        f"- Skill proposals touched: **{review['skill_proposals_touched']}**",
        f"- Evaluations: **{review['evaluations']}** (accepted {review['accepted_evaluations']} / rejected {review['rejected_evaluations']})",
        "",
        "## Outcomes",
        "",
    ]
    if review.get("outcomes"):
        for key, value in sorted(review["outcomes"].items()):
            lines.append(f"- {key}: {value}")
    else:
        lines.append("- No learning signals recorded.")

    lines.extend(["", "## Patterns", ""])
    if not review.get("patterns"):
        lines.append("- No patterns changed today.")
    else:
        for pattern in review["patterns"]:
            body = pattern.get("body") or {}
            lines.append(
                f"- **{pattern['pattern_id']}** · {pattern['status']} · confidence={pattern['confidence']:.2f} — {pattern['title']}"
            )
            lines.append(
                f"  - evidence={body.get('evidence_count', 0)}, independent_contexts={body.get('independent_context_count', 0)}"
            )
            if body.get("recommended_action"):
                lines.append(f"  - next: {body['recommended_action']}")

    lines.extend(["", "## Skill Evolution", ""])
    if not review.get("proposals"):
        lines.append("- No Skill proposal changed today.")
    else:
        for proposal in review["proposals"]:
            lines.append(
                f"- **{proposal['proposal_id']}** · {proposal['status']} — `{proposal['skill_path']}` "
                f"{proposal['baseline_version']} → {proposal['candidate_version']}"
            )

    lines.extend(["", "## Evaluation Decisions", ""])
    if not review.get("evaluation_items"):
        lines.append("- No evaluation decision today.")
    else:
        for item in review["evaluation_items"]:
            lines.append(f"- **{item['decision']}** · {item['proposal_id']} — {item.get('notes') or 'no notes'}")

    lines.extend([
        "",
        "## Governance Reminder",
        "",
        "- Wiki knowledge is retained even when a Skill proposal is rejected.",
        "- Accepted evaluation does **not** directly modify a production Skill.",
        "- Production release still requires the Policy / Authority Gate and a rollback target.",
        "",
    ])
    return "\n".join(lines)
