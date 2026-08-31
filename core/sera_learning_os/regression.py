"""Regression Harness + release-readiness gate for Sera Learning OS.

This module records append-only regression evidence for a Shadow Patch and computes a
release-readiness recommendation. It NEVER writes or releases production Skills.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
from collections import defaultdict
from datetime import datetime, timezone
from typing import Optional

from .learning import init_learning_schema
from .portability import assess_portability
from .shadow_patch import get_shadow_patch


REQUIRED_STATIC_CHECKS = {"frontmatter_valid", "required_sections_present", "no_secret_material", "no_private_cot"}
MIN_TASK_PROBES = 3
MAX_FAILURE_RATE = 0.0


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def init_regression_schema(conn: sqlite3.Connection) -> sqlite3.Connection:
    init_learning_schema(conn)
    conn.executescript(
        """
CREATE TABLE IF NOT EXISTS skill_regression_checks(
    check_id TEXT PRIMARY KEY,
    proposal_id TEXT NOT NULL,
    patch_id TEXT NOT NULL,
    check_type TEXT NOT NULL CHECK(check_type IN('static','task_probe')),
    check_name TEXT NOT NULL,
    model TEXT,
    passed INTEGER NOT NULL CHECK(passed IN(0,1)),
    score REAL,
    details TEXT NOT NULL DEFAULT '{}',
    at TEXT NOT NULL,
    FOREIGN KEY(proposal_id) REFERENCES skill_evolution_proposals(proposal_id),
    FOREIGN KEY(patch_id) REFERENCES skill_shadow_patches(patch_id)
);
CREATE TRIGGER IF NOT EXISTS regression_check_no_update BEFORE UPDATE ON skill_regression_checks
BEGIN SELECT RAISE(ABORT,'skill_regression_checks is append-only'); END;
CREATE TRIGGER IF NOT EXISTS regression_check_no_delete BEFORE DELETE ON skill_regression_checks
BEGIN SELECT RAISE(ABORT,'skill_regression_checks is append-only'); END;

CREATE TABLE IF NOT EXISTS skill_release_readiness(
    readiness_id TEXT PRIMARY KEY,
    proposal_id TEXT NOT NULL,
    patch_id TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN('blocked','needs_more_evidence','release_ready')),
    reason TEXT NOT NULL,
    evidence TEXT NOT NULL DEFAULT '{}',
    at TEXT NOT NULL,
    FOREIGN KEY(proposal_id) REFERENCES skill_evolution_proposals(proposal_id),
    FOREIGN KEY(patch_id) REFERENCES skill_shadow_patches(patch_id)
);
CREATE TRIGGER IF NOT EXISTS readiness_no_update BEFORE UPDATE ON skill_release_readiness
BEGIN SELECT RAISE(ABORT,'skill_release_readiness is append-only'); END;
CREATE TRIGGER IF NOT EXISTS readiness_no_delete BEFORE DELETE ON skill_release_readiness
BEGIN SELECT RAISE(ABORT,'skill_release_readiness is append-only'); END;
"""
    )
    conn.commit()
    return conn


def record_regression_check(
    conn: sqlite3.Connection,
    *,
    check_id: str,
    proposal_id: str,
    patch_id: str,
    check_type: str,
    check_name: str,
    passed: bool,
    score: Optional[float] = None,
    model: Optional[str] = None,
    details: Optional[dict] = None,
    at: Optional[str] = None,
    actor: str = "regression-harness",
) -> dict:
    init_regression_schema(conn)
    if check_type not in {"static", "task_probe"}:
        return {"error": f"invalid check_type: {check_type}"}
    patch = get_shadow_patch(conn, patch_id)
    if patch is None:
        return {"error": f"shadow patch not found: {patch_id}"}
    if patch["proposal_id"] != proposal_id:
        return {"error": "patch/proposal mismatch"}
    timestamp = at or _now()
    try:
        conn.execute(
            "INSERT INTO skill_regression_checks(check_id,proposal_id,patch_id,check_type,check_name,model,passed,score,details,at) VALUES(?,?,?,?,?,?,?,?,?,?)",
            (
                check_id, proposal_id, patch_id, check_type, check_name, model,
                1 if passed else 0, score, json.dumps(details or {}, ensure_ascii=False), timestamp,
            ),
        )
        conn.execute(
            "INSERT INTO learning_events(event_type,object_id,payload,actor,at) VALUES(?,?,?,?,?)",
            ("regression_check_recorded", patch_id, json.dumps({
                "check_id": check_id,
                "proposal_id": proposal_id,
                "check_type": check_type,
                "check_name": check_name,
                "model": model,
                "passed": bool(passed),
                "score": score,
            }, ensure_ascii=False), actor, timestamp),
        )
        conn.commit()
    except sqlite3.IntegrityError as exc:
        return {"error": str(exc)}
    return {"check_id": check_id, "status": "recorded", "passed": bool(passed)}


def list_regression_checks(conn: sqlite3.Connection, patch_id: str) -> list[dict]:
    init_regression_schema(conn)
    cursor = conn.execute("SELECT * FROM skill_regression_checks WHERE patch_id=? ORDER BY at", (patch_id,))
    cols = [d[0] for d in cursor.description]
    out = []
    for row in cursor.fetchall():
        item = dict(row) if isinstance(row, sqlite3.Row) else dict(zip(cols, row))
        item["passed"] = bool(item["passed"])
        try:
            item["details"] = json.loads(item.get("details") or "{}")
        except (TypeError, json.JSONDecodeError):
            item["details"] = {}
        out.append(item)
    return out


def assess_release_readiness(conn: sqlite3.Connection, proposal_id: str, patch_id: str) -> dict:
    """Compute readiness from Shadow Patch + regression + portability evidence."""
    patch = get_shadow_patch(conn, patch_id)
    if patch is None:
        return {"error": f"shadow patch not found: {patch_id}"}
    if patch["proposal_id"] != proposal_id:
        return {"error": "patch/proposal mismatch"}

    checks = list_regression_checks(conn, patch_id)
    static = {c["check_name"]: c for c in checks if c["check_type"] == "static"}
    missing_static = sorted(REQUIRED_STATIC_CHECKS - set(static))
    failed_static = sorted(name for name, check in static.items() if name in REQUIRED_STATIC_CHECKS and not check["passed"])
    task_probes = [c for c in checks if c["check_type"] == "task_probe"]
    failed_task_probes = [c for c in task_probes if not c["passed"]]
    portability = assess_portability(conn, proposal_id)

    evidence = {
        "required_static_checks": sorted(REQUIRED_STATIC_CHECKS),
        "missing_static_checks": missing_static,
        "failed_static_checks": failed_static,
        "task_probe_count": len(task_probes),
        "task_probe_failures": len(failed_task_probes),
        "portability": portability,
    }

    if failed_static or failed_task_probes:
        return {
            "proposal_id": proposal_id,
            "patch_id": patch_id,
            "status": "blocked",
            "reason": "regression_failure",
            "evidence": evidence,
            "production_skill_modified": False,
        }
    if missing_static or len(task_probes) < MIN_TASK_PROBES:
        return {
            "proposal_id": proposal_id,
            "patch_id": patch_id,
            "status": "needs_more_evidence",
            "reason": "regression_evidence_incomplete",
            "evidence": evidence,
            "production_skill_modified": False,
        }
    if portability.get("decision") not in {"accepted", "model_specific"}:
        return {
            "proposal_id": proposal_id,
            "patch_id": patch_id,
            "status": "needs_more_evidence" if portability.get("decision") == "insufficient_evidence" else "blocked",
            "reason": f"portability_{portability.get('decision')}",
            "evidence": evidence,
            "production_skill_modified": False,
        }

    return {
        "proposal_id": proposal_id,
        "patch_id": patch_id,
        "status": "release_ready",
        "reason": "regression_and_portability_gates_passed",
        "recommended_portability": portability.get("recommended_portability"),
        "evidence": evidence,
        "production_skill_modified": False,
    }


def record_release_readiness(conn: sqlite3.Connection, proposal_id: str, patch_id: str, actor: str = "release-readiness-gate") -> dict:
    """Append a readiness snapshot. release_ready is NOT a production release."""
    init_regression_schema(conn)
    assessment = assess_release_readiness(conn, proposal_id, patch_id)
    if assessment.get("error"):
        return assessment
    digest = hashlib.sha1(json.dumps(assessment, sort_keys=True, default=str).encode("utf-8")).hexdigest()[:12]
    readiness_id = f"READY.{digest}"
    timestamp = _now()
    try:
        conn.execute(
            "INSERT INTO skill_release_readiness(readiness_id,proposal_id,patch_id,status,reason,evidence,at) VALUES(?,?,?,?,?,?,?)",
            (
                readiness_id, proposal_id, patch_id, assessment["status"], assessment["reason"],
                json.dumps(assessment.get("evidence", {}), ensure_ascii=False), timestamp,
            ),
        )
        conn.execute(
            "INSERT INTO learning_events(event_type,object_id,payload,actor,at) VALUES(?,?,?,?,?)",
            ("release_readiness_assessed", patch_id, json.dumps({
                "readiness_id": readiness_id,
                "proposal_id": proposal_id,
                "status": assessment["status"],
                "reason": assessment["reason"],
            }, ensure_ascii=False), actor, timestamp),
        )
        conn.commit()
    except sqlite3.IntegrityError as exc:
        if "UNIQUE constraint failed" in str(exc):
            return {**assessment, "readiness_id": readiness_id, "recorded": False}
        return {"error": str(exc)}
    return {**assessment, "readiness_id": readiness_id, "recorded": True}
