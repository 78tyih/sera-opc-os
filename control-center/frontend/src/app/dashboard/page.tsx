"use client"

import Link from "next/link"
import { useEffect, useState } from "react"
import { motion } from "framer-motion"
import { ArrowUpRight, BrainCircuit, CheckCircle2, CircleDot, Clock3, Network, ShieldCheck, Sparkles } from "lucide-react"
import { useLang } from "@/lib/language-provider"

const missions = [
  { name: "TradeSpan Website", owner: "Frontend Agent", status: "EXECUTING", progress: 68, next: "Validate trust hierarchy" },
  { name: "PropFirm Video Factory", owner: "Video Producer", status: "REVIEW", progress: 84, next: "Approve real UI footage" },
  { name: "OTC Intelligence", owner: "OTC Agent", status: "LEARNING", progress: 42, next: "Distill client pattern" },
]
const signals = [
  ["Financial UI trust rule updated", "RULE", "organization", "2m"],
  ["Video failure pattern detected", "EXPERIENCE", "project", "18m"],
  ["Founder preference resolved a conflict", "DECISION", "founder", "41m"],
]
const stats = [["command.activeMissions", "03", "command.advancing"], ["command.agentsOnline", "12", "command.executing"], ["command.pendingDecisions", "05", "command.founderInput"], ["command.newLearnings", "02", "command.readyDistill"]]

export default function DashboardPage() {
  const { t, tt } = useLang()
  // Live clock; rendered only after mount so SSR HTML always matches first client render.
  const [now, setNow] = useState<Date | null>(null)
  useEffect(() => {
    const tick = () => setNow(new Date())
    tick()
    const id = setInterval(tick, 1000)
    return () => clearInterval(id)
  }, [])
  const dateLabel = now
    ? new Intl.DateTimeFormat("en-GB", { timeZone: "Asia/Shanghai", day: "2-digit", month: "short", year: "numeric" }).format(now).toUpperCase()
    : "-- --- ----"
  const timeLabel = now
    ? new Intl.DateTimeFormat("en-GB", { timeZone: "Asia/Shanghai", hour: "2-digit", minute: "2-digit", second: "2-digit", hour12: false }).format(now)
    : "--:--:--"
  return <div className="command-page">
    <motion.section className="command-intro" initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }}>
      <div><div className="eyebrow"><CircleDot /> {t("command.eyebrow")}</div><h1>{t("command.title")}</h1><p>{t("command.greeting")}</p></div>
      <div className="system-time"><span>{dateLabel}</span><strong>{timeLabel}</strong><small>ASIA / SHANGHAI</small></div>
    </motion.section>
    <section className="metric-strip">{stats.map(([label, value, note], index) => <motion.div key={label} className="metric-cell" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: .08 * index }}><span>{t(label)}</span><strong>{value}</strong><small>{t(note)}</small></motion.div>)}</section>
    <section className="command-grid">
      <div className="terminal-panel intelligence-map">
        <div className="panel-heading"><div><span>01</span><h2>{t("command.graph")}</h2></div><Link href="/memory">{t("command.openGraph")} <ArrowUpRight /></Link></div>
        <div className="cognition-map"><div className="map-spine" /><div className="map-node founder"><small>{t("command.authority")}</small><strong>Sera</strong><span>{t("command.founderIntelligence")}</span></div><div className="map-node context"><BrainCircuit /><small>CONTEXT OS</small><strong>{t("command.contextGovernor")}</strong><span>{t("command.contextRank")}</span></div><div className="map-branches"><div className="map-node"><Network /><small>{t("command.org")}</small><strong>12 {t("nav.agents")}</strong><span>{t("command.departments")}</span></div><div className="map-node"><Sparkles /><small>{t("command.workflow")}</small><strong>3 {t("command.missions")}</strong><span>{t("command.runtimeTasks")}</span></div><div className="map-node"><ShieldCheck /><small>{t("command.memoryOs")}</small><strong>346 objects</strong><span>{t("command.graphHealthy")}</span></div></div><div className="learning-loop">{t("command.learningLoop")} <span>{t("command.betterContext")}</span></div></div>
      </div>
      <aside className="terminal-panel runtime-watch">
        <div className="panel-heading"><div><span>02</span><h2>{t("command.runtime")}</h2></div><i className="live-dot" /></div>
        <div className="agent-identity"><div>FA</div><span><strong>Frontend Agent</strong><small>agent.frontend.engineer</small></span><b>EXECUTING</b></div>
        <dl className="runtime-list"><div><dt>{t("command.currentTask")}</dt><dd>Build TradeSpan landing page</dd></div><div><dt>{t("command.contextInjected")}</dt><dd>18 objects · 3 rules</dd></div><div><dt>{t("command.founderAuthority")}</dt><dd className="ok"><CheckCircle2 /> {t("command.authorityTrust")}</dd></div><div><dt>{t("command.knownRisk")}</dt><dd className="warn">{t("command.reactRisk")}</dd></div></dl>
        <div className="token-row"><span>CONTEXT BUDGET</span><strong>7,800 / 12,000</strong></div><div className="token-track"><i /></div><Link className="panel-action" href="/context">{t("command.inspectContext")} <ArrowUpRight /></Link>
      </aside>
    </section>
    <section className="terminal-panel mission-panel"><div className="panel-heading"><div><span>03</span><h2>{t("command.missions")}</h2></div><small>{t("command.outcomeHeader")}</small></div><div className="mission-table">{missions.map((mission, index) => <div className="mission-row" key={mission.name}><span className="mission-index">0{index + 1}</span><div><strong>{tt(mission.name)}</strong><small>{tt(mission.owner)}</small></div><b data-state={mission.status}>{t(mission.status === "EXECUTING" ? "command.statusExecuting" : mission.status === "REVIEW" ? "command.statusReview" : "command.statusLearning")}</b><div className="mission-progress"><i style={{ transform: `scaleX(${mission.progress / 100})` }} /><span>{mission.progress}%</span></div><p>{t("command.next")}{tt(mission.next)}</p><ArrowUpRight /></div>)}</div></section>
    <section className="terminal-panel learning-panel"><div className="panel-heading"><div><span>04</span><h2>{t("command.learning")}</h2></div><Link href="/learning">{t("command.viewTimeline")} <ArrowUpRight /></Link></div>{signals.map(([title, type, scope, time]) => <div className="signal-row" key={title}><Clock3 /><div><strong>{tt(title)}</strong><span>{type} · authority/{scope}</span></div><time>{time}</time></div>)}</section>
  </div>
}
