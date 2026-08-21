"""Sera Memory Kernel V0 — spec v2 (验收版).
stdlib + sqlite3 only.  -*- coding: utf-8 -*-
"""

import json
import os
import re
import sqlite3
from datetime import datetime, timezone
from typing import Optional

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

AUTHORITY_RANK = {"agent": 1, "project": 2, "organization": 3, "founder": 4}

HALF_LIFE_DAYS = {
    "rule": 90,
    "learned": 30,
    "structured": 14,
    "processed": 7,
    "raw": 2,
}

BUDGET_ALLOCATION = {
    "mission": 0.10,
    "active_decisions": 0.20,
    "active_rules": 0.15,
    "relevant_experiences": 0.25,
    "available_assets": 0.15,
    "relevant_skills": 0.10,
    "stale_markers": 0.05,
}

RANK_W = {"importance": 0.40, "recency": 0.25, "relation_weight": 0.20, "confidence": 0.15}

TYPE_TO_SECTION = {
    "Decision": "active_decisions",
    "Rule": "active_rules",
    "Experience": "relevant_experiences",
    "Asset": "available_assets",
    "Skill": "relevant_skills",
}

GENERIC_ROOT_CAUSE_BLACKLIST = ("整体", "不可信", "都不行")

ID_PATTERN = re.compile(r"^[a-z0-9]+(\.[a-z0-9-]+)+$")

DB_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "memory", "sera-kernel.db",
)

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _get_conn() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def _recency(accessed_at: str, data_state: str) -> float:
    """Half-life decay: 0.5^(days / half_life). 衰减只作用于 rank_score."""
    try:
        dt = datetime.fromisoformat(accessed_at)
    except (ValueError, TypeError):
        return 0.0
    days = (datetime.now(timezone.utc) - dt).days
    hl = HALF_LIFE_DAYS.get(data_state, 14)
    if hl <= 0:
        return 0.0
    return 0.5 ** (days / hl)


def _token_estimate(obj: dict) -> int:
    """启发式 token 估算：~4 chars per token."""
    return len(json.dumps(obj, ensure_ascii=False, default=str)) // 4


def _write_event(conn, event_type: str, object_id: str, payload: dict, actor: str):
    conn.execute(
        "INSERT INTO events (event_type, object_id, payload, actor, at) VALUES (?, ?, ?, ?, ?)",
        (event_type, object_id, json.dumps(payload, ensure_ascii=False), actor, _now()),
    )


def _slugify(text: str) -> str:
    """Sanitize a string for use as a rule ID slug."""
    slug = text.lower().replace(" ", "-").replace("_", "-")
    slug = re.sub(r"[^a-z0-9-]", "", slug)
    return slug[:48]


# ---------------------------------------------------------------------------
# Staging Gate
# ---------------------------------------------------------------------------

def staging_gate(obj: dict, actor: str) -> tuple:
    """Validate an object before write.  Returns (ok: bool, errors: list[str])."""
    errors = []

    # 1. ID 格式：点分隔小写
    obj_id = obj.get("id", "")
    if not obj_id:
        errors.append("id 必填")
    elif not ID_PATTERN.match(obj_id):
        errors.append(f"id 格式错误 '{obj_id}'：必须为点分隔小写")

    # 2. 必填字段
    for field in ("type", "name", "data_state", "scope"):
        if not obj.get(field):
            errors.append(f"{field} 必填")

    # 3. 枚举合法性（Gate 先拦截，给可读错误）
    valid_types = {"Person", "Project", "Task", "Decision", "Experience", "Rule", "Asset", "Skill"}
    if obj.get("type") and obj["type"] not in valid_types:
        errors.append(f"type '{obj['type']}' 非法，必须为 {sorted(valid_types)}")

    valid_data_states = {"raw", "processed", "structured", "learned", "rule"}
    if obj.get("data_state") and obj["data_state"] not in valid_data_states:
        errors.append(f"data_state '{obj['data_state']}' 非法")

    valid_scopes = {"session", "task", "project", "organization"}
    if obj.get("scope") and obj["scope"] not in valid_scopes:
        errors.append(f"scope '{obj['scope']}' 非法")

    valid_statuses = {"active", "draft", "deprecated", "archived"}
    if obj.get("status") and obj["status"] not in valid_statuses:
        errors.append(f"status '{obj['status']}' 非法")

    # 4. authority 合法性 + founder 防伪
    valid_authorities = {"agent", "project", "organization", "founder"}
    auth = obj.get("authority", "agent")
    if auth not in valid_authorities:
        errors.append(f"authority '{auth}' 非法")
    elif auth == "founder" and actor != "founder":
        errors.append(f"actor='{actor}' 不能以 founder 身份写入")

    # 5. importance / confidence 在 [0, 1]
    for field in ("importance", "confidence"):
        val = obj.get(field, 0.5)
        if not isinstance(val, (int, float)) or val < 0 or val > 1:
            errors.append(f"{field} 必须在 [0, 1] 范围内")

    # 6. Experience 专项检查
    if obj.get("type") == "Experience":
        props = obj.get("properties", {})
        if isinstance(props, str):
            try:
                props = json.loads(props)
            except (json.JSONDecodeError, TypeError):
                props = {}
        result = props.get("result") if isinstance(props, dict) else None
        root_cause = props.get("root_cause") if isinstance(props, dict) else None
        if result == "failure" and not root_cause:
            errors.append("失败经验必须提供 root_cause")
        if root_cause:
            for bad in GENERIC_ROOT_CAUSE_BLACKLIST:
                if bad in root_cause:
                    errors.append(f"拒绝泛化 root_cause: '{root_cause}'")
                    break

    return len(errors) == 0, errors


# ---------------------------------------------------------------------------
# init_db
# ---------------------------------------------------------------------------

def init_db(conn: Optional[sqlite3.Connection] = None) -> sqlite3.Connection:
    """Create schema, triggers, FTS.  Idempotent."""
    if conn is None:
        conn = _get_conn()

    conn.executescript("""
        CREATE TABLE IF NOT EXISTS objects (
          id          TEXT PRIMARY KEY,
          type        TEXT NOT NULL CHECK(type IN
                        ('Person','Project','Task','Decision','Experience','Rule','Asset','Skill')),
          name        TEXT NOT NULL,
          data_state  TEXT NOT NULL CHECK(data_state IN
                        ('raw','processed','structured','learned','rule')),
          scope       TEXT NOT NULL CHECK(scope IN
                        ('session','task','project','organization')),
          authority   TEXT NOT NULL DEFAULT 'agent' CHECK(authority IN
                        ('founder','organization','project','agent')),
          status      TEXT NOT NULL DEFAULT 'active' CHECK(status IN
                        ('active','draft','deprecated','archived')),
          importance  REAL DEFAULT 0.5 CHECK(importance BETWEEN 0 AND 1),
          confidence  REAL DEFAULT 0.5 CHECK(confidence BETWEEN 0 AND 1),
          properties  TEXT DEFAULT '{}',
          created_at  TEXT NOT NULL,
          accessed_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS relations (
          source_id TEXT NOT NULL,
          target_id TEXT NOT NULL,
          type      TEXT NOT NULL,
          weight    REAL DEFAULT 1.0,
          PRIMARY KEY (source_id, target_id, type)
        );

        CREATE TABLE IF NOT EXISTS events (
          seq        INTEGER PRIMARY KEY AUTOINCREMENT,
          event_type TEXT NOT NULL,
          object_id  TEXT NOT NULL,
          payload    TEXT NOT NULL,
          actor      TEXT NOT NULL,
          at         TEXT NOT NULL
        );

        -- events append-only 触发器
        CREATE TRIGGER IF NOT EXISTS events_no_update
        BEFORE UPDATE ON events BEGIN
          SELECT RAISE(ABORT, 'events is append-only');
        END;

        CREATE TRIGGER IF NOT EXISTS events_no_delete
        BEFORE DELETE ON events BEGIN
          SELECT RAISE(ABORT, 'events is append-only');
        END;

        -- FTS5 外部内容表
        CREATE VIRTUAL TABLE IF NOT EXISTS objects_fts USING fts5(
          id UNINDEXED, name, properties,
          content='objects', content_rowid='rowid'
        );

        -- FTS 同步触发器
        CREATE TRIGGER IF NOT EXISTS objects_fts_ai AFTER INSERT ON objects BEGIN
          INSERT INTO objects_fts(rowid, id, name, properties)
          VALUES (new.rowid, new.id, new.name, new.properties);
        END;

        CREATE TRIGGER IF NOT EXISTS objects_fts_ad AFTER DELETE ON objects BEGIN
          INSERT INTO objects_fts(objects_fts, rowid, id, name, properties)
          VALUES ('delete', old.rowid, old.id, old.name, old.properties);
        END;

        CREATE TRIGGER IF NOT EXISTS objects_fts_au AFTER UPDATE ON objects BEGIN
          INSERT INTO objects_fts(objects_fts, rowid, id, name, properties)
          VALUES ('delete', old.rowid, old.id, old.name, old.properties);
          INSERT INTO objects_fts(rowid, id, name, properties)
          VALUES (new.rowid, new.id, new.name, new.properties);
        END;
    """)
    conn.commit()
    return conn


# ---------------------------------------------------------------------------
# Basic CRUD
# ---------------------------------------------------------------------------

def object_store(
    conn: sqlite3.Connection,
    obj_id: str,
    obj_type: str,
    name: str,
    data_state: str,
    scope: str,
    authority: str = "agent",
    status: str = "active",
    importance: float = 0.5,
    confidence: float = 0.5,
    properties: Optional[dict] = None,
    actor: str = "system",
):
    """Store an object.  Staging gate first → events first → objects.

    Returns obj_id on success, or dict with 'error' key on gate rejection.
    """
    now = _now()
    props = json.dumps(properties or {}, ensure_ascii=False)

    obj = {
        "id": obj_id,
        "type": obj_type,
        "name": name,
        "data_state": data_state,
        "scope": scope,
        "authority": authority,
        "status": status,
        "importance": importance,
        "confidence": confidence,
        "properties": props,
    }

    ok, errs = staging_gate(obj, actor)
    if not ok:
        return {"error": "; ".join(errs)}

    # events first
    _write_event(conn, "create", obj_id, obj, actor)

    conn.execute(
        """INSERT OR REPLACE INTO objects
           (id, type, name, data_state, scope, authority,
            status, importance, confidence, properties, created_at, accessed_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (obj_id, obj_type, name, data_state, scope, authority,
         status, importance, confidence, props, now, now),
    )
    conn.commit()
    return obj_id


def object_get(conn: sqlite3.Connection, obj_id: str) -> Optional[dict]:
    """Get object by id.  Updates accessed_at + writes access event."""
    row = conn.execute("SELECT * FROM objects WHERE id = ?", (obj_id,)).fetchone()
    if row is None:
        return None
    now = _now()
    conn.execute("UPDATE objects SET accessed_at = ? WHERE id = ?", (now, obj_id))
    _write_event(conn, "access", obj_id, {"accessed_at": now}, "system")
    conn.commit()
    obj = dict(row)
    obj["properties"] = json.loads(obj["properties"])
    return obj


def relate(
    conn: sqlite3.Connection,
    source_id: str,
    target_id: str,
    rel_type: str,
    weight: float = 1.0,
):
    """Create a relation + write relate event.  UPSERT semantics."""
    conn.execute(
        "INSERT OR REPLACE INTO relations (source_id, target_id, type, weight) VALUES (?, ?, ?, ?)",
        (source_id, target_id, rel_type, weight),
    )
    _write_event(conn, "relate", source_id, {
        "source_id": source_id, "target_id": target_id,
        "type": rel_type, "weight": weight,
    }, "system")
    conn.commit()


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------

def search(conn: sqlite3.Connection, query: str, limit: int = 10) -> list:
    """FTS5 MATCH search.  Falls back to LIKE if FTS unavailable or returns empty."""
    degraded = False
    try:
        rows = conn.execute(
            """SELECT o.* FROM objects o
               JOIN objects_fts fts ON o.rowid = fts.rowid
               WHERE objects_fts MATCH ?
               LIMIT ?""",
            (query, limit),
        ).fetchall()
    except sqlite3.OperationalError:
        rows = []
        degraded = True

    # FTS5 may return empty for non-ASCII queries (e.g. Chinese);
    # fall back to LIKE for robustness.
    if len(rows) == 0:
        degraded = True
        rows = conn.execute(
            "SELECT * FROM objects WHERE name LIKE ? OR properties LIKE ? LIMIT ?",
            (f"%{query}%", f"%{query}%", limit),
        ).fetchall()

    result = []
    for r in rows:
        obj = dict(r)
        obj["properties"] = json.loads(obj["properties"])
        obj["degraded"] = degraded
        result.append(obj)
    return result


# ---------------------------------------------------------------------------
# build_context
# ---------------------------------------------------------------------------

def build_context(
    task_id: str,
    budget_tokens: int = 8000,
    conn: Optional[sqlite3.Connection] = None,
) -> dict:
    """Context Governor — ranked, budget-constrained context package.

    Hard constraints:
    1. Founder Rules (authority=founder, type=Rule) unconditionally injected,
       do not participate in ranking, do not consume section budgets.
    2. Remaining candidates ranked by rank_score, budgeted per section.
    3. Experience collected by data_state IN ('learned','rule'), regardless of status.
    4. Superseded objects → stale_markers only.
    5. Output includes truncated:bool + omitted_count:int.
    """
    if conn is None:
        conn = _get_conn()

    task = object_get(conn, task_id)
    if task is None:
        return {"error": f"Task {task_id} not found"}

    # Project via part_of
    proj = conn.execute(
        "SELECT target_id FROM relations WHERE source_id = ? AND type = 'part_of' LIMIT 1",
        (task_id,),
    ).fetchone()
    project_id = proj["target_id"] if proj else None

    # --- 1. Mission (fixed 10%) ---
    mission = {
        "summary": task.get("name", ""),
        "project": project_id or task_id,
        "priority": task.get("properties", {}).get("priority", "medium"),
    }
    mission_tokens = _token_estimate(mission)

    # --- 2. Collect candidates ---
    candidates = []
    seen = set()

    def _collect(target_id_val):
        rows = conn.execute(
            """SELECT r.type AS rel_type, r.weight AS rel_weight, o.*
               FROM relations r
               JOIN objects o ON r.source_id = o.id
               WHERE r.target_id = ?
                 AND (o.status = 'active'
                      OR (o.type = 'Experience' AND o.data_state IN ('learned', 'rule')))""",
            (target_id_val,),
        ).fetchall()
        for r in rows:
            d = dict(r)
            if d["id"] not in seen:
                seen.add(d["id"])
                d["properties"] = json.loads(d["properties"])
                candidates.append(d)

    if project_id:
        _collect(project_id)
    _collect(task_id)

    # --- 3. Superseded set ---
    sup_rows = conn.execute(
        "SELECT target_id FROM relations WHERE type = 'supersedes'"
    ).fetchall()
    sup_ids = {r["target_id"] for r in sup_rows}

    # --- 4. Separate founder Rules (unconditional, no ranking, no budget) ---
    founder_rules = []
    others = []
    for c in candidates:
        if c["id"] in sup_ids:
            continue
        if c["authority"] == "founder" and c["type"] == "Rule" and c["status"] == "active":
            founder_rules.append(c)
        else:
            others.append(c)

    # --- 5. Rank remaining ---
    for c in others:
        rec = _recency(c["accessed_at"], c["data_state"])
        rw = c.get("rel_weight", 0.5) or 0.5
        # authority tie-breaker: higher authority ranks higher
        auth_boost = AUTHORITY_RANK.get(c["authority"], 0) * 0.01
        c["rank_score"] = (
            RANK_W["importance"] * c["importance"]
            + RANK_W["recency"] * rec
            + RANK_W["relation_weight"] * rw
            + RANK_W["confidence"] * c["confidence"]
            + auth_boost
        )
    others.sort(key=lambda c: c["rank_score"], reverse=True)

    # --- 6. Budget allocation ---
    section_limits = {k: int(budget_tokens * v) for k, v in BUDGET_ALLOCATION.items()}
    section_used = {k: 0 for k in section_limits}

    pkg = {
        "context_id": f"ctx.{task_id}.{_now()[:10]}",
        "target_task": task_id,
        "compiled_at": _now(),
        "budget_tokens": budget_tokens,
        "used_tokens": mission_tokens,
        "truncated": False,
        "omitted_count": 0,
        "mission": mission,
        "active_decisions": [],
        "active_rules": [],
        "relevant_experiences": [],
        "available_assets": [],
        "relevant_skills": [],
        "stale_markers": [],
    }

    # Founder rules injected unconditionally, counted in used_tokens
    for fr in founder_rules:
        entry = {
            "id": fr["id"],
            "type": fr["type"],
            "name": fr["name"],
            "data_state": fr["data_state"],
            "authority": fr["authority"],
            "importance": fr["importance"],
            "confidence": fr["confidence"],
            "properties": fr["properties"],
        }
        pkg["active_rules"].append(entry)
        pkg["used_tokens"] += _token_estimate(entry)

    # Ranked candidates into sections
    omitted = 0
    for c in others:
        sec = TYPE_TO_SECTION.get(c["type"])
        if sec is None:
            continue
        entry = {
            "id": c["id"],
            "type": c["type"],
            "name": c["name"],
            "data_state": c["data_state"],
            "authority": c["authority"],
            "importance": c["importance"],
            "confidence": c["confidence"],
            "properties": c["properties"],
        }
        tok = _token_estimate(entry)
        if section_used[sec] + tok <= section_limits[sec]:
            pkg[sec].append(entry)
            section_used[sec] += tok
            pkg["used_tokens"] += tok
        else:
            omitted += 1

    # Stale markers
    stale_budget = section_limits["stale_markers"]
    stale_used = 0
    for sid in sup_ids:
        row = conn.execute("SELECT * FROM objects WHERE id = ?", (sid,)).fetchone()
        if row is None:
            continue
        superseder = conn.execute(
            "SELECT source_id FROM relations WHERE type = 'supersedes' AND target_id = ?",
            (sid,),
        ).fetchone()
        entry = {
            "id": sid,
            "reason": "已被 supersedes",
            "superseded_by": superseder["source_id"] if superseder else None,
        }
        tok = _token_estimate(entry)
        if stale_used + tok <= stale_budget:
            pkg["stale_markers"].append(entry)
            stale_used += tok
            pkg["used_tokens"] += tok

    pkg["truncated"] = omitted > 0
    pkg["omitted_count"] = omitted
    return pkg


# ---------------------------------------------------------------------------
# Promotion check (internal)
# ---------------------------------------------------------------------------

def _promotion_check(conn, root_cause: str, exclude_id: str = "") -> Optional[str]:
    """Check if an experience cluster qualifies for promotion to Rule.

    Conditions (all must be met):
    1. ≥3 independent tasks sharing the same root_cause.
    2. Each experience in the cluster has confidence ≥ 0.7.
    3. No higher or equal authority active Rule with the same root_cause exists.

    Returns rule_id on promotion, None otherwise.
    """
    rows = conn.execute(
        """SELECT * FROM objects
           WHERE type = 'Experience'
             AND data_state IN ('learned', 'rule')
             AND json_extract(properties, '$.root_cause') = ?""",
        (root_cause,),
    ).fetchall()

    # Filter to confidence ≥ 0.7
    qualified = [r for r in rows if r["confidence"] >= 0.7]

    # Count unique task contexts
    task_ids = set()
    for r in qualified:
        tr = conn.execute(
            "SELECT target_id FROM relations WHERE source_id = ? AND type = 'part_of' LIMIT 1",
            (r["id"],),
        ).fetchone()
        if tr:
            task_ids.add(tr["target_id"])
        else:
            task_ids.add(r["id"])

    if len(task_ids) < 3:
        return None

    # Check no higher/equal authority contradiction
    contradicting = conn.execute(
        """SELECT * FROM objects
           WHERE type = 'Rule' AND status = 'active'
             AND authority IN ('organization', 'founder')
             AND json_extract(properties, '$.root_cause') = ?""",
        (root_cause,),
    ).fetchone()
    if contradicting:
        return None

    # Promote: create new Rule object
    safe_slug = _slugify(root_cause)
    rule_id = f"rule.{safe_slug}"
    now = _now()
    source_ids = [r["id"] for r in qualified]

    rule_props = json.dumps({
        "root_cause": root_cause,
        "source_experiences": source_ids,
    }, ensure_ascii=False)

    conn.execute(
        """INSERT INTO objects
           (id, type, name, data_state, scope, authority,
            status, importance, confidence, properties, created_at, accessed_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (rule_id, "Rule", f"Rule: {root_cause[:60]}",
         "rule", "organization", "organization",
         "active", 0.7, 0.7,
         rule_props, now, now),
    )

    # derived_from relations
    for sid in source_ids:
        conn.execute(
            "INSERT OR IGNORE INTO relations (source_id, target_id, type, weight) VALUES (?, ?, 'derived_from', 1.0)",
            (rule_id, sid),
        )

    _write_event(conn, "promote", rule_id, {
        "root_cause": root_cause,
        "source_experiences": source_ids,
        "reason": f"≥3 independent tasks ({len(task_ids)}), all confidence ≥ 0.7",
    }, "system")

    conn.commit()
    return rule_id


# ---------------------------------------------------------------------------
# learn
# ---------------------------------------------------------------------------

def learn(
    task_id: str,
    result: str,
    lesson: str,
    failure_mode: Optional[str] = None,
    root_cause: Optional[str] = None,
    applies_to: Optional[list] = None,
    actor: str = "agent",
    conn: Optional[sqlite3.Connection] = None,
) -> dict:
    """Learn from an experience.  Staging gate → events-first → promotion check.

    Returns dict with experience_id, promoted (bool), and optional rule_id.
    """
    if conn is None:
        conn = _get_conn()

    now = _now()

    props = {"lesson": lesson, "result": result}
    if failure_mode:
        props["failure_mode"] = failure_mode
    if root_cause:
        props["root_cause"] = root_cause
    if applies_to:
        props["applies_to"] = applies_to

    exp_id = f"experience.{task_id}.{now[:10]}"

    # Gate the object
    gate_result = object_store(
        conn,
        obj_id=exp_id,
        obj_type="Experience",
        name=lesson[:80],
        data_state="learned",
        scope="task",
        authority="agent",
        status="draft",
        importance=0.5,
        confidence=0.5,
        properties=props,
        actor=actor,
    )
    if isinstance(gate_result, dict) and "error" in gate_result:
        return gate_result

    # Relate to task
    conn.execute(
        "INSERT OR IGNORE INTO relations (source_id, target_id, type, weight) VALUES (?, ?, 'part_of', 1.0)",
        (exp_id, task_id),
    )
    conn.commit()

    # Promotion check
    promoted = False
    rule_id = None
    if root_cause:
        rid = _promotion_check(conn, root_cause, exclude_id=exp_id)
        if rid:
            promoted = True
            rule_id = rid

    return {
        "experience_id": exp_id,
        "promoted": promoted,
        "rule_id": rule_id,
        "data_state": "rule" if promoted else "learned",
        "status": "active" if promoted else "draft",
    }


# ---------------------------------------------------------------------------
# confirm
# ---------------------------------------------------------------------------

def confirm(
    experience_id: str,
    actor: str,
    task_context: Optional[str] = None,
    conn: Optional[sqlite3.Connection] = None,
) -> dict:
    """Confirm an experience.  Increases confidence, triggers promotion check.

    - Normal confirm: confidence = min(current + 0.1, 0.8).
    - Founder confirm: confidence = 0.9.
    - Writes confirm event with task context.
    """
    if conn is None:
        conn = _get_conn()

    row = conn.execute("SELECT * FROM objects WHERE id = ?", (experience_id,)).fetchone()
    if row is None:
        return {"error": f"Experience {experience_id} not found"}
    if row["type"] != "Experience":
        return {"error": f"{experience_id} is not an Experience"}

    current = row["confidence"]
    if actor == "founder":
        new_conf = 0.9
    else:
        new_conf = min(current + 0.1, 0.8)

    now = _now()
    conn.execute(
        "UPDATE objects SET confidence = ?, accessed_at = ? WHERE id = ?",
        (new_conf, now, experience_id),
    )

    payload = {
        "experience_id": experience_id,
        "previous_confidence": current,
        "new_confidence": new_conf,
        "actor": actor,
    }
    if task_context:
        payload["task_context"] = task_context
    _write_event(conn, "confirm", experience_id, payload, actor)
    conn.commit()

    # Promotion check
    props = json.loads(row["properties"])
    root_cause = props.get("root_cause") if isinstance(props, dict) else None

    promoted = False
    rule_id = None
    if root_cause:
        rid = _promotion_check(conn, root_cause)
        if rid:
            promoted = True
            rule_id = rid

    return {
        "experience_id": experience_id,
        "previous_confidence": current,
        "new_confidence": new_conf,
        "promoted": promoted,
        "rule_id": rule_id,
    }


# ---------------------------------------------------------------------------
# stats
# ---------------------------------------------------------------------------

def stats(conn: Optional[sqlite3.Connection] = None) -> dict:
    if conn is None:
        conn = _get_conn()

    def _g(query):
        return {r[0]: r[1] for r in conn.execute(query).fetchall()}

    return {
        "objects": conn.execute("SELECT COUNT(*) FROM objects").fetchone()[0],
        "relations": conn.execute("SELECT COUNT(*) FROM relations").fetchone()[0],
        "events": conn.execute("SELECT COUNT(*) FROM events").fetchone()[0],
        "by_type": _g("SELECT type, COUNT(*) FROM objects GROUP BY type"),
        "by_data_state": _g("SELECT data_state, COUNT(*) FROM objects GROUP BY data_state"),
        "by_authority": _g("SELECT authority, COUNT(*) FROM objects GROUP BY authority"),
    }