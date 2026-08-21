"use client"
import { motion } from "framer-motion"
import { Box, ChevronRight, Database, GitBranch, Search } from "lucide-react"
import { useLang } from "@/lib/language-provider"
import { localized } from "@/lib/localized"

const objects = ["Project", "Agent", "Decision", "Experience", "Rule", "Asset", "Skill"]
export default function MemoryPage() {
  const { lang } = useLang()
  const c = (zh: string, en: string) => localized(lang, zh, en)
  return <div className="command-page"><header className="page-head"><div><span>MEMORY OS / SMOP</span><h1>{c("记忆图谱", "Memory Graph")}</h1><p>{c("公司不只是存储文件，而是记住对象、关系、权威与证据。", "The company does not store files. It remembers objects, relations, authority and evidence.")}</p></div><div className="head-stat"><strong>346</strong><span>{c("活跃对象", "ACTIVE OBJECTS")}</span></div></header>
    <div className="graph-layout"><section className="terminal-panel graph-canvas"><div className="graph-toolbar"><div><Search /><span>{c("搜索公司记忆", "Search company memory")}</span></div><button><GitBranch /> {c("关系", "RELATIONS")}</button></div><motion.div className="universe" initial={{ opacity: 0 }} animate={{ opacity: 1 }}><svg viewBox="0 0 800 520" aria-hidden><g>{[[400,120,245,245],[400,120,555,245],[245,245,180,400],[245,245,350,400],[555,245,475,400],[555,245,640,400]].map((v,i)=><line key={i} x1={v[0]} y1={v[1]} x2={v[2]} y2={v[3]} />)}</g></svg><button className="graph-node root"><Database /><b>TradeSpan</b><span>{c("项目", "Project")}</span></button>{[["Decisions","12","n1"],["Agents","4","n2"],["Previous failures","3","n3"],["Skills","18","n4"],["Rules applied","7","n5"],["Assets","42","n6"]].map(([name,count,pos])=><button key={name} className={`graph-node ${pos}`}><Box /><b>{c({Decisions:"决策",Agents:"智能体","Previous failures":"历史失败",Skills:"技能","Rules applied":"已应用规则",Assets:"资产"}[name] || name, name)}</b><span>{count} {c("个对象", "objects")}</span></button>)}</motion.div></section>
      <aside className="terminal-panel object-inspector"><div className="panel-heading"><div><span>{c("对象", "OBJECT")}</span><h2>project.tradespan</h2></div></div><div className="object-type"><Box /><span><b>TradeSpan</b><small>{c("项目 · 活跃 · v3", "Project · active · v3")}</small></span></div><dl><div><dt>{c("权威", "Authority")}</dt><dd>founder</dd></div><div><dt>{c("范围", "Scope")}</dt><dd>organization</dd></div><div><dt>{c("置信度", "Confidence")}</dt><dd>1.00</dd></div><div><dt>{c("重要性", "Importance")}</dt><dd>0.94</dd></div></dl><h3>{c("关系", "RELATIONSHIPS")}</h3>{[c("12 项决策", "12 decisions"), c("4 个分配智能体", "4 assigned agents"), c("7 条生效规则", "7 active rules"), c("3 次已学习失败", "3 learned failures")].map(x=><button className="relation" key={x}><span>{x}</span><ChevronRight /></button>)}</aside></div>
    <div className="object-legend">{objects.map((x,i)=><span key={x}><i data-n={i}/>{x}</span>)}</div>
  </div>
}
