#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sera Agent Router — 规则引擎（纯 stdlib，零依赖）
输入：自然语言请求 → 输出：Agent/Skill 编排链 JSON

V1.1 三层规划：
  Layer 1  Intent Router     意图识别（规则匹配）
  Layer 2  Agent Planner     Agent 选择（单 Agent 或 multi 编排）
  Layer 3  Execution Planner 分步执行计划（EXECUTION_STEPS 模板）

用法：
  python3 router.py "做一条 PropFirm.TV 视频"   # 单层路由（兼容）
  python3 router.py --plan "帮我做 TradeSpan 产品发布页"  # 三层规划
  python3 router.py --list                      # 列出所有路由
  python3 router.py --test                      # 单层自测
  python3 router.py --plan-test                 # 三层自测
  echo "帮我复盘这周交易" | python3 router.py -

路由规则：routes.yaml（同目录），关键词任一命中即匹配，优先级从上到下。
"""
import json
import os
import re
import sys

try:
    import yaml  # type: ignore
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

ROUTES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "routes.yaml")


def load_routes(path=ROUTES_PATH):
    """加载路由规则。优先 yaml，失败则回退内置规则。"""
    if HAS_YAML and os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return data.get("routes", [])
    return _builtin_routes()


def _builtin_routes():
    """内置兜底路由（无 PyYAML 时使用，保持核心能力可用）。"""
    return [
        {"id": "compute", "intent": "远程算力", "agent": "core",
         "keywords": ["serawin", "远程", "windows", "comfyui", "ollama", "gpu", "台式机", "渲染服务器"],
         "pipeline": ["sera-compute-control"],
         "finalize": []},

        {"id": "grill-clarify", "intent": "目标/范围/决策澄清", "agent": "core",
         "keywords": ["grill me", "grillme", "greenme", "sera_grill", "盘问我", "追问我", "帮我想清楚",
                      "需求澄清", "目标澄清", "范围澄清", "需求不清", "方向不清", "新架构", "架构方案",
                      "技术选型", "复杂工作流", "我想做一个"],
         "pipeline": ["sera-grill"],
         "finalize": []},

        {"id": "video-produce", "intent": "视频/素材生产", "agent": "video-agent",
         "keywords": ["视频", "短视频", "口播", "数字人", "合成", "渲染", "B-roll", "素材"],
         "pipeline": ["sera-content-factory", "sera-video-pipeline", "sera-asset-manager", "sera-compute-control"],
         "finalize": ["sera-knowledge-sync"]},
        {"id": "page-product-launch", "intent": "产品发布页（多 Agent）", "agent": "multi",
         "keywords": ["发布页", "产品页", "落地页", "landing page", "网站", "官网"],
         "pipeline": ["propfirm-agent:sera-content-factory", "design-agent:sera-design-studio",
                      "video-agent:sera-video-pipeline", "figma-review"],
         "finalize": ["sera-knowledge-sync"]},
        {"id": "propfirm-intel", "intent": "PropFirm 情报/竞品", "agent": "propfirm-agent",
         "keywords": ["propfirm", "考试盘", "竞品", "情报", "优惠", "规则", "规则更新", "出金", "推送", "官网拆解",
                      "topstep", "tradeify", "fundednext", "tradeday", "apex", "lucid"],
         "pipeline": ["sera-intelligence-monitor", "sera-browser-automation", "sera-content-factory"],
         "finalize": ["sera-knowledge-sync"]},
        {"id": "design-produce", "intent": "设计/品牌/UI/海报", "agent": "design-agent",
         "keywords": ["设计", "海报", "品牌", "logo", "界面", "UI", "设计稿", "规范"],
         "pipeline": ["sera-design-studio", "figma-review"],
         "finalize": ["sera-knowledge-sync"]},
        {"id": "trading-research", "intent": "交易研究/复盘", "agent": "trading-agent",
         "keywords": ["复盘", "交易", "策略", "回测", "ATAS", "订单流", "胜率", "盈亏比", "市场结构"],
         "pipeline": ["trading-analysis", "sera-finance-suite", "sera-knowledge-reader"],
         "finalize": ["sera-knowledge-sync"]},
        {"id": "otc-bd", "intent": "OTC 商务/客户", "agent": "otc-agent",
         "keywords": ["客户", "报价", "跟进", "OTC", "商务", "风控", "资信", "回复"],
         "pipeline": ["sera-crm-adapter", "sera-mail-hub", "sera-memory-system"],
         "finalize": ["sera-knowledge-sync"]},
        {"id": "knowledge-ops", "intent": "知识/记忆/归档", "agent": "core",
         "keywords": ["归档", "同步", "知识库", "记录", "记忆", "上下文", "交接", "状态", "上次"],
         "pipeline": ["sera-context-system", "sera-state-manager", "sera-knowledge-sync"],
         "finalize": []},
        {"id": "product-init", "intent": "产品发布/项目初始化", "agent": "product-agent",
         "keywords": ["产品发布", "推广", "推广产品", "新产品", "项目初始化", "产品分析", "产品手册", "产品定位", "product launch", "启动项目"],
         "pipeline": ["sera-grill", "sera-project-profile", "sera-product-analysis", "sera-market-research",
                      "sera-user-persona", "sera-positioning", "sera-copywriting", "sera-product-manual"],
         "finalize": ["sera-knowledge-sync", "sera-context-system"]},
        {"id": "ceo-decision", "intent": "CEO 决策", "agent": "sera-ceo-agent",
         "keywords": ["评估项目", "值不值得做", "商业机会", "要不要做", "项目决策", "ceo", "战略决策"],
         "pipeline": ["sera-decision-framework", "sera-priority-engine"],
         "finalize": ["sera-knowledge-sync"]},
        {"id": "fallback", "intent": "未匹配", "agent": "sera-agent-orchestrator",
         "keywords": [],
         "pipeline": ["sera-agent-orchestrator"],
         "finalize": []},
    ]


def normalize(text):
    """归一化：小写 + 去标点 + 压缩空白。"""
    text = text.lower()
    text = re.sub(r"[\s\W_]+", " ", text, flags=re.UNICODE)
    return text.strip()


def route(text, routes=None):
    """核心路由：自然语言 → 编排链。

    返回：
      {
        "matched": bool,
        "route": {"id","intent","agent"},
        "pipeline": [...],
        "finalize": [...],
        "query": 原始输入,
      }
    """
    routes = routes or load_routes()
    norm = normalize(text)
    for r in routes:
        for kw in r.get("keywords", []):
            if kw and kw.lower() in norm:
                return {
                    "matched": True,
                    "route": {"id": r["id"], "intent": r["intent"], "agent": r["agent"]},
                    "pipeline": r.get("pipeline", []),
                    "finalize": r.get("finalize", []),
                    "query": text,
                }
    # 未匹配 → fallback
    fallback = next((r for r in routes if r.get("id") == "fallback"), None)
    if fallback:
        return {
            "matched": False,
            "route": {"id": fallback["id"], "intent": fallback["intent"], "agent": fallback["agent"]},
            "pipeline": fallback.get("pipeline", []),
            "finalize": fallback.get("finalize", []),
            "query": text,
        }
    return {"matched": False, "route": {}, "pipeline": [], "finalize": [], "query": text}


# ============ V1.1: 三层规划（Intent → Agent Planner → Execution Planner） ============

# 执行步骤模板：为多 Agent 复合任务生成分步执行计划
# pipeline 中 "agent:skill" 形式 → 归属指定 Agent 的 Skill
EXECUTION_STEPS = {
    "page-product-launch": [
        {"step": 1, "task": "Research",        "skill": "propfirm-agent:sera-content-factory", "desc": "产品事实/素材收集"},
        {"step": 2, "task": "Brand",           "skill": "design-agent:sera-design-studio",      "desc": "品牌/视觉规范"},
        {"step": 3, "task": "Landing Page",    "skill": "design-agent:sera-design-studio",      "desc": "页面设计实现"},
        {"step": 4, "task": "Video",           "skill": "video-agent:sera-video-pipeline",      "desc": "页面内嵌内容"},
        {"step": 5, "task": "Publish",         "skill": "figma-review",                         "desc": "审查 + 发布"},
    ],
    "video-produce": [
        {"step": 1, "task": "Content",         "skill": "sera-content-factory",   "desc": "官网素材/事实"},
        {"step": 2, "task": "Compose",         "skill": "sera-video-pipeline",    "desc": "图卡/字幕/BGM 合成"},
        {"step": 3, "task": "Render",          "skill": "sera-compute-control",   "desc": "远程渲染（可选）"},
        {"step": 4, "task": "Archive",         "skill": "sera-asset-manager",     "desc": "入库 Eagle"},
    ],
    "trading-research": [
        {"step": 1, "task": "Analyze",         "skill": "trading-analysis",       "desc": "复盘/统计"},
        {"step": 2, "task": "Research",        "skill": "sera-finance-suite",     "desc": "行情/数据辅助"},
        {"step": 3, "task": "Report",          "skill": "sera-knowledge-sync",    "desc": "报告归档"},
    ],
    "otc-bd": [
        {"step": 1, "task": "Profile",         "skill": "sera-crm-adapter",       "desc": "客户画像"},
        {"step": 2, "task": "Outreach",        "skill": "sera-mail-hub",          "desc": "沟通/回复"},
        {"step": 3, "task": "Record",          "skill": "sera-knowledge-sync",    "desc": "归档"},
    ],
}


def intent_router(text, routes=None):
    """Layer 1 — Intent Router：识别意图（规则匹配，与 route() 同源）。"""
    res = route(text, routes)
    return {"intent": res["route"].get("intent", "未匹配"),
            "route_id": res["route"].get("id", "fallback"),
            "matched": res["matched"]}


def agent_planner(text, routes=None):
    """Layer 2 — Agent Planner：选择主 Agent（或 multi 编排）。"""
    res = route(text, routes)
    return {"agent": res["route"].get("agent", "sera-agent-orchestrator"),
            "pipeline": res.get("pipeline", []),
            "finalize": res.get("finalize", [])}


def execution_planner(text, routes=None):
    """Layer 3 — Execution Planner：生成分步执行计划。

    复合任务（有 EXECUTION_STEPS 模板）→ 结构化分步计划；
    单 Agent 任务 → 按 pipeline 顺序列出。
    """
    res = route(text, routes)
    rid = res["route"].get("id", "fallback")
    steps = EXECUTION_STEPS.get(rid)
    if steps:
        return {"plan": steps, "route_id": rid, "finalize": res.get("finalize", [])}
    # 单 Agent：把 pipeline 转成 step 列表
    steps = [{"step": i + 1, "task": s.split(":")[-1], "skill": s, "desc": ""}
             for i, s in enumerate(res.get("pipeline", []))]
    return {"plan": steps, "route_id": rid, "finalize": res.get("finalize", [])}


def plan(text, routes=None):
    """V1.1 三层规划入口：返回完整三层结果。"""
    return {
        "query": text,
        "layer1_intent": intent_router(text, routes),
        "layer2_agent": agent_planner(text, routes),
        "layer3_execution": execution_planner(text, routes),
    }


# 内置自测用例
TESTS = [
    ("grill me，先帮我把需求想清楚", "grill-clarify"),
    ("帮我想清楚这个技术选型", "grill-clarify"),
    ("做一条 PropFirm.TV 视频", "video-produce"),
    ("生成官网素材 B-roll", "video-produce"),
    ("推送今天的 PropFirm 优惠", "propfirm-intel"),
    ("分析一下 topstep 的规则", "propfirm-intel"),
    ("设计一个品牌海报", "design-produce"),
    ("帮我做 TradeSpan 产品发布页", "product-init"),
    ("复盘这周的交易", "trading-research"),
    ("ATAS 订单流怎么解读", "trading-research"),
    ("这个客户跟进一下", "otc-bd"),
    ("把报告归档到 Obsidian", "knowledge-ops"),
    ("让 serawin 渲染", "compute"),
    ("今天天气怎么样", "fallback"),

    # CEO Agent
    ("评估这个项目值不值得做", "ceo-decision"),
    ("帮我评估商业机会", "ceo-decision"),
]


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return
    if args[0] == "--list":
        for r in load_routes():
            print(f"  {r['id']:24s} {r['intent']:20s} agent={r.get('agent','')}")
        return
    if args[0] == "--test":
        ok = 0
        for query, expected in TESTS:
            res = route(query)
            rid = res["route"].get("id", "")
            mark = "✓" if rid == expected else "✗"
            if rid == expected:
                ok += 1
            print(f"  {mark} [{rid:24s}] {query}")
        print(f"\n通过 {ok}/{len(TESTS)}")
        return
    if args[0] == "--plan":
        # V1.1 三层规划
        query = " ".join(args[1:]) or sys.stdin.read().strip()
        print(json.dumps(plan(query), ensure_ascii=False, indent=2))
        return
    if args[0] == "--plan-test":
        # 三层规划自测：复合任务应生成分步计划
        ok = 0
        for query, expected in TESTS:
            p = plan(query)
            l1 = p["layer1_intent"]["route_id"]
            steps = p["layer3_execution"].get("plan", [])
            valid = l1 == expected and len(steps) >= 1
            mark = "✓" if valid else "✗"
            if valid:
                ok += 1
            print(f"  {mark} [{l1:24s}] {query} → {len(steps)} steps")
        print(f"\n通过 {ok}/{len(TESTS)}")
        return
    # 普通输入
    query = " ".join(args)
    if query == "-":
        query = sys.stdin.read().strip()
    res = route(query)
    print(json.dumps(res, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
