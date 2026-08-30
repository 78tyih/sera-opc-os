#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sera Agent Router — natural-language intent to Agent/Skill pipeline."""
import json, os, re, sys
try:
    import yaml  # type: ignore
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

ROUTES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "routes.yaml")

def load_routes(path=ROUTES_PATH):
    if HAS_YAML and os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return data.get("routes", [])
    return _builtin_routes()

def _builtin_routes():
    return [
        {"id":"compute","intent":"远程算力","agent":"core","keywords":["serawin","远程","windows","comfyui","ollama","gpu","台式机","渲染服务器"],"pipeline":["sera-compute-control"],"finalize":[]},
        {"id":"grill-clarify","intent":"目标/范围/决策澄清","agent":"core","keywords":["grill me","grillme","greenme","sera_grill","盘问我","追问我","帮我想清楚","需求澄清","目标澄清","范围澄清","需求不清","方向不清","新架构","架构方案","技术选型","复杂工作流","我想做一个"],"pipeline":["sera-grill"],"finalize":[]},
        {"id":"creator-intelligence","intent":"Creator/频道内容研究与知识沉淀","agent":"core","keywords":["creator intelligence","creator analysis","youtube channel","youtube 知识库","youtube知识库","频道分析","分析频道","分析博主","博主分析","自媒体分析","视频总结","视频拆解","视频文字稿","文字稿","transcript","哪些视频最值得看","值得看的视频","论点论据","内容分布","内容沉淀","博主知识库","监控博主"],"pipeline":["sera-creator-intelligence"],"finalize":["sera-knowledge-sync","sera-context-system"]},
        {"id":"video-produce","intent":"视频/素材生产","agent":"video-agent","keywords":["视频","短视频","口播","数字人","合成","渲染","B-roll","素材"],"pipeline":["sera-content-factory","sera-video-pipeline","sera-asset-manager","sera-compute-control"],"finalize":["sera-knowledge-sync"]},
        {"id":"product-init","intent":"产品发布/项目初始化","agent":"product-agent","keywords":["产品发布","推广","推广产品","新产品","项目初始化","产品分析","产品手册","产品定位","product launch","启动项目"],"pipeline":["sera-grill","sera-project-profile","sera-product-analysis","sera-market-research","sera-user-persona","sera-positioning","sera-copywriting","sera-product-manual"],"finalize":["sera-knowledge-sync","sera-context-system"]},
        {"id":"page-product-launch","intent":"产品发布页（多 Agent）","agent":"multi","keywords":["发布页","产品页","落地页","landing page","网站","官网"],"pipeline":["propfirm-agent:sera-content-factory","design-agent:sera-design-studio","video-agent:sera-video-pipeline","figma-review"],"finalize":["sera-knowledge-sync"]},
        {"id":"propfirm-intel","intent":"PropFirm 情报/竞品","agent":"propfirm-agent","keywords":["propfirm","考试盘","竞品","情报","优惠","规则","规则更新","出金","推送","官网拆解","topstep","tradeify","fundednext","tradeday","apex","lucid"],"pipeline":["sera-intelligence-monitor","sera-browser-automation","sera-content-factory"],"finalize":["sera-knowledge-sync"]},
        {"id":"design-produce","intent":"设计/品牌/UI/海报","agent":"design-agent","keywords":["设计","海报","品牌","logo","界面","UI","设计稿","规范"],"pipeline":["sera-design-studio","figma-review"],"finalize":["sera-knowledge-sync"]},
        {"id":"trading-research","intent":"交易研究/复盘","agent":"trading-agent","keywords":["复盘","交易","策略","回测","ATAS","订单流","胜率","盈亏比","市场结构"],"pipeline":["trading-analysis","sera-finance-suite","sera-knowledge-reader"],"finalize":["sera-knowledge-sync"]},
        {"id":"otc-bd","intent":"OTC 商务/客户","agent":"otc-agent","keywords":["客户","报价","跟进","OTC","商务","风控","资信","回复"],"pipeline":["sera-crm-adapter","sera-mail-hub","sera-memory-system"],"finalize":["sera-knowledge-sync"]},
        {"id":"knowledge-ops","intent":"知识/记忆/归档","agent":"core","keywords":["归档","同步","知识库","记录","记忆","上下文","交接","状态","上次"],"pipeline":["sera-context-system","sera-state-manager","sera-knowledge-sync"],"finalize":[]},
        {"id":"ceo-decision","intent":"CEO 决策","agent":"sera-ceo-agent","keywords":["评估项目","值不值得做","商业机会","要不要做","项目决策","ceo","战略决策"],"pipeline":["sera-decision-framework","sera-priority-engine"],"finalize":["sera-knowledge-sync"]},
        {"id":"fallback","intent":"未匹配","agent":"sera-agent-orchestrator","keywords":[],"pipeline":["sera-agent-orchestrator"],"finalize":[]},
    ]

def normalize(text):
    return re.sub(r"[\s\W_]+", " ", text.lower(), flags=re.UNICODE).strip()

def route(text, routes=None):
    routes = routes or load_routes()
    norm = normalize(text)
    for r in routes:
        for kw in r.get("keywords", []):
            if kw and normalize(kw) in norm:
                return {"matched":True,"route":{"id":r["id"],"intent":r["intent"],"agent":r["agent"]},"pipeline":r.get("pipeline",[]),"finalize":r.get("finalize",[]),"query":text}
    fallback = next((r for r in routes if r.get("id")=="fallback"), None)
    if fallback:
        return {"matched":False,"route":{"id":fallback["id"],"intent":fallback["intent"],"agent":fallback["agent"]},"pipeline":fallback.get("pipeline",[]),"finalize":fallback.get("finalize",[]),"query":text}
    return {"matched":False,"route":{},"pipeline":[],"finalize":[],"query":text}

EXECUTION_STEPS = {
    "page-product-launch":[
        {"step":1,"task":"Research","skill":"propfirm-agent:sera-content-factory","desc":"产品事实/素材收集"},
        {"step":2,"task":"Brand","skill":"design-agent:sera-design-studio","desc":"品牌/视觉规范"},
        {"step":3,"task":"Landing Page","skill":"design-agent:sera-design-studio","desc":"页面设计实现"},
        {"step":4,"task":"Video","skill":"video-agent:sera-video-pipeline","desc":"页面内嵌内容"},
        {"step":5,"task":"Publish","skill":"figma-review","desc":"审查 + 发布"}],
    "video-produce":[
        {"step":1,"task":"Content","skill":"sera-content-factory","desc":"官网素材/事实"},
        {"step":2,"task":"Compose","skill":"sera-video-pipeline","desc":"图卡/字幕/BGM 合成"},
        {"step":3,"task":"Render","skill":"sera-compute-control","desc":"远程渲染（可选）"},
        {"step":4,"task":"Archive","skill":"sera-asset-manager","desc":"入库 Eagle"}],
    "creator-intelligence":[
        {"step":1,"task":"Inventory","skill":"sera-creator-intelligence","desc":"建立 Creator/频道完整目录与覆盖率"},
        {"step":2,"task":"Acquire","skill":"sera-creator-intelligence","desc":"获取并规范化 Transcript/Raw sources"},
        {"step":3,"task":"Analyze","skill":"sera-creator-intelligence","desc":"单内容 Intelligence + Claim/Evidence/Reasoning"},
        {"step":4,"task":"Score","skill":"sera-creator-intelligence","desc":"Knowledge Score + Watch Verdict"},
        {"step":5,"task":"Synthesize","skill":"sera-creator-intelligence","desc":"Topic/Recurring Ideas/Evolution/Contradictions"},
        {"step":6,"task":"Publish","skill":"sera-creator-intelligence","desc":"Creator Report + Canonical Knowledge + indexes"}],
    "trading-research":[
        {"step":1,"task":"Analyze","skill":"trading-analysis","desc":"复盘/统计"},
        {"step":2,"task":"Research","skill":"sera-finance-suite","desc":"行情/数据辅助"},
        {"step":3,"task":"Report","skill":"sera-knowledge-sync","desc":"报告归档"}],
    "otc-bd":[
        {"step":1,"task":"Profile","skill":"sera-crm-adapter","desc":"客户画像"},
        {"step":2,"task":"Outreach","skill":"sera-mail-hub","desc":"沟通/回复"},
        {"step":3,"task":"Record","skill":"sera-knowledge-sync","desc":"归档"}],
}

def intent_router(text, routes=None):
    res=route(text,routes); return {"intent":res["route"].get("intent","未匹配"),"route_id":res["route"].get("id","fallback"),"matched":res["matched"]}
def agent_planner(text, routes=None):
    res=route(text,routes); return {"agent":res["route"].get("agent","sera-agent-orchestrator"),"pipeline":res.get("pipeline",[]),"finalize":res.get("finalize",[])}
def execution_planner(text, routes=None):
    res=route(text,routes); rid=res["route"].get("id","fallback"); steps=EXECUTION_STEPS.get(rid)
    if steps: return {"plan":steps,"route_id":rid,"finalize":res.get("finalize",[])}
    steps=[{"step":i+1,"task":s.split(":")[-1],"skill":s,"desc":""} for i,s in enumerate(res.get("pipeline",[]))]
    return {"plan":steps,"route_id":rid,"finalize":res.get("finalize",[])}
def plan(text,routes=None):
    return {"query":text,"layer1_intent":intent_router(text,routes),"layer2_agent":agent_planner(text,routes),"layer3_execution":execution_planner(text,routes)}

TESTS = [
    ("grill me，先帮我把需求想清楚","grill-clarify"),
    ("帮我想清楚这个技术选型","grill-clarify"),
    ("帮我分析这个 YouTube 博主哪些视频最值得看","creator-intelligence"),
    ("把这个频道所有视频拆成论点论据并做知识库","creator-intelligence"),
    ("做一条 PropFirm.TV 视频","video-produce"),
    ("生成官网素材 B-roll","video-produce"),
    ("推送今天的 PropFirm 优惠","propfirm-intel"),
    ("分析一下 topstep 的规则","propfirm-intel"),
    ("设计一个品牌海报","design-produce"),
    ("帮我做 TradeSpan 产品发布页","product-init"),
    ("复盘这周的交易","trading-research"),
    ("ATAS 订单流怎么解读","trading-research"),
    ("这个客户跟进一下","otc-bd"),
    ("把报告归档到 Obsidian","knowledge-ops"),
    ("让 serawin 渲染","compute"),
    ("今天天气怎么样","fallback"),
    ("评估这个项目值不值得做","ceo-decision"),
    ("帮我评估商业机会","ceo-decision"),
]

def main():
    args=sys.argv[1:]
    if not args or args[0] in ("-h","--help"):
        print(__doc__); return
    if args[0]=="--list":
        for r in load_routes(): print(f"  {r['id']:24s} {r['intent']:20s} agent={r.get('agent','')}")
        return
    if args[0]=="--test":
        ok=0
        for query,expected in TESTS:
            rid=route(query)["route"].get("id",""); mark="✓" if rid==expected else "✗"; ok+=rid==expected; print(f"  {mark} [{rid:24s}] {query}")
        print(f"\n通过 {ok}/{len(TESTS)}"); return
    if args[0]=="--plan":
        query=" ".join(args[1:]) or sys.stdin.read().strip(); print(json.dumps(plan(query),ensure_ascii=False,indent=2)); return
    if args[0]=="--plan-test":
        ok=0
        for query,expected in TESTS:
            p=plan(query); l1=p["layer1_intent"]["route_id"]; steps=p["layer3_execution"].get("plan",[]); valid=l1==expected and len(steps)>=1; ok+=valid; print(f"  {'✓' if valid else '✗'} [{l1:24s}] {query} → {len(steps)} steps")
        print(f"\n通过 {ok}/{len(TESTS)}"); return
    query=" ".join(args)
    if query=="-": query=sys.stdin.read().strip()
    print(json.dumps(route(query),ensure_ascii=False,indent=2))

if __name__=="__main__": main()
