"""Cross-model Skill portability evaluation for Sera Learning OS.

WikiSkill shows that a Skill improvement can transfer across models, but negative
transfer is also possible. This module stores append-only baseline/candidate probes
and produces a governed evaluation recommendation. It never releases a Skill.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
from collections import defaultdict
from datetime import datetime, timezone
from typing import Optional

from .learning import init_learning_schema, record_evaluation


MIN_MODELS_FOR_UNIVERSAL = 2
REGRESSION_THRESHOLD = -0.05
NON_REGRESSION_FLOOR = -0.01
MEAN_IMPROVEMENT_THRESHOLD = 0.02
MODEL_IMPROVEMENT_THRESHOLD = 0.02


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def init_portability_schema(conn: sqlite3.Connection) -> sqlite3.Connection:
    init_learning_schema(conn)
    conn.executescript(
        """
CREATE TABLE IF NOT EXISTS skill_portability_probes(
    probe_id TEXT PRIMARY KEY,
    proposal_id TEXT NOT NULL,
    model TEXT NOT NULL,
    model_family TEXT,
    agent_shell TEXT,
    environment TEXT,
    metric_name TEXT NOT NULL,
    baseline_score REAL NOT NULL,
    candidate_score REAL NOT NULL,
    metadata TEXT NOT NULL DEFAULT '{}',
    at TEXT NOT NULL,
    FOREIGN KEY(proposal_id) REFERENCES skill_evolution_proposals(proposal_id)
);
CREATE TRIGGER IF NOT EXISTS portability_probes_no_update
BEFORE UPDATE ON skill_portability_probes
BEGIN SELECT RAISE(ABORT,'skill_portability_probes is append-only'); END;
CREATE TRIGGER IF NOT EXISTS portability_probes_no_delete
BEFORE DELETE ON skill_portability_probes
BEGIN SELECT RAISE(ABORT,'skill_portability_probes is append-only'); END;
"""
    )
    conn.commit()
    return conn


def record_portability_probe(
    conn: sqlite3.Connection,
    *,
    probe_id: str,
    proposal_id: str,
    model: str,
    metric_name: str,
    baseline_score: float,
    candidate_score: float,
    model_family: Optional[str] = None,
    agent_shell: Optional[str] = None,
    environment: Optional[str] = None,
    metadata: Optional[dict] = None,
    at: Optional[str] = None,
    actor: str = "evaluator",
) -> dict:
    """Append one baseline-vs-candidate probe for one model/environment."""
    init_portability_schema(conn)
    proposal = conn.execute(
        "SELECT proposal_id FROM skill_evolution_proposals WHERE proposal_id=?", (proposal_id,)
    ).fetchone()
    if proposal is None:
        return {"error": f"proposal not found: {proposal_id}"}
    if not probe_id or not model or not metric_name:
        return {"error": "probe_id, model and metric_name are required"}
    for name, value in (("baseline_score", baseline_score), ("candidate_score", candidate_score)):
        if not isinstance(value, (int, float)):
            return {"error": f"{name} must be numeric"}

    timestamp = at or _now()
    payload = metadata or {}
    try:
        conn.execute(
            """
            INSERT INTO skill_portability_probes(
                probe_id,proposal_id,model,model_family,agent_shell,environment,
                metric_name,baseline_score,candidate_score,metadata,at
            ) VALUES(?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                probe_id, proposal_id, model, model_family, agent_shell, environment,
                metric_name, float(baseline_score), float(candidate_score),
                json.dumps(payload, ensure_ascii=False), timestamp,
            ),
        )
        conn.execute(
            "INSERT INTO learning_events(event_type,object_id,payload,actor,at) VALUES(?,?,?,?,?)",
            (
                "portability_probe_recorded",
                proposal_id,
                json.dumps({
                    "probe_id": probe_id,
                    "model": model,
                    "model_family": model_family,
                    "metric_name": metric_name,
                    "baseline_score": baseline_score,
                    "candidate_score": candidate_score,
                    "delta": float(candidate_score) - float(baseline_score),
                }, ensure_ascii=False),
                actor,
                timestamp,
            ),
        )
        conn.commit()
    except sqlite3.IntegrityError as exc:
        return {"error": str(exc)}
    return {
        "probe_id": probe_id,
        "proposal_id": proposal_id,
        "model": model,
        "delta": float(candidate_score) - float(baseline_score),
        "status": "recorded",
    }


def list_portability_probes(conn: sqlite3.Connection, proposal_id: str) -> list[dict]:
    init_portability_schema(conn)
    cursor = conn.execute(
        "SELECT * FROM skill_portability_probes WHERE proposal_id=? ORDER BY at ASC", (proposal_id,)
    )
    columns = [d[0] for d in cursor.description]
    out = []
    for row in cursor.fetchall():
        item = dict(row) if isinstance(row, sqlite3.Row) else dict(zip(columns, row))
        try:
            item["metadata"] = json.loads(item.get("metadata") or "{}")
        except (TypeError, json.JSONDecodeError):
            item["metadata"] = {}
        item["delta"] = float(item["candidate_score"]) - float(item["baseline_score"])
        out.append(item)
    return out


def assess_portability(conn: sqlite3.Connection, proposal_id: str) -> dict:
    """Assess cross-model transfer without mutating proposal/evaluation state."""
    probes = list_portability_probes(conn, proposal_id)
    if not probes:
        return {
            "proposal_id": proposal_id,
            "decision": "insufficient_evidence",
            "recommended_portability": None,
            "reason": "no_portability_probes",
            "models": {},
        }

    by_model = defaultdict(list)
    family_by_model = {}
    for probe in probes:
        by_model[probe["model"]].append(probe["delta"])
        if probe.get("model_family"):
            family_by_model[probe["model"]] = probe["model_family"]

    model_stats = {
        model: {
            "probe_count": len(deltas),
            "mean_delta": sum(deltas) / len(deltas),
            "min_delta": min(deltas),
            "max_delta": max(deltas),
            "model_family": family_by_model.get(model),
        }
        for model, deltas in by_model.items()
    }
    means = [stats["mean_delta"] for stats in model_stats.values()]
    average_delta = sum(means) / len(means)
    regressions = [model for model, stats in model_stats.items() if stats["mean_delta"] <= REGRESSION_THRESHOLD]
    improvements = [model for model, stats in model_stats.items() if stats["mean_delta"] >= MODEL_IMPROVEMENT_THRESHOLD]
    non_regressing = [model for model, stats in model_stats.items() if stats["mean_delta"] >= NON_REGRESSION_FLOOR]

    if len(model_stats) < MIN_MODELS_FOR_UNIVERSAL:
        return {
            "proposal_id": proposal_id,
            "decision": "insufficient_evidence",
            "recommended_portability": "model_specific" if improvements else None,
            "reason": "need_multiple_models_for_universal_claim",
            "models": model_stats,
            "average_delta": average_delta,
        }

    if regressions:
        if improvements:
            families_improved = {family_by_model.get(m) for m in improvements if family_by_model.get(m)}
            families_regressed = {family_by_model.get(m) for m in regressions if family_by_model.get(m)}
            family_specific = bool(families_improved) and families_improved.isdisjoint(families_regressed)
            return {
                "proposal_id": proposal_id,
                "decision": "model_specific",
                "recommended_portability": "model_family" if family_specific else "model_specific",
                "reason": "negative_transfer_detected",
                "models": model_stats,
                "average_delta": average_delta,
                "regressed_models": regressions,
                "improved_models": improvements,
            }
        return {
            "proposal_id": proposal_id,
            "decision": "rejected",
            "recommended_portability": None,
            "reason": "candidate_regresses_without_compensating_model_gain",
            "models": model_stats,
            "average_delta": average_delta,
            "regressed_models": regressions,
        }

    if len(non_regressing) == len(model_stats) and average_delta >= MEAN_IMPROVEMENT_THRESHOLD:
        return {
            "proposal_id": proposal_id,
            "decision": "accepted",
            "recommended_portability": "universal",
            "reason": "multi_model_improvement_without_material_regression",
            "models": model_stats,
            "average_delta": average_delta,
        }

    return {
        "proposal_id": proposal_id,
        "decision": "revise",
        "recommended_portability": None,
        "reason": "mixed_or_neutral_results_need_more_work",
        "models": model_stats,
        "average_delta": average_delta,
    }


def _assessment_id(proposal_id: str, probes: list[dict]) -> str:
    refs = "|".join(sorted(str(p["probe_id"]) for p in probes))
    digest = hashlib.sha1(f"{proposal_id}|{refs}".encode("utf-8")).hexdigest()[:10]
    return f"EVAL.portability.{digest}"


def assess_and_record_portability(
    conn: sqlite3.Connection,
    proposal_id: str,
    actor: str = "portability-evaluator",
) -> dict:
    """Assess probes and append the resulting governed Evaluation decision.

    This may mark the proposal accepted/rejected/model_specific/revise/etc., but it
    still does NOT modify or release a production Skill.
    """
    assessment = assess_portability(conn, proposal_id)
    probes = list_portability_probes(conn, proposal_id)
    if not probes:
        return {**assessment, "evaluation_recorded": False, "production_skill_modified": False}

    if assessment["decision"] == "model_specific" and assessment.get("recommended_portability"):
        conn.execute(
            "UPDATE skill_evolution_proposals SET portability=?,updated_at=? WHERE proposal_id=?",
            (assessment["recommended_portability"], _now(), proposal_id),
        )
        conn.commit()

    evaluation = {
        "eval_id": _assessment_id(proposal_id, probes),
        "proposal_id": proposal_id,
        "decision": assessment["decision"],
        "metrics": {
            "evaluation_type": "cross_model_portability",
            "average_delta": assessment.get("average_delta"),
            "models": assessment.get("models", {}),
            "recommended_portability": assessment.get("recommended_portability"),
            "reason": assessment.get("reason"),
        },
        "notes": "Automatic cross-model portability assessment. Production release still requires Policy / Authority Gate.",
    }
    result = record_evaluation(conn, evaluation, actor=actor)
    if result.get("error") and "UNIQUE constraint failed" in result["error"]:
        return {
            **assessment,
            "evaluation_recorded": False,
            "reason_detail": "same probe set already assessed",
            "production_skill_modified": False,
        }
    if result.get("error"):
        return {"error": result["error"], "stage": "record_evaluation"}
    return {
        **assessment,
        "eval_id": result["eval_id"],
        "evaluation_recorded": True,
        "production_skill_modified": False,
    }
