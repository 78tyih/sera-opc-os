"""Automatic Wiki Maintainer for Sera Learning OS.

The maintainer compiles observable Learning Signals into persistent Wiki patterns.
It is intentionally conservative:
- failure patterns prefer concrete root_cause / tool error signatures;
- symptom-only failures never become verified automatically;
- verification requires repeated evidence across independent task contexts;
- private reasoning is never required or persisted.
"""

from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from typing import Any, Optional

from .learning import get_pattern, record_raw_signal, upsert_pattern


MIN_SUPPORTED_EVIDENCE = 2
MIN_VERIFIED_EVIDENCE = 3
MIN_VERIFIED_CONTEXTS = 3


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


def _normalize(text: str) -> str:
    text = re.sub(r"\s+", " ", (text or "").strip().lower())
    text = re.sub(r"[^\w\-.:/\u4e00-\u9fff ]+", "", text)
    return text[:500]


def _hash_key(*parts: str) -> str:
    raw = "|".join(_normalize(p) for p in parts if p)
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:12]


def _independent_context(signal: dict) -> str:
    project = str(signal.get("project") or "unknown")
    task = str(signal.get("task") or signal.get("run_id") or signal.get("trace_id"))
    return f"{project}::{task}"


def _affected_skills(signal: dict) -> list[dict]:
    out = []
    for item in signal.get("affected_skills", []) or []:
        if isinstance(item, str):
            out.append({"path": item})
        elif isinstance(item, dict) and item.get("path"):
            out.append(dict(item))
    return out


def _tool_error_signatures(signal: dict) -> list[str]:
    signatures = []
    for event in signal.get("tool_events", []) or []:
        if isinstance(event, dict) and event.get("error_signature"):
            signatures.append(str(event["error_signature"]))
    return signatures


def _derive_candidate(signal: dict) -> Optional[dict]:
    """Derive one conservative pattern candidate from a learning signal."""
    outcome = signal.get("outcome")
    signal_types = set(signal.get("signal_types") or [])
    root_cause = (signal.get("root_cause") or "").strip()
    failure_mode = (signal.get("failure_mode") or "").strip()
    success_mechanism = (signal.get("success_mechanism") or "").strip()
    tool_errors = _tool_error_signatures(signal)

    basis = ""
    basis_kind = ""
    pattern_type = "heuristic"
    title_prefix = "Observed pattern"
    verification_blocked = False

    if outcome in {"failure", "partial"}:
        pattern_type = "failure_pattern"
        title_prefix = "Failure pattern"
        if root_cause:
            basis = root_cause
            basis_kind = "root_cause"
        elif tool_errors:
            basis = tool_errors[0]
            basis_kind = "tool_error_signature"
        elif failure_mode:
            basis = failure_mode
            basis_kind = "failure_mode"
            verification_blocked = True
        else:
            return None
    elif outcome == "success" and ("repeat_success" in signal_types or success_mechanism):
        if not success_mechanism:
            return None
        pattern_type = "success_pattern"
        title_prefix = "Success pattern"
        basis = success_mechanism
        basis_kind = "success_mechanism"
    elif "anti_pattern" in signal_types:
        basis = root_cause or failure_mode
        if not basis:
            return None
        pattern_type = "anti_pattern"
        title_prefix = "Anti-pattern"
        basis_kind = "root_cause" if root_cause else "failure_mode"
        verification_blocked = not bool(root_cause)
    else:
        return None

    if "model_behavior" in signal_types:
        pattern_type = "model_behavior"
        title_prefix = "Model behavior"
    elif "tool_behavior" in signal_types:
        pattern_type = "tool_behavior"
        title_prefix = "Tool behavior"
    elif "workflow_behavior" in signal_types:
        pattern_type = "workflow_pattern"
        title_prefix = "Workflow pattern"

    scope_anchor = str(signal.get("project") or "organization")
    identity = _hash_key(pattern_type, basis_kind, basis, scope_anchor)
    pattern_id = f"PAT.auto.{identity}"
    short_basis = re.sub(r"\s+", " ", basis).strip()
    if len(short_basis) > 96:
        short_basis = short_basis[:93] + "..."

    return {
        "pattern_id": pattern_id,
        "title": f"{title_prefix}: {short_basis}",
        "pattern_type": pattern_type,
        "scope": "project" if signal.get("project") else "organization",
        "basis": basis,
        "basis_kind": basis_kind,
        "verification_blocked": verification_blocked,
        "failure_mode": failure_mode or None,
        "root_cause": root_cause or None,
        "success_mechanism": success_mechanism or None,
        "recommended_action": signal.get("recommended_action"),
        "affected_skills": _affected_skills(signal),
    }


def _merge_unique(existing: list, new_items: list) -> list:
    result = list(existing or [])
    seen = {json.dumps(item, ensure_ascii=False, sort_keys=True, default=str) for item in result}
    for item in new_items or []:
        key = json.dumps(item, ensure_ascii=False, sort_keys=True, default=str)
        if key not in seen:
            result.append(item)
            seen.add(key)
    return result


def _status_and_confidence(evidence_count: int, context_count: int, blocked: bool) -> tuple[str, float]:
    if evidence_count >= MIN_VERIFIED_EVIDENCE and context_count >= MIN_VERIFIED_CONTEXTS and not blocked:
        return "verified", min(0.95, 0.72 + 0.06 * min(evidence_count, 4))
    if evidence_count >= MIN_SUPPORTED_EVIDENCE:
        return "supported", min(0.84, 0.58 + 0.07 * min(evidence_count, 3))
    return "provisional", 0.50


def compile_signal_to_wiki(
    conn: sqlite3.Connection,
    signal: dict,
    actor: str = "wiki-maintainer",
    record_raw: bool = True,
) -> dict:
    """Persist a signal and compile it into a persistent Wiki pattern.

    Returns a deterministic pattern status. Replaying the exact same trace is idempotent
    for pattern evidence; raw storage remains append-only and duplicate trace IDs are skipped.
    """
    if record_raw:
        raw_result = record_raw_signal(conn, signal, actor=actor)
        if raw_result.get("error") and "UNIQUE constraint failed" not in raw_result["error"]:
            return {"error": raw_result["error"], "stage": "raw"}

    candidate = _derive_candidate(signal)
    if candidate is None:
        return {
            "trace_id": signal.get("trace_id"),
            "status": "recorded_no_pattern",
            "reason": "signal lacks a reusable root_cause/success_mechanism pattern basis",
        }

    existing = get_pattern(conn, candidate["pattern_id"])
    existing_body = _decode(existing.get("body")) if existing else {}
    existing_evidence = existing.get("evidence", []) if existing else []
    evidence_refs = {item.get("evidence_ref") for item in existing_evidence if isinstance(item, dict)}
    evidence_refs.add(str(signal["trace_id"]))

    contexts = set(existing_body.get("independent_contexts", []) or [])
    contexts.add(_independent_context(signal))
    agents = set(existing_body.get("source_agents", []) or [])
    agents.add(str(signal.get("source_agent") or "unknown"))
    models = set(existing_body.get("source_models", []) or [])
    models.add(str(signal.get("source_model") or "unknown"))
    projects = set(existing_body.get("projects", []) or [])
    if signal.get("project"):
        projects.add(str(signal["project"]))

    affected_skills = _merge_unique(existing_body.get("affected_skills", []), candidate["affected_skills"])
    blocked = bool(existing_body.get("verification_blocked")) or candidate["verification_blocked"]
    evidence_count = len([ref for ref in evidence_refs if ref])
    context_count = len(contexts)
    status, confidence = _status_and_confidence(evidence_count, context_count, blocked)

    pattern = {
        "pattern_id": candidate["pattern_id"],
        "title": candidate["title"],
        "pattern_type": candidate["pattern_type"],
        "status": status,
        "scope": candidate["scope"],
        "confidence": confidence,
        "basis": candidate["basis"],
        "basis_kind": candidate["basis_kind"],
        "verification_blocked": blocked,
        "failure_mode": candidate["failure_mode"] or existing_body.get("failure_mode"),
        "root_cause": candidate["root_cause"] or existing_body.get("root_cause"),
        "success_mechanism": candidate["success_mechanism"] or existing_body.get("success_mechanism"),
        "recommended_action": candidate["recommended_action"] or existing_body.get("recommended_action"),
        "evidence_count": evidence_count,
        "independent_context_count": context_count,
        "independent_contexts": sorted(contexts),
        "source_agents": sorted(agents),
        "source_models": sorted(models),
        "projects": sorted(projects),
        "affected_skills": affected_skills,
        "last_trace_id": signal["trace_id"],
        "evidence": [{"ref": signal["trace_id"], "kind": "trace"}],
    }
    result = upsert_pattern(conn, pattern, actor=actor)
    result.update({
        "evidence_count": evidence_count,
        "independent_context_count": context_count,
        "confidence": confidence,
        "verification_blocked": blocked,
    })
    return result


def maintain_uncompiled_signals(conn: sqlite3.Connection, limit: int = 500) -> list[dict]:
    """Compile raw signals that have not yet been linked as pattern evidence."""
    limit = max(1, min(int(limit), 5000))
    rows = conn.execute(
        """
        SELECT r.*
        FROM learning_raw_signals r
        WHERE NOT EXISTS (
          SELECT 1 FROM wiki_pattern_evidence e WHERE e.evidence_ref = r.trace_id
        )
        ORDER BY r.at ASC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    results = []
    columns = [d[0] for d in conn.execute("SELECT * FROM learning_raw_signals LIMIT 0").description]
    for row in rows:
        item = dict(row) if isinstance(row, sqlite3.Row) else dict(zip(columns, row))
        payload = _decode(item.pop("payload", {}))
        signal = {**item, **payload}
        signal.setdefault("trace_id", item["trace_id"])
        results.append(compile_signal_to_wiki(conn, signal, record_raw=False))
    return results
