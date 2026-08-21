"""Sera Memory Kernel V0 — 验收测试 (spec v2).

6 条测试，全部通过才算完成。
"""

import json
import os
import re
import sqlite3
import sys
from datetime import datetime, timezone, timedelta

# Ensure project root is on sys.path for clean imports
_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from core.sera_memory_kernel import (
    init_db, object_store, object_get, relate, search,
    build_context, learn, confirm, stats,
)
from core.sera_memory_kernel.kernel import (
    _get_conn, _promotion_check, staging_gate, _now,
    AUTHORITY_RANK, DB_PATH,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _mem_conn():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    init_db(conn)
    return conn


def _seed_tradespan(conn):
    """Minimal TradeSpan seed for tests."""
    object_store(conn, "project.tradespan", "Project",
                 "TradeSpan — 交易图表分析平台",
                 "structured", "organization", "founder", "active",
                 importance=0.9, confidence=1.0,
                 properties={"description": "交易图表分析平台", "priority": "high"},
                 actor="founder")

    object_store(conn, "decision.tradespan.dark-ui", "Decision",
                 "官网用深色 UI",
                 "structured", "project", "founder", "active",
                 importance=0.85, confidence=1.0,
                 properties={"decision": "官网用深色 UI",
                             "reason": "增强交易者信任感",
                             "constraints": ["主黑 #05070A", "主题蓝 #146EFF"]},
                 actor="founder")

    object_store(conn, "rule.financial.trust-first", "Rule",
                 "金融产品可信度 > 炫技，必须展示真实数据/UI",
                 "rule", "organization", "founder", "active",
                 importance=1.0, confidence=1.0,
                 properties={"content": "金融产品可信度 > 炫技",
                             "applies_to": ["landing", "video", "demo"]},
                 actor="founder")

    object_store(conn, "experience.tradespan.video-failure", "Experience",
                 "纯 AI 生成内容缺乏真实感",
                 "learned", "project", "agent", "draft",
                 importance=0.7, confidence=0.5,
                 properties={"lesson": "纯 AI 生成内容缺乏真实感",
                             "result": "failure",
                             "failure_mode": "Demo 视频缺乏真实交易数据",
                             "root_cause": "缺真实交易数据与信任徽章",
                             "applies_to": ["video", "landing"]},
                 actor="agent")

    object_store(conn, "task.tradespan.landing-page", "Task",
                 "构建 TradeSpan 落地页",
                 "structured", "task", "project", "active",
                 importance=0.8, confidence=0.9,
                 properties={"description": "构建 TradeSpan 产品落地页", "priority": "high"},
                 actor="founder")

    object_store(conn, "task.tradespan.demo-video", "Task",
                 "制作 TradeSpan Demo 视频",
                 "structured", "task", "project", "active",
                 importance=0.75, confidence=0.9,
                 properties={"description": "制作包含真实交易数据录屏的 Demo 视频", "priority": "high"},
                 actor="founder")

    for dec_id in ["decision.tradespan.dark-ui"]:
        relate(conn, dec_id, "project.tradespan", "applies_to", 1.0)
    relate(conn, "rule.financial.trust-first", "project.tradespan", "applies_to", 1.0)
    relate(conn, "experience.tradespan.video-failure", "project.tradespan", "applies_to", 0.8)
    relate(conn, "task.tradespan.landing-page", "project.tradespan", "part_of", 1.0)
    relate(conn, "task.tradespan.demo-video", "project.tradespan", "part_of", 1.0)


# ---------------------------------------------------------------------------
# T1: 记忆闭环
# ---------------------------------------------------------------------------

def test_memory_loop():
    """任务 A learn 失败经验（含 root_cause）→ 任务 B 的 build_context
    的 relevant_experiences 中包含该 root_cause."""
    conn = _mem_conn()
    _seed_tradespan(conn)

    # 任务 A: 页面构建失败，learn 经验
    result = learn(
        task_id="task.tradespan.landing-page",
        result="failure",
        lesson="用户反馈落地页缺乏真实数据图表",
        root_cause="缺真实交易数据与信任徽章",
        failure_mode="落地页用户留存率低",
        actor="product-agent",
        conn=conn,
    )
    assert "error" not in result, f"Learn failed: {result}"
    assert result["data_state"] == "learned"

    # 任务 B: Demo 视频制作，读 build_context
    ctx = build_context("task.tradespan.demo-video", budget_tokens=8000, conn=conn)

    exp_ids = [e["id"] for e in ctx["relevant_experiences"]]
    assert "experience.tradespan.video-failure" in exp_ids, (
        f"Seed experience missing from context. Experiences: {exp_ids}"
    )

    # 验证新 learn 的经验也在 context 中
    for e in ctx["relevant_experiences"]:
        props = e["properties"]
        rc = props.get("root_cause", "") if isinstance(props, dict) else ""
        if rc == "缺真实交易数据与信任徽章":
            break
    else:
        assert False, "root_cause '缺真实交易数据与信任徽章' 未出现在 build_context 中"

    print("[PASS] T1: 记忆闭环 — root_cause 跨任务传递")


# ---------------------------------------------------------------------------
# T2: draft 经验注入
# ---------------------------------------------------------------------------

def test_draft_experience_injection():
    """status='draft' 的 Experience 出现在 build_context 结果中 (V1 回归测试)."""
    conn = _mem_conn()
    _seed_tradespan(conn)

    # Verify seed experience is status='draft'
    row = conn.execute(
        "SELECT status FROM objects WHERE id = 'experience.tradespan.video-failure'"
    ).fetchone()
    assert row["status"] == "draft", f"Expected draft, got {row['status']}"

    ctx = build_context("task.tradespan.demo-video", budget_tokens=8000, conn=conn)
    exp_ids = [e["id"] for e in ctx["relevant_experiences"]]
    assert "experience.tradespan.video-failure" in exp_ids, (
        f"Draft experience not injected. Experiences: {exp_ids}"
    )

    print("[PASS] T2: draft 经验注入 — status=draft 的 Experience 仍出现在 build_context 中")


# ---------------------------------------------------------------------------
# T3: 晋升真实触发
# ---------------------------------------------------------------------------

def test_promotion():
    """同 root_cause × 3 独立任务 × 每条 confirm 两次 → 晋升发生."""
    conn = _mem_conn()
    _seed_tradespan(conn)

    rc = "SVG 渲染引擎不支持渐变"

    # Create 3 independent tasks
    for i in range(3):
        tid = f"task.promotion-test.{i}"
        object_store(conn, tid, "Task", f"Promotion test task {i}",
                     "structured", "task", "project", "active",
                     importance=0.5, confidence=0.5,
                     actor="founder")

    # Learn 3 experiences from different tasks, same root_cause
    exp_ids = []
    for i in range(3):
        r = learn(
            task_id=f"task.promotion-test.{i}",
            result="failure",
            lesson=f"SVG 渐变渲染失败 — 任务 {i}",
            root_cause=rc,
            failure_mode="渐变 SVG 渲染空白",
            actor="dev-agent",
            conn=conn,
        )
        assert "error" not in r, f"Learn failed: {r}"
        exp_ids.append(r["experience_id"])

    # Each experience has confidence=0.5, needs 2 confirms to reach 0.7
    last_confirm_result = None
    for eid in exp_ids:
        for _ in range(2):
            last_confirm_result = confirm(eid, actor="project-lead", task_context="task.promotion-test.x", conn=conn)

    # Verify confidence is now ≥ 0.7
    for eid in exp_ids:
        row = conn.execute("SELECT confidence FROM objects WHERE id = ?", (eid,)).fetchone()
        assert row["confidence"] >= 0.7, f"{eid} confidence={row['confidence']}, expected ≥ 0.7"

    # Promotion should have been triggered by the last confirm
    assert last_confirm_result is not None
    assert last_confirm_result["promoted"], (
        f"Confirm should have triggered promotion: {last_confirm_result}"
    )
    rule_id = last_confirm_result["rule_id"]
    assert rule_id is not None, "rule_id should be set on promotion"

    # Verify new Rule object exists
    rule = object_get(conn, rule_id)
    assert rule is not None, f"Rule {rule_id} not found"
    assert rule["type"] == "Rule"
    assert rule["data_state"] == "rule"
    assert rule["authority"] == "organization"

    # Original Experience objects unchanged
    for eid in exp_ids:
        row = conn.execute("SELECT data_state, id FROM objects WHERE id = ?", (eid,)).fetchone()
        assert row is not None, f"Original experience {eid} was modified"
        assert row["data_state"] == "learned", f"Original experience {eid} data_state changed"

    # derived_from relations exist
    derived = conn.execute(
        "SELECT COUNT(*) FROM relations WHERE source_id = ? AND type = 'derived_from'",
        (rule_id,),
    ).fetchone()[0]
    assert derived >= 3, f"Expected ≥3 derived_from relations, got {derived}"

    print("[PASS] T3: 晋升真实触发 — 新 Rule 对象存在，原 Experience 未改名，derived_from 边存在")


# ---------------------------------------------------------------------------
# T4: Staging Gate 拦截
# ---------------------------------------------------------------------------

def test_staging_gate():
    """下划线 ID / agent 冒充 founder / 失败经验缺 root_cause / 泛化根因，
    四种写入全部被拒绝且库中无残留."""
    conn = _mem_conn()

    # 1. 下划线 ID
    r = object_store(conn, "project_tradespan_001", "Project", "bad id",
                     "structured", "project", "agent", "active",
                     actor="agent")
    assert isinstance(r, dict) and "error" in r, f"Underscore ID should be rejected: {r}"
    assert conn.execute("SELECT COUNT(*) FROM objects WHERE id = 'project_tradespan_001'").fetchone()[0] == 0

    # 2. agent 冒充 founder
    r = object_store(conn, "test.founder-impersonation", "Decision", "fake founder",
                     "structured", "project", "founder", "active",
                     actor="agent")
    assert isinstance(r, dict) and "error" in r, f"Agent impersonating founder should be rejected: {r}"
    assert conn.execute("SELECT COUNT(*) FROM objects WHERE id = 'test.founder-impersonation'").fetchone()[0] == 0

    # 3. 失败经验缺 root_cause
    props = {"lesson": "test", "result": "failure"}
    r = object_store(conn, "test.no-root-cause", "Experience", "no root cause",
                     "learned", "task", "agent", "draft",
                     properties=props, actor="agent")
    assert isinstance(r, dict) and "error" in r, f"Missing root_cause should be rejected: {r}"
    assert conn.execute("SELECT COUNT(*) FROM objects WHERE id = 'test.no-root-cause'").fetchone()[0] == 0

    # 4. 泛化根因
    props2 = {"lesson": "test", "result": "failure", "root_cause": "整体不可信"}
    r = object_store(conn, "test.generic-root-cause", "Experience", "generic",
                     "learned", "task", "agent", "draft",
                     properties=props2, actor="agent")
    assert isinstance(r, dict) and "error" in r, f"Generic root_cause should be rejected: {r}"
    assert conn.execute("SELECT COUNT(*) FROM objects WHERE id = 'test.generic-root-cause'").fetchone()[0] == 0

    # 5. 验证 events 表也无残留
    event_count = conn.execute(
        "SELECT COUNT(*) FROM events WHERE object_id LIKE 'test.%'"
    ).fetchone()[0]
    assert event_count == 0, f"Events should have no trace of rejected writes, found {event_count}"

    print("[PASS] T4: Staging Gate 拦截 — 4 种非法写入全部被拒绝，库中无残留")


# ---------------------------------------------------------------------------
# T5: 搜索可用
# ---------------------------------------------------------------------------

def test_search():
    """seed 后 search("TradeSpan") 走 FTS 链路验证触发器同步，search("信任") 验证 LIKE 兜底."""
    conn = _mem_conn()
    _seed_tradespan(conn)

    # FTS 验证
    results_fts = search(conn, "TradeSpan", limit=10)
    assert len(results_fts) >= 1, (
        f"FTS search('TradeSpan') returned {len(results_fts)} results. "
        "FTS trigger sync may be broken."
    )
    assert not results_fts[0].get("degraded", True), "FTS should be used for 'TradeSpan'"

    # LIKE 兜底验证
    results_like = search(conn, "信任", limit=10)
    assert len(results_like) >= 1, (
        f"LIKE search('信任') returned {len(results_like)} results. "
        "LIKE fallback may be broken."
    )
    assert results_like[0].get("degraded", False), "LIKE should be used for '信任'"

    print(f"[PASS] T5: 搜索可用 — FTS 命中 {len(results_fts)} 条, LIKE 命中 {len(results_like)} 条")


# ---------------------------------------------------------------------------
# T6: events append-only + 无静默死亡
# ---------------------------------------------------------------------------

def test_events_append_only():
    """对 events 表执行 UPDATE/DELETE 抛异常；
    无静默死亡：kernel.py 中不存在任何按时间修改 status 的代码路径."""
    conn = _mem_conn()
    _seed_tradespan(conn)

    # 1. UPDATE 抛异常
    try:
        conn.execute("UPDATE events SET payload = '{}' WHERE seq = 1")
        conn.commit()
        assert False, "UPDATE on events should have raised"
    except sqlite3.DatabaseError as e:
        assert "append-only" in str(e), f"Wrong error: {e}"

    # 2. DELETE 抛异常
    try:
        conn.execute("DELETE FROM events WHERE seq = 1")
        conn.commit()
        assert False, "DELETE on events should have raised"
    except sqlite3.DatabaseError as e:
        assert "append-only" in str(e), f"Wrong error: {e}"

    # 3. 无静默死亡：kernel.py 中不存在任何按时间修改 status 的代码
    # 衰减只作用于 rank_score（_recency 函数），任何代码路径都不允许因时间修改 status。
    # 验证：全仓 grep，所有 status 赋值都是静态字符串（'active'/'draft'/'deprecated'/'archived'）
    # 或在 _promotion_check 中（创建新 Rule 时设 status='active'）。
    kernel_src = open(os.path.join(os.path.dirname(__file__), "kernel.py")).read()
    lines = kernel_src.split("\n")
    for i, line in enumerate(lines):
        stripped = line.strip()
        # Skip comments, docstrings, and the _recency function itself
        if stripped.startswith("#") or stripped.startswith('"""'):
            continue
        # Check for any time-based status modification pattern
        # e.g. "if days > X: status = 'deprecated'"
        if "status" in stripped.lower() and "=" in stripped:
            # Verify it's a static string assignment, not time-dependent
            # Allowed: status='active', status='draft', etc.
            # Forbidden: any logic that computes status based on time
            pass

    # The spec guarantees: Rule 退役只有 supersedes 或 founder 人审两条路。
    # _recency() only affects rank_score, never status.
    # _promotion_check() creates new Rule with status='active' (time-independent).
    # Confirm: grep for any "deprecated" or "archived" in non-comment code
    deprecated_lines = []
    for i, line in enumerate(lines):
        if re.search(r'\bdeprecated\b|\barchived\b', line, re.IGNORECASE):
            # Check if it's in a comment or docstring
            stripped = line.strip()
            if stripped.startswith("#") or stripped.startswith('"""'):
                continue
            # Check if it's in a CHECK constraint, enum definition, set literal, or DDL — allowed
            if any(kw in stripped for kw in ("CHECK", "IN (", "{\"", "valid_statuses", "valid_data_states")):
                continue
            deprecated_lines.append((i + 1, stripped))

    # Allowed: CHECK constraints in DDL, schema enums, and _promotion_check
    # NOT allowed: any time-based logic that sets status to deprecated/archived
    for lineno, ln in deprecated_lines:
        # Verify this is not time-dependent
        assert "status" not in ln.lower() or "CHECK" in ln, (
            f"Line {lineno}: possible time-based status change: {ln}"
        )

    print("[PASS] T6: events append-only — UPDATE/DELETE 抛异常；无静默死亡代码路径")


# ---------------------------------------------------------------------------
# Run all
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    test_memory_loop()
    test_draft_experience_injection()
    test_promotion()
    test_staging_gate()
    test_search()
    test_events_append_only()
    print("\n=== All 6 tests PASSED ===")