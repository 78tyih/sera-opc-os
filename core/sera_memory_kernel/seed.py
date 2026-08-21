"""Sera Memory Kernel V0 — TradeSpan 种子数据.
Spec v2: 只保留 TradeSpan 真实场景，删除 Niuniu AI 编造数据.
所有 seed 必须过 Staging Gate.

Usage: python3 -m core.sera_memory_kernel.seed
"""

from core.sera_memory_kernel import init_db, object_store, relate, stats
from core.sera_memory_kernel.kernel import _get_conn


def seed(conn=None):
    if conn is None:
        conn = _get_conn()
    init_db(conn)

    # Idempotent
    existing = conn.execute(
        "SELECT COUNT(*) FROM objects WHERE id = 'project.tradespan'"
    ).fetchone()[0]
    if existing > 0:
        print("[seed] Database already seeded, skipping.")
        return stats(conn)

    # --- 对象 ---
    # project
    object_store(conn, "project.tradespan", "Project",
                 "TradeSpan — 交易图表分析平台",
                 "structured", "organization", "founder", "active",
                 importance=0.9, confidence=1.0,
                 properties={"description": "交易图表分析平台", "priority": "high"},
                 actor="founder")

    # decisions
    object_store(conn, "decision.tradespan.dark-ui", "Decision",
                 "官网用深色 UI",
                 "structured", "project", "founder", "active",
                 importance=0.85, confidence=1.0,
                 properties={"decision": "官网用深色 UI",
                             "reason": "增强交易者信任感，符合金融科技品牌调性",
                             "constraints": ["主黑 #05070A", "主题蓝 #146EFF", "避免大面积渐变"]},
                 actor="founder")

    object_store(conn, "decision.tradespan.trust-first", "Decision",
                 "落地页信任元素优先于转化元素",
                 "structured", "project", "founder", "active",
                 importance=0.85, confidence=1.0,
                 properties={"decision": "落地页信任元素优先于转化元素",
                             "reason": "交易平台用户决策周期长，信任是转化的前提"},
                 actor="founder")

    # rules
    object_store(conn, "rule.financial.trust-first", "Rule",
                 "金融产品可信度 > 炫技，必须展示真实数据/UI",
                 "rule", "organization", "founder", "active",
                 importance=1.0, confidence=1.0,
                 properties={"content": "金融产品可信度 > 炫技，必须展示真实数据/UI",
                             "applies_to": ["landing", "video", "demo"]},
                 actor="founder")

    # experiences
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

    # tasks
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

    # --- 关系 ---
    # Decisions → Project
    for dec_id in ["decision.tradespan.dark-ui", "decision.tradespan.trust-first"]:
        relate(conn, dec_id, "project.tradespan", "applies_to", 1.0)

    # Rule → Project
    relate(conn, "rule.financial.trust-first", "project.tradespan", "applies_to", 1.0)

    # Experience → Project
    relate(conn, "experience.tradespan.video-failure", "project.tradespan", "applies_to", 0.8)

    # Tasks → Project
    relate(conn, "task.tradespan.landing-page", "project.tradespan", "part_of", 1.0)
    relate(conn, "task.tradespan.demo-video", "project.tradespan", "part_of", 1.0)

    s = stats(conn)
    print(f"[seed] Seeded.  objects={s['objects']}  relations={s['relations']}  events={s['events']}")
    return s


if __name__ == "__main__":
    result = seed()
    for k, v in sorted(result.items()):
        if isinstance(v, dict):
            print(f"  {k}:")
            for sk, sv in sorted(v.items()):
                print(f"    {sk}: {sv}")
        else:
            print(f"  {k}: {v}")