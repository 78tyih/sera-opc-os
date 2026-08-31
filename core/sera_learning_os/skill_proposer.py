"""Governed Skill Proposer for Sera Learning OS.

Only verified Wiki patterns with sufficient independent evidence and explicit affected
Skill metadata are eligible. The proposer creates a proposal object; it never writes
production SKILL.md files.
"""

from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from typing import Any

from .learning import list_patterns, propose_skill_change


ELIGIBLE_PATTERN_STATUSES = {"verified"}
MIN_EVIDENCE = 3
MIN_CONTEXTS = 3


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


def _bump_patch(version: str) -> str:
    match = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)", str(version or ""))
    if not match:
        return "0.0.1-candidate"
    major, minor, patch = map(int, match.groups())
    return f"{major}.{minor}.{patch + 1}"


def _stable_suffix(value: str) -> str:
    return hashlib.sha1(value.encode("utf-8")).hexdigest()[:8]


def _proposal_exists(conn: sqlite3.Connection, pattern_id: str, skill_path: str) -> bool:
    rows = conn.execute("SELECT body,skill_path FROM skill_evolution_proposals").fetchall()
    for row in rows:
        path = row["skill_path"] if isinstance(row, sqlite3.Row) else row[1]
        body_raw = row["body"] if isinstance(row, sqlite3.Row) else row[0]
        body = _decode(body_raw)
        if path == skill_path and pattern_id in (body.get("source_patterns") or []):
            return True
    return False


def _eligible(pattern: dict) -> tuple[bool, str]:
    if pattern.get("status") not in ELIGIBLE_PATTERN_STATUSES:
        return False, "pattern_not_verified"
    body = _decode(pattern.get("body"))
    if body.get("verification_blocked"):
        return False, "verification_blocked"
    if int(body.get("evidence_count") or 0) < MIN_EVIDENCE:
        return False, "insufficient_evidence"
    if int(body.get("independent_context_count") or 0) < MIN_CONTEXTS:
        return False, "insufficient_independent_contexts"
    if not body.get("affected_skills"):
        return False, "no_affected_skill_metadata"
    if not body.get("recommended_action"):
        return False, "no_recommended_action"
    return True, "eligible"


def propose_from_pattern(
    conn: sqlite3.Connection,
    pattern: dict,
    actor: str = "skill-proposer",
) -> list[dict]:
    """Create governed Skill proposals from one eligible pattern."""
    ok, reason = _eligible(pattern)
    if not ok:
        return [{"pattern_id": pattern.get("pattern_id"), "status": "skipped", "reason": reason}]

    body = _decode(pattern.get("body"))
    outputs = []
    for skill in body.get("affected_skills", []):
        if isinstance(skill, str):
            skill = {"path": skill}
        if not isinstance(skill, dict) or not skill.get("path"):
            continue
        skill_path = str(skill["path"])
        if _proposal_exists(conn, pattern["pattern_id"], skill_path):
            outputs.append({
                "pattern_id": pattern["pattern_id"],
                "skill_path": skill_path,
                "status": "skipped",
                "reason": "proposal_already_exists",
            })
            continue

        baseline_version = str(skill.get("baseline_version") or "0.0.0")
        candidate_version = str(skill.get("candidate_version") or _bump_patch(baseline_version))
        portability = str(skill.get("portability") or "universal")
        proposal_id = f"SEP.auto.{pattern['pattern_id'].split('.')[-1]}.{_stable_suffix(skill_path)}"

        proposal = {
            "proposal_id": proposal_id,
            "skill_path": skill_path,
            "baseline_version": baseline_version,
            "candidate_version": candidate_version,
            "portability": portability,
            "status": "proposed",
            "source_patterns": [pattern["pattern_id"]],
            "why": body.get("basis") or pattern.get("title"),
            "recommended_changes": body.get("recommended_action"),
            "evidence_count": body.get("evidence_count"),
            "independent_context_count": body.get("independent_context_count"),
            "tested_models_observed": body.get("source_models", []),
            "tested_agents_observed": body.get("source_agents", []),
            "rollback_target": baseline_version,
            "production_write_allowed": False,
        }
        result = propose_skill_change(conn, proposal, actor=actor)
        result.update({"pattern_id": pattern["pattern_id"], "skill_path": skill_path})
        outputs.append(result)
    return outputs or [{"pattern_id": pattern["pattern_id"], "status": "skipped", "reason": "no_valid_skill_metadata"}]


def propose_ready_skills(conn: sqlite3.Connection, limit: int = 200) -> list[dict]:
    """Scan verified patterns and create proposals where policy gates are met."""
    patterns = list_patterns(conn, status="verified", limit=limit)
    outputs = []
    for pattern in patterns:
        outputs.extend(propose_from_pattern(conn, pattern))
    return outputs
