"""Sera Learning OS V0.

A minimal stdlib/sqlite runtime for the WikiSkill-inspired learning loop:
observable evidence -> persistent pattern -> skill proposal -> evaluation.

This module intentionally does NOT auto-edit production Skills. Promotion remains
behind the existing policy/authority gate.
"""

from __future__ import annotations

import json
import re
import sqlite3
from datetime import datetime, timezone
from typing import Any, Optional


PATTERN_TYPES = {
    "success_pattern",
    "failure_pattern",
    "anti_pattern",
    "heuristic",
    "model_behavior",
    "tool_behavior",
    "workflow_pattern",
}
PATTERN_STATUSES = {"provisional", "supported", "verified", "contested", "superseded"}
OUTCOMES = {"success", "failure", "partial", "cancelled"}
PROPOSAL_STATUSES = {
    "proposed",
    "evaluating",
    "accepted",
    "rejected",
    "revise",
    "model_specific",
    "insufficient_evidence",
}
EVAL_DECISIONS = {"accepted", "rejected", "revise", "model_specific", "insufficient_evidence"}
PORTABILITY = {
    "universal",
    "model_family",
    "model_specific",
    "agent_shell_specific",
    "tool_environment_specific",
}
PRIVATE_REASONING_KEYS = {
    "chain_of_thought",
    "chain-of-thought",
    "private_reasoning",
    "hidden_reasoning",
    "cot",
}
ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{2,127}$")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _event(conn: sqlite3.Connection, event_type: str, object_id: str, payload: dict, actor: str) -> None:
    conn.execute(
        "INSERT INTO learning_events(event_type,object_id,payload,actor,at) VALUES(?,?,?,?,?)",
        (event_type, object_id, json.dumps(payload, ensure_ascii=False, default=str), actor, _now()),
    )


def _valid_id(value: str) -> bool:
    return bool(value and ID_PATTERN.match(value))


def _contains_private_reasoning(value: Any) -> bool:
    """Reject payload fields that explicitly attempt to persist private CoT."""
    if isinstance(value, dict):
        for key, child in value.items():
            if str(key).strip().lower() in PRIVATE_REASONING_KEYS:
                return True
            if _contains_private_reasoning(child):
                return True
    elif isinstance(value, list):
        return any(_contains_private_reasoning(item) for item in value)
    return False


def _json(value: Any) -> str:
    return json.dumps(value if value is not None else {}, ensure_ascii=False, default=str)


def _decode(value: Optional[str]) -> Any:
    if not value:
        return {}
    try:
        return json.loads(value)
    except (TypeError, json.JSONDecodeError):
        return value


def init_learning_schema(conn: sqlite3.Connection) -> sqlite3.Connection:
    """Create Learning OS tables and append-only guards. Idempotent."""
    conn.executescript(
        """
CREATE TABLE IF NOT EXISTS learning_raw_signals(
    trace_id TEXT PRIMARY KEY,
    at TEXT NOT NULL,
    project TEXT NOT NULL,
    source_agent TEXT NOT NULL,
    source_model TEXT NOT NULL,
    run_id TEXT,
    outcome TEXT NOT NULL CHECK(outcome IN('success','failure','partial','cancelled')),
    payload TEXT NOT NULL DEFAULT '{}'
);
CREATE TRIGGER IF NOT EXISTS learning_raw_no_update BEFORE UPDATE ON learning_raw_signals
BEGIN SELECT RAISE(ABORT,'learning_raw_signals is append-only'); END;
CREATE TRIGGER IF NOT EXISTS learning_raw_no_delete BEFORE DELETE ON learning_raw_signals
BEGIN SELECT RAISE(ABORT,'learning_raw_signals is append-only'); END;

CREATE TABLE IF NOT EXISTS wiki_patterns(
    pattern_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    pattern_type TEXT NOT NULL CHECK(pattern_type IN(
        'success_pattern','failure_pattern','anti_pattern','heuristic',
        'model_behavior','tool_behavior','workflow_pattern')),
    status TEXT NOT NULL CHECK(status IN('provisional','supported','verified','contested','superseded')),
    scope TEXT NOT NULL,
    confidence REAL NOT NULL DEFAULT 0.5 CHECK(confidence BETWEEN 0 AND 1),
    body TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS wiki_pattern_evidence(
    pattern_id TEXT NOT NULL,
    evidence_ref TEXT NOT NULL,
    kind TEXT NOT NULL DEFAULT 'trace',
    at TEXT NOT NULL,
    PRIMARY KEY(pattern_id,evidence_ref),
    FOREIGN KEY(pattern_id) REFERENCES wiki_patterns(pattern_id)
);
CREATE TRIGGER IF NOT EXISTS wiki_evidence_no_update BEFORE UPDATE ON wiki_pattern_evidence
BEGIN SELECT RAISE(ABORT,'wiki_pattern_evidence is append-only'); END;
CREATE TRIGGER IF NOT EXISTS wiki_evidence_no_delete BEFORE DELETE ON wiki_pattern_evidence
BEGIN SELECT RAISE(ABORT,'wiki_pattern_evidence is append-only'); END;

CREATE TABLE IF NOT EXISTS skill_evolution_proposals(
    proposal_id TEXT PRIMARY KEY,
    skill_path TEXT NOT NULL,
    baseline_version TEXT NOT NULL,
    candidate_version TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN(
        'proposed','evaluating','accepted','rejected','revise','model_specific','insufficient_evidence')),
    portability TEXT NOT NULL CHECK(portability IN(
        'universal','model_family','model_specific','agent_shell_specific','tool_environment_specific')),
    body TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS skill_evaluations(
    eval_id TEXT PRIMARY KEY,
    proposal_id TEXT NOT NULL,
    decision TEXT NOT NULL CHECK(decision IN(
        'accepted','rejected','revise','model_specific','insufficient_evidence')),
    metrics TEXT NOT NULL DEFAULT '{}',
    notes TEXT NOT NULL DEFAULT '',
    actor TEXT NOT NULL,
    at TEXT NOT NULL,
    FOREIGN KEY(proposal_id) REFERENCES skill_evolution_proposals(proposal_id)
);
CREATE TRIGGER IF NOT EXISTS skill_eval_no_update BEFORE UPDATE ON skill_evaluations
BEGIN SELECT RAISE(ABORT,'skill_evaluations is append-only'); END;
CREATE TRIGGER IF NOT EXISTS skill_eval_no_delete BEFORE DELETE ON skill_evaluations
BEGIN SELECT RAISE(ABORT,'skill_evaluations is append-only'); END;

CREATE TABLE IF NOT EXISTS learning_events(
    seq INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT NOT NULL,
    object_id TEXT NOT NULL,
    payload TEXT NOT NULL,
    actor TEXT NOT NULL,
    at TEXT NOT NULL
);
CREATE TRIGGER IF NOT EXISTS learning_events_no_update BEFORE UPDATE ON learning_events
BEGIN SELECT RAISE(ABORT,'learning_events is append-only'); END;
CREATE TRIGGER IF NOT EXISTS learning_events_no_delete BEFORE DELETE ON learning_events
BEGIN SELECT RAISE(ABORT,'learning_events is append-only'); END;
"""
    )
    conn.commit()
    return conn


def record_raw_signal(conn: sqlite3.Connection, signal: dict, actor: str = "system") -> dict:
    """Append an observable learning signal.

    Required: trace_id, project, source_agent, source_model, outcome.
    Explicit private-CoT fields are rejected.
    """
    init_learning_schema(conn)
    required = ("trace_id", "project", "source_agent", "source_model", "outcome")
    missing = [field for field in required if not signal.get(field)]
    if missing:
        return {"error": f"missing required fields: {', '.join(missing)}"}
    if not _valid_id(str(signal["trace_id"])):
        return {"error": "invalid trace_id"}
    if signal["outcome"] not in OUTCOMES:
        return {"error": f"invalid outcome: {signal['outcome']}"}
    if _contains_private_reasoning(signal):
        return {"error": "private chain-of-thought/private reasoning must not be persisted"}

    payload = {
        key: value
        for key, value in signal.items()
        if key not in {"trace_id", "project", "source_agent", "source_model", "run_id", "outcome", "at"}
    }
    at = signal.get("at") or _now()
    try:
        conn.execute(
            "INSERT INTO learning_raw_signals(trace_id,at,project,source_agent,source_model,run_id,outcome,payload) "
            "VALUES(?,?,?,?,?,?,?,?)",
            (
                signal["trace_id"],
                at,
                signal["project"],
                signal["source_agent"],
                signal["source_model"],
                signal.get("run_id"),
                signal["outcome"],
                _json(payload),
            ),
        )
        _event(conn, "raw_signal_recorded", signal["trace_id"], signal, actor)
        conn.commit()
    except sqlite3.IntegrityError as exc:
        return {"error": str(exc)}
    return {"trace_id": signal["trace_id"], "status": "recorded"}


def upsert_pattern(conn: sqlite3.Connection, pattern: dict, actor: str = "wiki-maintainer") -> dict:
    """Create/update a persistent Wiki pattern while preserving event/evidence history."""
    init_learning_schema(conn)
    required = ("pattern_id", "title", "pattern_type", "status", "scope")
    missing = [field for field in required if not pattern.get(field)]
    if missing:
        return {"error": f"missing required fields: {', '.join(missing)}"}
    if not _valid_id(str(pattern["pattern_id"])):
        return {"error": "invalid pattern_id"}
    if pattern["pattern_type"] not in PATTERN_TYPES:
        return {"error": f"invalid pattern_type: {pattern['pattern_type']}"}
    if pattern["status"] not in PATTERN_STATUSES:
        return {"error": f"invalid pattern status: {pattern['status']}"}
    confidence = pattern.get("confidence", 0.5)
    if not isinstance(confidence, (int, float)) or not 0 <= confidence <= 1:
        return {"error": "confidence must be in [0,1]"}
    if _contains_private_reasoning(pattern):
        return {"error": "private chain-of-thought/private reasoning must not be persisted"}

    now = _now()
    existing = conn.execute(
        "SELECT pattern_id,body,status,confidence FROM wiki_patterns WHERE pattern_id=?",
        (pattern["pattern_id"],),
    ).fetchone()
    body = {
        key: value
        for key, value in pattern.items()
        if key not in {"pattern_id", "title", "pattern_type", "status", "scope", "confidence", "evidence"}
    }
    if existing is None:
        conn.execute(
            "INSERT INTO wiki_patterns(pattern_id,title,pattern_type,status,scope,confidence,body,created_at,updated_at) "
            "VALUES(?,?,?,?,?,?,?,?,?)",
            (
                pattern["pattern_id"], pattern["title"], pattern["pattern_type"], pattern["status"],
                pattern["scope"], confidence, _json(body), now, now,
            ),
        )
        event_type = "pattern_created"
    else:
        conn.execute(
            "UPDATE wiki_patterns SET title=?,pattern_type=?,status=?,scope=?,confidence=?,body=?,updated_at=? "
            "WHERE pattern_id=?",
            (
                pattern["title"], pattern["pattern_type"], pattern["status"], pattern["scope"],
                confidence, _json(body), now, pattern["pattern_id"],
            ),
        )
        event_type = "pattern_updated"

    for evidence in pattern.get("evidence", []) or []:
        if isinstance(evidence, str):
            ref, kind = evidence, "trace"
        else:
            ref = evidence.get("ref")
            kind = evidence.get("kind", "trace")
        if ref:
            conn.execute(
                "INSERT OR IGNORE INTO wiki_pattern_evidence(pattern_id,evidence_ref,kind,at) VALUES(?,?,?,?)",
                (pattern["pattern_id"], ref, kind, now),
            )
    _event(conn, event_type, pattern["pattern_id"], pattern, actor)
    conn.commit()
    return {"pattern_id": pattern["pattern_id"], "status": pattern["status"], "event": event_type}


def propose_skill_change(conn: sqlite3.Connection, proposal: dict, actor: str = "skill-proposer") -> dict:
    """Create a governed Skill evolution proposal. Does not modify the Skill file."""
    init_learning_schema(conn)
    required = ("proposal_id", "skill_path", "baseline_version", "candidate_version", "portability")
    missing = [field for field in required if not proposal.get(field)]
    if missing:
        return {"error": f"missing required fields: {', '.join(missing)}"}
    if not _valid_id(str(proposal["proposal_id"])):
        return {"error": "invalid proposal_id"}
    portability = proposal["portability"]
    if portability not in PORTABILITY:
        return {"error": f"invalid portability: {portability}"}
    status = proposal.get("status", "proposed")
    if status not in PROPOSAL_STATUSES:
        return {"error": f"invalid proposal status: {status}"}
    if _contains_private_reasoning(proposal):
        return {"error": "private chain-of-thought/private reasoning must not be persisted"}

    body = {
        key: value
        for key, value in proposal.items()
        if key not in {"proposal_id", "skill_path", "baseline_version", "candidate_version", "portability", "status"}
    }
    now = _now()
    try:
        conn.execute(
            "INSERT INTO skill_evolution_proposals(proposal_id,skill_path,baseline_version,candidate_version,status,portability,body,created_at,updated_at) "
            "VALUES(?,?,?,?,?,?,?,?,?)",
            (
                proposal["proposal_id"], proposal["skill_path"], proposal["baseline_version"],
                proposal["candidate_version"], status, portability, _json(body), now, now,
            ),
        )
        _event(conn, "skill_proposal_created", proposal["proposal_id"], proposal, actor)
        conn.commit()
    except sqlite3.IntegrityError as exc:
        return {"error": str(exc)}
    return {"proposal_id": proposal["proposal_id"], "status": status}


def record_evaluation(conn: sqlite3.Connection, evaluation: dict, actor: str = "evaluator") -> dict:
    """Append an evaluation and materialize the proposal decision.

    The function records the result only. A separate authority/policy gate must perform
    any production Skill write or release.
    """
    init_learning_schema(conn)
    required = ("eval_id", "proposal_id", "decision")
    missing = [field for field in required if not evaluation.get(field)]
    if missing:
        return {"error": f"missing required fields: {', '.join(missing)}"}
    if not _valid_id(str(evaluation["eval_id"])):
        return {"error": "invalid eval_id"}
    if evaluation["decision"] not in EVAL_DECISIONS:
        return {"error": f"invalid decision: {evaluation['decision']}"}
    if _contains_private_reasoning(evaluation):
        return {"error": "private chain-of-thought/private reasoning must not be persisted"}

    proposal = conn.execute(
        "SELECT proposal_id FROM skill_evolution_proposals WHERE proposal_id=?",
        (evaluation["proposal_id"],),
    ).fetchone()
    if proposal is None:
        return {"error": f"proposal not found: {evaluation['proposal_id']}"}

    now = _now()
    try:
        conn.execute(
            "INSERT INTO skill_evaluations(eval_id,proposal_id,decision,metrics,notes,actor,at) VALUES(?,?,?,?,?,?,?)",
            (
                evaluation["eval_id"], evaluation["proposal_id"], evaluation["decision"],
                _json(evaluation.get("metrics", {})), evaluation.get("notes", ""), actor, now,
            ),
        )
        conn.execute(
            "UPDATE skill_evolution_proposals SET status=?,updated_at=? WHERE proposal_id=?",
            (evaluation["decision"], now, evaluation["proposal_id"]),
        )
        _event(conn, "skill_proposal_evaluated", evaluation["proposal_id"], evaluation, actor)
        conn.commit()
    except sqlite3.IntegrityError as exc:
        return {"error": str(exc)}
    return {
        "eval_id": evaluation["eval_id"],
        "proposal_id": evaluation["proposal_id"],
        "decision": evaluation["decision"],
        "production_skill_modified": False,
    }


def get_pattern(conn: sqlite3.Connection, pattern_id: str) -> Optional[dict]:
    init_learning_schema(conn)
    row = conn.execute("SELECT * FROM wiki_patterns WHERE pattern_id=?", (pattern_id,)).fetchone()
    if row is None:
        return None
    columns = [desc[0] for desc in conn.execute("SELECT * FROM wiki_patterns LIMIT 0").description]
    result = dict(zip(columns, row)) if not isinstance(row, sqlite3.Row) else dict(row)
    result["body"] = _decode(result.get("body"))
    evidence_rows = conn.execute(
        "SELECT evidence_ref,kind,at FROM wiki_pattern_evidence WHERE pattern_id=? ORDER BY at",
        (pattern_id,),
    ).fetchall()
    result["evidence"] = [
        dict(item) if isinstance(item, sqlite3.Row) else {"evidence_ref": item[0], "kind": item[1], "at": item[2]}
        for item in evidence_rows
    ]
    return result


def list_patterns(conn: sqlite3.Connection, status: Optional[str] = None, limit: int = 100) -> list[dict]:
    init_learning_schema(conn)
    if status is not None and status not in PATTERN_STATUSES:
        raise ValueError(f"invalid pattern status: {status}")
    limit = max(1, min(int(limit), 1000))
    if status:
        cursor = conn.execute(
            "SELECT * FROM wiki_patterns WHERE status=? ORDER BY updated_at DESC LIMIT ?",
            (status, limit),
        )
    else:
        cursor = conn.execute("SELECT * FROM wiki_patterns ORDER BY updated_at DESC LIMIT ?", (limit,))
    columns = [desc[0] for desc in cursor.description]
    out = []
    for row in cursor.fetchall():
        item = dict(row) if isinstance(row, sqlite3.Row) else dict(zip(columns, row))
        item["body"] = _decode(item.get("body"))
        out.append(item)
    return out
