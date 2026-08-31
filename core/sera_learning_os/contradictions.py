"""Contradiction handling for Sera Learning OS.

Persistent Wiki knowledge must be able to learn that an earlier Pattern is no longer
reliable. Contradictory evidence is append-only; the Pattern materialized state may
move to `contested`, but prior supportive evidence is never deleted.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from typing import Optional

from .learning import get_pattern, init_learning_schema


MIN_CONTRADICTION_STRENGTH = 0.70
MIN_INDEPENDENT_CONTRADICTIONS = 2
EXPLICIT_CONTRADICTION_STRENGTH = 0.80


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def init_contradiction_schema(conn: sqlite3.Connection) -> sqlite3.Connection:
    init_learning_schema(conn)
    conn.executescript(
        """
CREATE TABLE IF NOT EXISTS wiki_pattern_contradictions(
    pattern_id TEXT NOT NULL,
    evidence_ref TEXT NOT NULL,
    reason TEXT NOT NULL,
    source_agent TEXT NOT NULL,
    source_model TEXT NOT NULL,
    task_context TEXT NOT NULL,
    strength REAL NOT NULL CHECK(strength BETWEEN 0 AND 1),
    explicit INTEGER NOT NULL DEFAULT 0 CHECK(explicit IN(0,1)),
    at TEXT NOT NULL,
    PRIMARY KEY(pattern_id,evidence_ref),
    FOREIGN KEY(pattern_id) REFERENCES wiki_patterns(pattern_id)
);
CREATE TRIGGER IF NOT EXISTS wiki_contradictions_no_update
BEFORE UPDATE ON wiki_pattern_contradictions
BEGIN SELECT RAISE(ABORT,'wiki_pattern_contradictions is append-only'); END;
CREATE TRIGGER IF NOT EXISTS wiki_contradictions_no_delete
BEFORE DELETE ON wiki_pattern_contradictions
BEGIN SELECT RAISE(ABORT,'wiki_pattern_contradictions is append-only'); END;
"""
    )
    conn.commit()
    return conn


def _rows_to_dicts(cursor) -> list[dict]:
    columns = [d[0] for d in cursor.description]
    rows = cursor.fetchall()
    return [dict(row) if isinstance(row, sqlite3.Row) else dict(zip(columns, row)) for row in rows]


def list_contradictions(conn: sqlite3.Connection, pattern_id: str) -> list[dict]:
    init_contradiction_schema(conn)
    cursor = conn.execute(
        "SELECT * FROM wiki_pattern_contradictions WHERE pattern_id=? ORDER BY at ASC",
        (pattern_id,),
    )
    return _rows_to_dicts(cursor)


def _should_contest(rows: list[dict]) -> tuple[bool, str]:
    explicit = [r for r in rows if bool(r.get("explicit")) and float(r.get("strength", 0)) >= EXPLICIT_CONTRADICTION_STRENGTH]
    if explicit:
        return True, "explicit_high_confidence_contradiction"

    strong = [r for r in rows if float(r.get("strength", 0)) >= MIN_CONTRADICTION_STRENGTH]
    independent = {str(r.get("task_context")) for r in strong if r.get("task_context")}
    if len(independent) >= MIN_INDEPENDENT_CONTRADICTIONS:
        return True, "repeated_independent_contradictions"
    return False, "insufficient_contradictory_evidence"


def record_pattern_contradiction(
    conn: sqlite3.Connection,
    *,
    pattern_id: str,
    evidence_ref: str,
    reason: str,
    source_agent: str,
    source_model: str,
    task_context: str,
    strength: float = 0.70,
    explicit: bool = False,
    actor: str = "wiki-maintainer",
    at: Optional[str] = None,
) -> dict:
    """Append contradictory evidence and, when warranted, mark a Pattern contested.

    `explicit=True` is intended for an evaluator/human/authority-backed contradiction,
    not ordinary model self-confidence. Production Skills are not modified here.
    """
    init_contradiction_schema(conn)
    pattern = get_pattern(conn, pattern_id)
    if pattern is None:
        return {"error": f"pattern not found: {pattern_id}"}
    if not evidence_ref or not reason or not source_agent or not source_model or not task_context:
        return {"error": "evidence_ref, reason, source_agent, source_model and task_context are required"}
    if not isinstance(strength, (int, float)) or not 0 <= float(strength) <= 1:
        return {"error": "strength must be in [0,1]"}

    timestamp = at or _now()
    try:
        conn.execute(
            """
            INSERT INTO wiki_pattern_contradictions(
                pattern_id,evidence_ref,reason,source_agent,source_model,task_context,strength,explicit,at
            ) VALUES(?,?,?,?,?,?,?,?,?)
            """,
            (
                pattern_id,
                evidence_ref,
                reason,
                source_agent,
                source_model,
                task_context,
                float(strength),
                1 if explicit else 0,
                timestamp,
            ),
        )
    except sqlite3.IntegrityError as exc:
        return {"error": str(exc)}

    rows = list_contradictions(conn, pattern_id)
    should_contest, trigger = _should_contest(rows)
    old_status = pattern.get("status")
    old_confidence = float(pattern.get("confidence") or 0.5)
    new_status = old_status
    new_confidence = old_confidence

    if should_contest and old_status != "superseded":
        new_status = "contested"
        # Contradiction lowers confidence in the materialized current claim, but never
        # destroys either supporting or contradictory evidence.
        new_confidence = max(0.20, round(old_confidence * 0.65, 4))
        conn.execute(
            "UPDATE wiki_patterns SET status=?,confidence=?,updated_at=? WHERE pattern_id=?",
            (new_status, new_confidence, timestamp, pattern_id),
        )

    event_payload = {
        "pattern_id": pattern_id,
        "evidence_ref": evidence_ref,
        "reason": reason,
        "strength": float(strength),
        "explicit": bool(explicit),
        "task_context": task_context,
        "old_status": old_status,
        "new_status": new_status,
        "old_confidence": old_confidence,
        "new_confidence": new_confidence,
        "trigger": trigger,
        "production_skill_modified": False,
    }
    conn.execute(
        "INSERT INTO learning_events(event_type,object_id,payload,actor,at) VALUES(?,?,?,?,?)",
        ("pattern_contradiction_recorded", pattern_id, json.dumps(event_payload, ensure_ascii=False), actor, timestamp),
    )
    conn.commit()

    return {
        "pattern_id": pattern_id,
        "contradictions": len(rows),
        "status": new_status,
        "confidence": new_confidence,
        "trigger": trigger,
        "production_skill_modified": False,
    }
