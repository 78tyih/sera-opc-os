"""PR-based release controller for Sera Learning OS.

This module turns a `release_ready` Shadow Patch into a governed release request.
It deliberately stops short of touching GitHub or production files. GitHub branch / PR
creation is handled by an adapter using the payload emitted here.

Security invariant:
    release_ready != approved != merged != post-release-verified

The same autonomous loop may propose, patch, and evaluate, but production authority
must be represented by an explicit release event from a human or policy authority.
"""

from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from datetime import datetime, timezone
from typing import Optional

from .learning import init_learning_schema
from .shadow_patch import get_shadow_patch, validate_shadow_baseline


AUTHORITY_PREFIXES = ("human:", "policy:", "founder:")
EVENT_TO_STATE = {
    "release_prepared": "prepared",
    "draft_pr_opened": "draft_pr_open",
    "branch_ci_passed": "ci_passed",
    "branch_ci_failed": "blocked",
    "approval_granted": "approved",
    "approval_denied": "denied",
    "merged": "merged",
    "post_release_verified": "verified",
    "post_release_regression": "rollback_required",
    "rollback_requested": "rollback_requested",
    "rolled_back": "rolled_back",
    "cancelled": "cancelled",
}
ALLOWED_TRANSITIONS = {
    None: {"prepared"},
    "prepared": {"draft_pr_open", "cancelled"},
    "draft_pr_open": {"ci_passed", "blocked", "cancelled"},
    "ci_passed": {"approved", "denied", "cancelled"},
    "approved": {"merged", "cancelled"},
    "merged": {"verified", "rollback_required"},
    "rollback_required": {"rollback_requested"},
    "rollback_requested": {"rolled_back"},
    "blocked": {"cancelled"},
    "denied": {"cancelled"},
    "verified": set(),
    "rolled_back": set(),
    "cancelled": set(),
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _slug(value: str, limit: int = 48) -> str:
    value = re.sub(r"[^a-zA-Z0-9._-]+", "-", value).strip("-._").lower()
    return (value or "skill")[:limit]


def _row_to_dict(cursor: sqlite3.Cursor, row) -> dict:
    if isinstance(row, sqlite3.Row):
        return dict(row)
    return dict(zip([d[0] for d in cursor.description], row))


def init_release_schema(conn: sqlite3.Connection) -> sqlite3.Connection:
    init_learning_schema(conn)
    conn.executescript(
        """
CREATE TABLE IF NOT EXISTS skill_release_requests(
    request_id TEXT PRIMARY KEY,
    proposal_id TEXT NOT NULL,
    patch_id TEXT NOT NULL,
    readiness_id TEXT NOT NULL,
    target_repo TEXT NOT NULL,
    base_branch TEXT NOT NULL,
    candidate_branch TEXT NOT NULL,
    skill_path TEXT NOT NULL,
    baseline_sha256 TEXT NOT NULL,
    candidate_sha256 TEXT NOT NULL,
    rollback_version TEXT NOT NULL,
    risk_class TEXT NOT NULL CHECK(risk_class IN('low','medium','high','critical')),
    payload TEXT NOT NULL DEFAULT '{}',
    created_by TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY(proposal_id) REFERENCES skill_evolution_proposals(proposal_id),
    FOREIGN KEY(patch_id) REFERENCES skill_shadow_patches(patch_id),
    FOREIGN KEY(readiness_id) REFERENCES skill_release_readiness(readiness_id)
);
CREATE TRIGGER IF NOT EXISTS release_request_no_update BEFORE UPDATE ON skill_release_requests
BEGIN SELECT RAISE(ABORT,'skill_release_requests is append-only'); END;
CREATE TRIGGER IF NOT EXISTS release_request_no_delete BEFORE DELETE ON skill_release_requests
BEGIN SELECT RAISE(ABORT,'skill_release_requests is append-only'); END;

CREATE TABLE IF NOT EXISTS skill_release_events(
    event_id TEXT PRIMARY KEY,
    request_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    state TEXT NOT NULL,
    payload TEXT NOT NULL DEFAULT '{}',
    actor TEXT NOT NULL,
    at TEXT NOT NULL,
    FOREIGN KEY(request_id) REFERENCES skill_release_requests(request_id)
);
CREATE TRIGGER IF NOT EXISTS release_event_no_update BEFORE UPDATE ON skill_release_events
BEGIN SELECT RAISE(ABORT,'skill_release_events is append-only'); END;
CREATE TRIGGER IF NOT EXISTS release_event_no_delete BEFORE DELETE ON skill_release_events
BEGIN SELECT RAISE(ABORT,'skill_release_events is append-only'); END;
"""
    )
    conn.commit()
    return conn


def get_release_request(conn: sqlite3.Connection, request_id: str) -> Optional[dict]:
    init_release_schema(conn)
    cursor = conn.execute("SELECT * FROM skill_release_requests WHERE request_id=?", (request_id,))
    row = cursor.fetchone()
    if row is None:
        return None
    item = _row_to_dict(cursor, row)
    try:
        item["payload"] = json.loads(item.get("payload") or "{}")
    except (TypeError, json.JSONDecodeError):
        item["payload"] = {}
    item["state"] = current_release_state(conn, request_id)
    return item


def list_release_events(conn: sqlite3.Connection, request_id: str) -> list[dict]:
    init_release_schema(conn)
    cursor = conn.execute(
        "SELECT * FROM skill_release_events WHERE request_id=? ORDER BY at,event_id", (request_id,)
    )
    columns = [d[0] for d in cursor.description]
    out = []
    for row in cursor.fetchall():
        item = dict(row) if isinstance(row, sqlite3.Row) else dict(zip(columns, row))
        try:
            item["payload"] = json.loads(item.get("payload") or "{}")
        except (TypeError, json.JSONDecodeError):
            item["payload"] = {}
        out.append(item)
    return out


def current_release_state(conn: sqlite3.Connection, request_id: str) -> Optional[str]:
    init_release_schema(conn)
    row = conn.execute(
        "SELECT state FROM skill_release_events WHERE request_id=? ORDER BY at DESC,event_id DESC LIMIT 1",
        (request_id,),
    ).fetchone()
    if row is None:
        return None
    return row["state"] if isinstance(row, sqlite3.Row) else row[0]


def _readiness(conn: sqlite3.Connection, readiness_id: str) -> Optional[dict]:
    cursor = conn.execute("SELECT * FROM skill_release_readiness WHERE readiness_id=?", (readiness_id,))
    row = cursor.fetchone()
    if row is None:
        return None
    return _row_to_dict(cursor, row)


def _proposal(conn: sqlite3.Connection, proposal_id: str) -> Optional[dict]:
    cursor = conn.execute("SELECT * FROM skill_evolution_proposals WHERE proposal_id=?", (proposal_id,))
    row = cursor.fetchone()
    if row is None:
        return None
    item = _row_to_dict(cursor, row)
    try:
        item["body"] = json.loads(item.get("body") or "{}")
    except (TypeError, json.JSONDecodeError):
        item["body"] = {}
    return item


def build_pr_payload(
    conn: sqlite3.Connection,
    *,
    proposal_id: str,
    patch_id: str,
    readiness_id: str,
    target_repo: str,
    current_production_content: str,
    base_branch: str = "main",
    risk_class: str = "medium",
) -> dict:
    """Validate gates and construct a deterministic Draft-PR release payload."""
    init_release_schema(conn)
    readiness = _readiness(conn, readiness_id)
    if readiness is None:
        return {"error": f"readiness not found: {readiness_id}"}
    if readiness["proposal_id"] != proposal_id or readiness["patch_id"] != patch_id:
        return {"error": "readiness/proposal/patch mismatch"}
    if readiness["status"] != "release_ready":
        return {"error": f"release blocked: readiness={readiness['status']}"}
    if risk_class not in {"low", "medium", "high", "critical"}:
        return {"error": f"invalid risk_class: {risk_class}"}

    patch = get_shadow_patch(conn, patch_id)
    if patch is None:
        return {"error": f"shadow patch not found: {patch_id}"}
    if patch["proposal_id"] != proposal_id:
        return {"error": "patch/proposal mismatch"}

    baseline = validate_shadow_baseline(conn, patch_id, current_production_content)
    if baseline.get("release_blocked"):
        return {
            "error": "production baseline changed after Shadow Patch generation",
            "stage": "baseline_guard",
            **baseline,
        }

    proposal = _proposal(conn, proposal_id)
    if proposal is None:
        return {"error": f"proposal not found: {proposal_id}"}

    seed = f"{proposal_id}|{patch_id}|{readiness_id}|{patch['candidate_sha256']}"
    suffix = hashlib.sha1(seed.encode("utf-8")).hexdigest()[:8]
    skill_name = patch["skill_path"].split("/")[-2] if "/" in patch["skill_path"] else patch["skill_path"]
    candidate_branch = f"skill-evolution/{_slug(skill_name)}/{_slug(patch['candidate_version'])}-{suffix}"

    source_patterns = proposal.get("body", {}).get("source_patterns") or []
    title = f"skill: evolve {skill_name} to {patch['candidate_version']}"
    body = (
        "## Sera Learning OS — governed Skill release\n\n"
        f"- Proposal: `{proposal_id}`\n"
        f"- Shadow patch: `{patch_id}`\n"
        f"- Release readiness: `{readiness_id}`\n"
        f"- Skill: `{patch['skill_path']}`\n"
        f"- Baseline: `{patch['baseline_version']}` (`{patch['baseline_sha256']}`)\n"
        f"- Candidate: `{patch['candidate_version']}` (`{patch['candidate_sha256']}`)\n"
        f"- Rollback target: `{patch['baseline_version']}`\n"
        f"- Risk class: `{risk_class}`\n"
        f"- Source Patterns: {', '.join(f'`{p}`' for p in source_patterns) if source_patterns else 'n/a'}\n\n"
        "### Gates\n"
        "- [x] Pattern evidence matured\n"
        "- [x] Shadow Patch generated\n"
        "- [x] Regression Harness passed\n"
        "- [x] Portability Gate acceptable for declared scope\n"
        "- [ ] Candidate branch CI passed\n"
        "- [ ] Human / Policy authority approval recorded\n"
        "- [ ] Post-release verification completed\n\n"
        "### Safety\n"
        "This PR is generated as a **draft candidate**. `release_ready` does not authorize merge. "
        "If production changed after the recorded baseline hash, the release must be regenerated.\n"
    )

    return {
        "proposal_id": proposal_id,
        "patch_id": patch_id,
        "readiness_id": readiness_id,
        "target_repo": target_repo,
        "base_branch": base_branch,
        "candidate_branch": candidate_branch,
        "skill_path": patch["skill_path"],
        "baseline_sha256": patch["baseline_sha256"],
        "candidate_sha256": patch["candidate_sha256"],
        "candidate_content": patch["candidate_content"],
        "unified_diff": patch["unified_diff"],
        "rollback_version": patch["baseline_version"],
        "risk_class": risk_class,
        "pr": {"title": title, "body": body, "draft": True},
        "production_skill_modified": False,
        "merge_authorized": False,
    }


def prepare_release_request(
    conn: sqlite3.Connection,
    *,
    proposal_id: str,
    patch_id: str,
    readiness_id: str,
    target_repo: str,
    current_production_content: str,
    base_branch: str = "main",
    risk_class: str = "medium",
    actor: str = "release-controller",
) -> dict:
    """Persist an immutable release request and initial `prepared` event."""
    payload = build_pr_payload(
        conn,
        proposal_id=proposal_id,
        patch_id=patch_id,
        readiness_id=readiness_id,
        target_repo=target_repo,
        current_production_content=current_production_content,
        base_branch=base_branch,
        risk_class=risk_class,
    )
    if payload.get("error"):
        return payload

    seed = f"{proposal_id}|{patch_id}|{readiness_id}|{payload['candidate_sha256']}"
    request_id = "REL." + hashlib.sha1(seed.encode("utf-8")).hexdigest()[:14]
    timestamp = _now()
    try:
        conn.execute(
            """
            INSERT INTO skill_release_requests(
              request_id,proposal_id,patch_id,readiness_id,target_repo,base_branch,candidate_branch,
              skill_path,baseline_sha256,candidate_sha256,rollback_version,risk_class,payload,created_by,created_at
            ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                request_id, proposal_id, patch_id, readiness_id, target_repo, base_branch,
                payload["candidate_branch"], payload["skill_path"], payload["baseline_sha256"],
                payload["candidate_sha256"], payload["rollback_version"], risk_class,
                json.dumps(payload, ensure_ascii=False), actor, timestamp,
            ),
        )
        conn.commit()
    except sqlite3.IntegrityError as exc:
        if "UNIQUE constraint failed" not in str(exc):
            return {"error": str(exc)}
        existing = get_release_request(conn, request_id)
        return {**(existing or {}), "request_id": request_id, "recorded": False}

    event = record_release_event(
        conn,
        request_id=request_id,
        event_type="release_prepared",
        actor=actor,
        payload={"candidate_branch": payload["candidate_branch"], "draft_pr": True},
    )
    if event.get("error"):
        return event
    return {
        **payload,
        "request_id": request_id,
        "state": "prepared",
        "recorded": True,
    }


def _authority_actor(actor: str) -> bool:
    value = str(actor or "").lower()
    return value == "founder" or value.startswith(AUTHORITY_PREFIXES)


def record_release_event(
    conn: sqlite3.Connection,
    *,
    request_id: str,
    event_type: str,
    actor: str,
    payload: Optional[dict] = None,
    at: Optional[str] = None,
) -> dict:
    """Append a release lifecycle event after validating state transition and authority."""
    init_release_schema(conn)
    request = conn.execute("SELECT request_id FROM skill_release_requests WHERE request_id=?", (request_id,)).fetchone()
    if request is None:
        return {"error": f"release request not found: {request_id}"}
    if event_type not in EVENT_TO_STATE:
        return {"error": f"invalid release event: {event_type}"}

    old_state = current_release_state(conn, request_id)
    new_state = EVENT_TO_STATE[event_type]
    if new_state not in ALLOWED_TRANSITIONS.get(old_state, set()):
        return {"error": f"invalid release transition: {old_state} -> {new_state}"}

    if event_type == "approval_granted" and not _authority_actor(actor):
        return {
            "error": "approval_granted requires explicit human/policy authority actor",
            "required_actor_prefixes": list(AUTHORITY_PREFIXES) + ["founder"],
        }
    if event_type in {"merged", "rollback_requested", "rolled_back"} and not _authority_actor(actor):
        return {"error": f"{event_type} requires explicit human/policy authority actor"}

    timestamp = at or _now()
    event_payload = payload or {}
    seed = f"{request_id}|{event_type}|{actor}|{timestamp}|{json.dumps(event_payload, sort_keys=True, default=str)}"
    event_id = "RELEVT." + hashlib.sha1(seed.encode("utf-8")).hexdigest()[:16]
    try:
        conn.execute(
            "INSERT INTO skill_release_events(event_id,request_id,event_type,state,payload,actor,at) VALUES(?,?,?,?,?,?,?)",
            (
                event_id, request_id, event_type, new_state,
                json.dumps(event_payload, ensure_ascii=False), actor, timestamp,
            ),
        )
        conn.execute(
            "INSERT INTO learning_events(event_type,object_id,payload,actor,at) VALUES(?,?,?,?,?)",
            (
                "skill_release_event",
                request_id,
                json.dumps({"release_event": event_type, "state": new_state, **event_payload}, ensure_ascii=False),
                actor,
                timestamp,
            ),
        )
        conn.commit()
    except sqlite3.IntegrityError as exc:
        return {"error": str(exc)}

    return {
        "event_id": event_id,
        "request_id": request_id,
        "event_type": event_type,
        "previous_state": old_state,
        "state": new_state,
        "production_skill_modified": event_type == "merged",
        "authority_recorded": event_type == "approval_granted",
    }
