"use client"

import { motion } from "framer-motion"
import { Bot, Cpu, Wrench, ExternalLink } from "lucide-react"
import { useLang } from "@/lib/language-provider"
import agentsData from "@/data/agents.json"

const departmentMap: Record<string, { name: string; gradient: string }> = {
  product: { name: "dept.product", gradient: "linear-gradient(135deg, #0066FF, #2692FF)" },
  design: { name: "dept.design", gradient: "linear-gradient(135deg, #C9A84C, #DEC48A)" },
  marketing: { name: "dept.marketing", gradient: "linear-gradient(135deg, #10B981, #34D399)" },
  content: { name: "dept.content", gradient: "linear-gradient(135deg, #F59E0B, #FBBF24)" },
  engineering: { name: "dept.engineering", gradient: "linear-gradient(135deg, #0066FF, #0052CC)" },
  business: { name: "dept.business", gradient: "linear-gradient(135deg, #8B5CF6, #A78BFA)" },
}

function AgentCard({ agent, index }: { agent: typeof agentsData[0]; index: number }) {
  const { t, tt } = useLang()
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05 }}
      className="htx-card p-5 cursor-pointer"
    >
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg flex items-center justify-center" style={{ background: "var(--brand-gradient)" }}>
            <Bot className="w-5 h-5 text-white" />
          </div>
          <div>
            <h3 className="text-sm font-semibold" style={{ color: "var(--text-primary)" }}>{tt(agent.name)}</h3>
            <span className="text-xs" style={{ color: "var(--text-muted)" }}>{tt(agent.role)}</span>
          </div>
        </div>
        <span className={`badge ${agent.status === "active" ? "badge-active" : "badge-idle"}`}>
          <span className={`status-dot ${agent.status}`} />
          {agent.status === "active" ? t("agents.active") : t("agents.idle")}
        </span>
      </div>

      <div className="space-y-2.5 mb-4">
        <div className="flex items-center gap-2 text-xs" style={{ color: "var(--text-muted)" }}>
          <Cpu className="w-3.5 h-3.5" />
          <span style={{ color: "var(--text-secondary)" }}>{agent.model}</span>
        </div>
        <div className="flex flex-wrap gap-1.5">
          {agent.skills.map(skill => (
            <span key={skill} className="px-2 py-0.5 rounded text-[10px]" style={{ background: "var(--bg-surface-hover)", color: "var(--text-secondary)", border: "1px solid var(--border)" }}>
              {tt(skill)}
            </span>
          ))}
        </div>
        <div className="flex items-center gap-2 text-xs" style={{ color: "var(--text-muted)" }}>
          <Wrench className="w-3.5 h-3.5" />
          <span style={{ color: "var(--text-secondary)" }}>{agent.tools.join(", ")}</span>
        </div>
      </div>

      <div className="flex items-center justify-between pt-3" style={{ borderTop: "1px solid var(--border)" }}>
        <span className="text-xs" style={{ color: "var(--text-muted)" }}>{tt(agent.description)}</span>
        <ExternalLink className="w-4 h-4" style={{ color: "var(--text-muted)" }} />
      </div>
    </motion.div>
  )
}

export default function AgentsPage() {
  const { t } = useLang()
  const departments = Object.entries(departmentMap)

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold" style={{ color: "var(--text-primary)" }}>{t("agents.title")}</h1>
        <p className="text-sm mt-1" style={{ color: "var(--text-muted)" }}>{t("agents.subtitle")}</p>
      </div>

      {departments.map(([deptId, dept]) => {
        const deptAgents = agentsData.filter(a => a.department === deptId)
        if (deptAgents.length === 0) return null
        return (
          <div key={deptId}>
            <div className="flex items-center gap-2 mb-3">
              <div className="w-8 h-8 rounded-lg flex items-center justify-center text-white text-sm" style={{ background: dept.gradient }}>
                {t(dept.name).charAt(0)}
              </div>
              <div>
                <h2 className="text-sm font-semibold" style={{ color: "var(--text-primary)" }}>{t(dept.name)}</h2>
                <span className="text-xs" style={{ color: "var(--text-muted)" }}>{deptAgents.length}{t("misc.agents")}</span>
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {deptAgents.map((agent, i) => (
                <AgentCard key={agent.id} agent={agent} index={i} />
              ))}
            </div>
          </div>
        )
      })}
    </div>
  )
}