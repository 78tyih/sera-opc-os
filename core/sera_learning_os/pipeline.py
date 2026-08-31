"""Unified governed ingestion pipeline for Sera Learning OS.

One observable Learning Signal can:
1. be persisted as Raw evidence;
2. update/create a supportive Wiki Pattern when it contains a reusable mechanism;
3. append explicit contradiction evidence against existing Patterns;
4. create Skill proposals only from Patterns already meeting verification gates.

It never modifies a production Skill.
"""

from __future__ import annotations

import sqlite3
from typing import Any

from .contradictions import record_pattern_contradiction
from .skill_proposer import propose_ready_skills
from .wiki_maintainer import compile_signal_to_wiki


def _task_context(signal: dict) -> str:
    project = str(signal.get("project") or "unknown")
    task = str(signal.get("task") or signal.get("run_id") or signal.get("trace_id") or "unknown")
    return f"{project}::{task}"


def _normalized_signal(signal: dict) -> dict:
    """Bridge schema naming to the runtime store without changing the external contract."""
    normalized = dict(signal)
    if normalized.get("observed_at") and not normalized.get("at"):
        normalized["at"] = normalized["observed_at"]
    return normalized


def _contradiction_specs(signal: dict) -> list[dict]:
    specs = []
    for item in signal.get("contradictions", []) or []:
        if isinstance(item, str):
            specs.append({
                "pattern_id": item,
                "reason": signal.get("contradiction_reason") or signal.get("human_feedback") or "Contradictory execution evidence",
            })
        elif isinstance(item, dict) and item.get("pattern_id"):
            specs.append(dict(item))

    for pattern_id in signal.get("contradicts_pattern_ids", []) or []:
        if any(spec.get("pattern_id") == pattern_id for spec in specs):
            continue
        specs.append({
            "pattern_id": pattern_id,
            "reason": signal.get("contradiction_reason") or signal.get("human_feedback") or "Contradictory execution evidence",
            "strength": signal.get("contradiction_strength", 0.70),
            "explicit": signal.get("contradiction_explicit", False),
        })
    return specs


def process_learning_signal(
    conn: sqlite3.Connection,
    signal: dict,
    *,
    actor: str = "learning-pipeline",
    auto_propose: bool = True,
) -> dict:
    """Process one Learning Signal through Raw -> Wiki -> Contradiction -> Proposal.

    `auto_propose=True` only creates proposal records. It does not evaluate, release,
    patch, commit or modify production Skills.
    """
    normalized = _normalized_signal(signal)
    wiki_result = compile_signal_to_wiki(conn, normalized, actor=actor, record_raw=True)
    if wiki_result.get("error"):
        return {"error": wiki_result["error"], "stage": wiki_result.get("stage", "wiki")}

    contradiction_results = []
    for spec in _contradiction_specs(normalized):
        result = record_pattern_contradiction(
            conn,
            pattern_id=str(spec["pattern_id"]),
            evidence_ref=str(spec.get("evidence_ref") or normalized.get("trace_id")),
            reason=str(spec.get("reason") or "Contradictory execution evidence"),
            source_agent=str(normalized.get("source_agent") or "unknown"),
            source_model=str(normalized.get("source_model") or "unknown"),
            task_context=str(spec.get("task_context") or _task_context(normalized)),
            strength=float(spec.get("strength", 0.70)),
            explicit=bool(spec.get("explicit", False)),
            actor=actor,
            at=normalized.get("at"),
        )
        contradiction_results.append(result)

    proposals = propose_ready_skills(conn) if auto_propose else []
    return {
        "trace_id": normalized.get("trace_id"),
        "wiki": wiki_result,
        "contradictions": contradiction_results,
        "proposals": proposals,
        "production_skill_modified": False,
    }
