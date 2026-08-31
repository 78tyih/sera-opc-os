"""Shadow Skill patch generation for Sera Learning OS.

A Shadow Patch is a candidate SKILL.md materialization plus unified diff. It is stored
for evaluation only and MUST NOT overwrite the production Skill. Candidate generation
is deterministic from a proposal + baseline content unless an external governed patch
producer explicitly supplies candidate_content.
"""

from __future__ import annotations

import difflib
import hashlib
import json
import re
import sqlite3
from datetime import datetime, timezone
from typing import Optional

from .learning import init_learning_schema


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def init_shadow_patch_schema(conn: sqlite3.Connection) -> sqlite3.Connection:
    init_learning_schema(conn)
    conn.executescript(
        """
CREATE TABLE IF NOT EXISTS skill_shadow_patches(
    patch_id TEXT PRIMARY KEY,
    proposal_id TEXT NOT NULL,
    skill_path TEXT NOT NULL,
    baseline_version TEXT NOT NULL,
    candidate_version TEXT NOT NULL,
    baseline_sha256 TEXT NOT NULL,
    candidate_sha256 TEXT NOT NULL,
    baseline_content TEXT NOT NULL,
    candidate_content TEXT NOT NULL,
    unified_diff TEXT NOT NULL,
    generator TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN('shadow','stale','superseded')),
    metadata TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL,
    FOREIGN KEY(proposal_id) REFERENCES skill_evolution_proposals(proposal_id)
);
CREATE TRIGGER IF NOT EXISTS shadow_patch_no_update BEFORE UPDATE ON skill_shadow_patches
BEGIN SELECT RAISE(ABORT,'skill_shadow_patches is append-only'); END;
CREATE TRIGGER IF NOT EXISTS shadow_patch_no_delete BEFORE DELETE ON skill_shadow_patches
BEGIN SELECT RAISE(ABORT,'skill_shadow_patches is append-only'); END;
"""
    )
    conn.commit()
    return conn


def _proposal(conn: sqlite3.Connection, proposal_id: str) -> Optional[dict]:
    init_shadow_patch_schema(conn)
    row = conn.execute("SELECT * FROM skill_evolution_proposals WHERE proposal_id=?", (proposal_id,)).fetchone()
    if row is None:
        return None
    if isinstance(row, sqlite3.Row):
        result = dict(row)
    else:
        columns = [d[0] for d in conn.execute("SELECT * FROM skill_evolution_proposals LIMIT 0").description]
        result = dict(zip(columns, row))
    try:
        result["body"] = json.loads(result.get("body") or "{}")
    except (TypeError, json.JSONDecodeError):
        result["body"] = {}
    return result


def _replace_frontmatter_version(content: str, version: str) -> str:
    match = re.match(r"\A---\n(.*?)\n---\n", content, re.DOTALL)
    if not match:
        return content
    frontmatter = match.group(1)
    if re.search(r"(?m)^version:\s*.*$", frontmatter):
        frontmatter = re.sub(r"(?m)^version:\s*.*$", f"version: {version}", frontmatter, count=1)
    else:
        frontmatter += f"\nversion: {version}"
    return f"---\n{frontmatter}\n---\n" + content[match.end():]


def _default_candidate(baseline_content: str, proposal: dict) -> str:
    body = proposal.get("body") or {}
    recommendation = str(body.get("recommended_changes") or "").strip()
    source_patterns = body.get("source_patterns") or []
    candidate = _replace_frontmatter_version(baseline_content, proposal["candidate_version"])
    marker = "## Learned Guardrails"
    block = (
        f"\n\n{marker}\n"
        f"- Evolution proposal: `{proposal['proposal_id']}`\n"
        f"- Source patterns: {', '.join(f'`{p}`' for p in source_patterns) if source_patterns else 'n/a'}\n"
        f"- Recommended change: {recommendation or 'No concrete recommendation supplied.'}\n"
        "- This section was generated as a shadow candidate and requires regression + authority review before release.\n"
    )
    if marker in candidate:
        candidate += (
            "\n\n### Additional Learned Constraint\n"
            f"- Proposal `{proposal['proposal_id']}`: {recommendation or 'No concrete recommendation supplied.'}\n"
        )
    else:
        candidate += block
    return candidate


def generate_shadow_patch(
    conn: sqlite3.Connection,
    *,
    proposal_id: str,
    baseline_content: str,
    candidate_content: Optional[str] = None,
    generator: str = "sera-shadow-patch-v0",
    metadata: Optional[dict] = None,
    actor: str = "shadow-patch-generator",
) -> dict:
    """Generate and persist a Shadow Patch without modifying production content."""
    proposal = _proposal(conn, proposal_id)
    if proposal is None:
        return {"error": f"proposal not found: {proposal_id}"}
    if not baseline_content.strip():
        return {"error": "baseline_content is required"}

    baseline_sha = _sha256(baseline_content)
    candidate = candidate_content if candidate_content is not None else _default_candidate(baseline_content, proposal)
    candidate_sha = _sha256(candidate)
    if candidate_sha == baseline_sha:
        return {"error": "candidate content is identical to baseline"}

    seed = f"{proposal_id}|{baseline_sha}|{candidate_sha}"
    patch_id = "PATCH.shadow." + hashlib.sha1(seed.encode("utf-8")).hexdigest()[:14]
    diff = "".join(difflib.unified_diff(
        baseline_content.splitlines(keepends=True),
        candidate.splitlines(keepends=True),
        fromfile=f"a/{proposal['skill_path']}",
        tofile=f"b/{proposal['skill_path']}",
    ))
    timestamp = _now()
    try:
        conn.execute(
            """
            INSERT INTO skill_shadow_patches(
              patch_id,proposal_id,skill_path,baseline_version,candidate_version,
              baseline_sha256,candidate_sha256,baseline_content,candidate_content,
              unified_diff,generator,status,metadata,created_at
            ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                patch_id, proposal_id, proposal["skill_path"], proposal["baseline_version"],
                proposal["candidate_version"], baseline_sha, candidate_sha, baseline_content,
                candidate, diff, generator, "shadow", json.dumps(metadata or {}, ensure_ascii=False), timestamp,
            ),
        )
        conn.execute(
            "INSERT INTO learning_events(event_type,object_id,payload,actor,at) VALUES(?,?,?,?,?)",
            ("shadow_patch_generated", patch_id, json.dumps({
                "proposal_id": proposal_id,
                "skill_path": proposal["skill_path"],
                "baseline_sha256": baseline_sha,
                "candidate_sha256": candidate_sha,
            }, ensure_ascii=False), actor, timestamp),
        )
        conn.commit()
    except sqlite3.IntegrityError as exc:
        return {"error": str(exc)}
    return {
        "patch_id": patch_id,
        "proposal_id": proposal_id,
        "skill_path": proposal["skill_path"],
        "baseline_sha256": baseline_sha,
        "candidate_sha256": candidate_sha,
        "unified_diff": diff,
        "production_skill_modified": False,
    }


def get_shadow_patch(conn: sqlite3.Connection, patch_id: str) -> Optional[dict]:
    init_shadow_patch_schema(conn)
    row = conn.execute("SELECT * FROM skill_shadow_patches WHERE patch_id=?", (patch_id,)).fetchone()
    if row is None:
        return None
    if isinstance(row, sqlite3.Row):
        result = dict(row)
    else:
        cols = [d[0] for d in conn.execute("SELECT * FROM skill_shadow_patches LIMIT 0").description]
        result = dict(zip(cols, row))
    try:
        result["metadata"] = json.loads(result.get("metadata") or "{}")
    except (TypeError, json.JSONDecodeError):
        result["metadata"] = {}
    return result


def validate_shadow_baseline(conn: sqlite3.Connection, patch_id: str, current_production_content: str) -> dict:
    """Fail closed if production changed after Shadow Patch generation."""
    patch = get_shadow_patch(conn, patch_id)
    if patch is None:
        return {"error": f"shadow patch not found: {patch_id}"}
    current_sha = _sha256(current_production_content)
    valid = current_sha == patch["baseline_sha256"]
    return {
        "patch_id": patch_id,
        "baseline_matches_current_production": valid,
        "expected_baseline_sha256": patch["baseline_sha256"],
        "current_production_sha256": current_sha,
        "release_blocked": not valid,
    }
