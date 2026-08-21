"use client"

import { motion } from "framer-motion"
import { Bot, Users, Wrench, Zap } from "lucide-react"
import { useLang } from "@/lib/language-provider"
import agentsData from "@/data/agents.json"
import departmentsData from "@/data/departments.json"

// Agent short codes + scores
const AGENT_META: Record<string, { code: string; score: number }> = {
  "product-agent": { code: "PA", score: 91 },
  "brand-agent": { code: "BA", score: 93 },
  "ui-agent": { code: "UA", score: 90 },
  "motion-agent": { code: "MA", score: 88 },
  "seo-agent": { code: "SA", score: 87 },
  "growth-agent": { code: "GA", score: 87 },
  "script-agent": { code: "SC", score: 89 },
  "video-agent": { code: "VA", score: 94 },
  "frontend-agent": { code: "FA", score: 92 },
  "backend-agent": { code: "BE", score: 90 },
  "propfirm-agent": { code: "PF", score: 90 },
  "otc-agent": { code: "OA", score: 86 },
  "trading-agent": { code: "TA", score: 88 },
}

const MODEL_COLORS: Record<string, string> = {
  "DeepSeek": "#4C6FFF",
  "Trae": "#EC4899",
  "Codex": "#10B981",
  "Serawin": "#F59E0B",
  "Kimi K3": "#8B5CF6",
}

const CEO_AGENT = { code: "SC", name: "Sera CEO", role: "首席执行官 · 战略与优先级裁决", model: "Kimi K3", score: 96 }

function AgentCard({ agent }: { agent: typeof agentsData[0] }) {
  const meta = AGENT_META[agent.id]
  const isActive = agent.status === "active"
  const modelColor = MODEL_COLORS[agent.model] || "var(--text-muted)"

  return (
    <div className="flex items-center gap-3 p-3 rounded-lg border transition-all" style={{
      background: isActive ? "var(--bg-surface)" : "var(--bg-base)",
      borderColor: isActive ? "var(--border)" : "var(--border)",
      opacity: isActive ? 1 : 0.6,
    }}>
      {/* Avatar */}
      <div className="w-9 h-9 rounded-lg flex items-center justify-center shrink-0 text-xs font-bold" style={{ background: `${modelColor}15`, color: modelColor }}>
        {meta?.code || "??"}
      </div>
      {/* Info */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium truncate" style={{ color: "var(--text-primary)" }}>{agent.name}</span>
          <span className="w-1.5 h-1.5 rounded-full shrink-0" style={{ background: isActive ? "var(--success)" : "var(--text-muted)" }} />
        </div>
        <p className="text-xs truncate" style={{ color: "var(--text-muted)" }}>{agent.role}</p>
      </div>
      {/* Model & Score */}
      <div className="flex items-center gap-2 shrink-0">
        <span className="text-[10px] px-1.5 py-0.5 rounded font-medium" style={{ background: `${modelColor}15`, color: modelColor }}>
          {agent.model}
        </span>
        {meta && (
          <span className="text-xs font-mono font-bold w-7 text-right" style={{ color: "var(--text-secondary)" }}>{meta.score}</span>
        )}
      </div>
    </div>
  )
}

export default function AgentsPage() {
  const { t } = useLang()
  const activeCount = agentsData.filter(a => a.status === "active").length
  const totalCount = agentsData.length

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-lg font-bold" style={{ color: "var(--text-primary)" }}>员工 · 数字劳动力</h1>
          <p className="text-sm mt-1" style={{ color: "var(--text-muted)" }}>
            {totalCount} 名员工 · {activeCount} 名在岗 · {departmentsData.length} 个部门
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs transition-all" style={{ color: "var(--brand)", background: "var(--brand-soft)" }}>
            <Wrench className="w-3.5 h-3.5" />编排模式
          </button>
          <button className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs transition-all border" style={{ color: "var(--text-secondary)", borderColor: "var(--border)" }}>
            <Zap className="w-3.5 h-3.5" />扩编
          </button>
        </div>
      </div>

      {/* CEO + Decision Layer */}
      <div className="rounded-xl border p-4" style={{ background: "var(--bg-surface)", borderColor: "var(--border)" }}>
        <div className="flex items-center gap-2 mb-3">
          <span className="text-[10px] uppercase tracking-wider px-2 py-0.5 rounded font-medium" style={{ background: `${MODEL_COLORS["Kimi K3"]}15`, color: MODEL_COLORS["Kimi K3"] }}>
            决策层
          </span>
          <span className="text-[10px] font-medium" style={{ color: "var(--text-muted)" }}>1</span>
        </div>
        <div className="flex items-center gap-3 p-3 rounded-lg" style={{ background: "var(--bg-base)" }}>
          <div className="w-10 h-10 rounded-lg flex items-center justify-center shrink-0 text-xs font-bold" style={{ background: `${MODEL_COLORS["Kimi K3"]}15`, color: MODEL_COLORS["Kimi K3"] }}>
            {CEO_AGENT.code}
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium" style={{ color: "var(--text-primary)" }}>{CEO_AGENT.name}</span>
              <span className="w-1.5 h-1.5 rounded-full" style={{ background: "var(--success)" }} />
            </div>
            <p className="text-xs" style={{ color: "var(--text-muted)" }}>{CEO_AGENT.role}</p>
          </div>
          <span className="text-[10px] px-1.5 py-0.5 rounded font-medium" style={{ background: `${MODEL_COLORS["Kimi K3"]}15`, color: MODEL_COLORS["Kimi K3"] }}>
            {CEO_AGENT.model}
          </span>
          <span className="text-xs font-mono font-bold w-7 text-right" style={{ color: "var(--text-secondary)" }}>{CEO_AGENT.score}</span>
        </div>
      </div>

      {/* Departments */}
      <div className="space-y-4">
        {departmentsData.map(dept => {
          const deptAgents = agentsData.filter(a => dept.agents.includes(a.id))
          const activeInDept = deptAgents.filter(a => a.status === "active").length
          return (
            <motion.div
              key={dept.id}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              className="rounded-xl border overflow-hidden" style={{ background: "var(--bg-surface)", borderColor: "var(--border)" }}
            >
              {/* Department header */}
              <div className="flex items-center gap-3 px-4 py-3 border-b" style={{ borderColor: "var(--border)" }}>
                <div className="w-2.5 h-2.5 rounded-full shrink-0" style={{ background: dept.color }} />
                <div className="flex-1">
                  <span className="text-sm font-semibold" style={{ color: "var(--text-primary)" }}>{dept.name}</span>
                  <span className="text-xs ml-2" style={{ color: "var(--text-muted)" }}>{dept.description}</span>
                </div>
                <span className="text-[10px] font-medium" style={{ color: "var(--text-muted)" }}>
                  {deptAgents.length} agents · {activeInDept} 在线
                </span>
              </div>
              {/* Agent cards */}
              <div className="p-3 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2">
                {deptAgents.map(agent => (
                  <AgentCard key={agent.id} agent={agent} />
                ))}
              </div>
            </motion.div>
          )
        })}
      </div>
    </div>
  )
}