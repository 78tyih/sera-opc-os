#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sera Agent Router — 规则引擎（纯 stdlib，零依赖）
输入：自然语言请求 → 输出：Agent/Skill 编排链 JSON

用法：
  python3 router.py "做一条 PropFirm.TV 视频"
  python3 router.py --list                # 列出所有路由
  python3 router.py --test                # 运行内置自测用例
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


# 内置自测用例
TESTS = [
    ("做一条 PropFirm.TV 视频", "video-produce"),
    ("生成官网素材 B-roll", "video-produce"),
    ("推送今天的 PropFirm 优惠", "propfirm-intel"),
    ("分析一下 topstep 的规则", "propfirm-intel"),
    ("设计一个品牌海报", "design-produce"),
    ("帮我做 TradeSpan 产品发布页", "page-product-launch"),
    ("复盘这周的交易", "trading-research"),
    ("ATAS 订单流怎么解读", "trading-research"),
    ("这个客户跟进一下", "otc-bd"),
    ("把报告归档到 Obsidian", "knowledge-ops"),
    ("让 serawin 渲染", "compute"),
    ("今天天气怎么样", "fallback"),
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
    # 普通输入
    query = " ".join(args)
    if query == "-":
        query = sys.stdin.read().strip()
    res = route(query)
    print(json.dumps(res, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
