"use client"

import { motion } from "framer-motion"
import { Building2, Bot, FolderKanban, Users, ChevronRight } from "lucide-react"
import { useLang } from "@/lib/language-provider"
import departmentsData from "@/data/departments.json"
import agentsData from "@/data/agents.json"

const gradientMap: Record<string, string> = {
  product: "linear-gradient(135deg, #0066FF, #2692FF)",
  design: "linear-gradient(135deg, #C9A84C, #DEC48A)",
  marketing: "linear-gradient(135deg, #10B981, #34D399)",
  content: "linear-gradient(135deg, #F59E0B, #FBBF24)",
  engineering: "linear-gradient(135deg, #0066FF, #0052CC)",
  business: "linear-gradient(135deg, #8B5CF6, #A78BFA)",
}

const deptNameKey: Record<string, string> = {
  product: "dept.product",
  design: "dept.design",
  marketing: "dept.marketing",
  content: "dept.content",
  engineering: "dept.engineering",
  business: "dept.business",
}

function DepartmentSection({ dept, index }: { dept: typeof departmentsData[0]; index: number }) {
  const { t, tt } = useLang()
  const deptAgents = agentsData.filter(a => dept.agents.includes(a.id))
  const gradient = gradientMap[dept.id] || "var(--brand-gradient)"

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1 }}
      className="htx-card overflow-hidden"
    >
      <div className="p-5" style={{ borderBottom: "1px solid var(--border)" }}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg flex items-center justify-center" style={{ background: gradient }}>
              <Building2 className="w-5 h-5 text-white" />
            </div>
            <div>
              <h3 className="text-base font-semibold" style={{ color: "var(--text-primary)" }}>
                {t(deptNameKey[dept.id] || dept.id)}
              </h3>
              <p className="text-xs" style={{ color: "var(--text-muted)" }}>{tt(dept.description)}</p>
            </div>
          </div>
          <div className="flex items-center gap-3 text-xs" style={{ color: "var(--text-muted)" }}>
            <span className="flex items-center gap-1">
              <Bot className="w-3.5 h-3.5" /> {deptAgents.length}{t("misc.agents")}
            </span>
            <span className="flex items-center gap-1">
              <FolderKanban className="w-3.5 h-3.5" /> {dept.projects.length}{t("misc.projects")}
            </span>
          </div>
        </div>
      </div>

      <div className="p-5">
        <div className="flex items-center gap-1 mb-3 text-xs uppercase tracking-wider" style={{ color: "var(--text-muted)" }}>
          <Users className="w-3.5 h-3.5" /> {t("department.team-members")}
        </div>
        <div className="space-y-2">
          {deptAgents.map((agent, i) => (
            <motion.div
              key={agent.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 + i * 0.05 }}
              className="flex items-center gap-3 p-3 rounded-lg transition-all cursor-pointer group"
              style={{ background: "var(--bg-base)", border: "1px solid var(--border)" }}
              onMouseEnter={e => e.currentTarget.style.borderColor = "var(--brand)"}
              onMouseLeave={e => e.currentTarget.style.borderColor = "var(--border)"}
            >
              <div className="w-8 h-8 rounded-lg flex items-center justify-center shrink-0" style={{ background: "var(--brand-gradient)" }}>
                <Bot className="w-4 h-4 text-white" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium" style={{ color: "var(--text-primary)" }}>{tt(agent.name)}</span>
                  <span className={`status-dot ${agent.status}`} />
                </div>
                <span className="text-xs" style={{ color: "var(--text-muted)" }}>{tt(agent.role)}</span>
              </div>
              <div className="flex items-center gap-2 shrink-0">
                <div className="flex flex-wrap gap-1">
                  {agent.skills.slice(0, 2).map(s => (
                    <span key={s} className="text-[10px] px-1.5 py-0.5 rounded" style={{ background: "var(--bg-surface-hover)", color: "var(--text-muted)", border: "1px solid var(--border)" }}>
                      {tt(s)}
                    </span>
                  ))}
                  {agent.skills.length > 2 && (
                    <span className="text-[10px] px-1.5 py-0.5 rounded" style={{ background: "var(--bg-surface-hover)", color: "var(--text-muted)", border: "1px solid var(--border)" }}>
                      +{agent.skills.length - 2}
                    </span>
                  )}
                </div>
                <ChevronRight className="w-4 h-4" style={{ color: "var(--border-strong)" }} />
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {dept.projects.length > 0 && (
        <div className="px-5 pb-5">
          <div className="flex items-center gap-1 mb-2 text-xs uppercase tracking-wider" style={{ color: "var(--text-muted)" }}>
            <FolderKanban className="w-3.5 h-3.5" /> {t("department.active-projects")}
          </div>
          <div className="flex flex-wrap gap-2">
            {dept.projects.map(p => (
              <span key={p} className="px-2.5 py-1 rounded-md text-xs" style={{ background: "var(--bg-surface-hover)", color: "var(--text-secondary)", border: "1px solid var(--border)" }}>
                {p}
              </span>
            ))}
          </div>
        </div>
      )}
    </motion.div>
  )
}

export default function DepartmentPage() {
  const { t } = useLang()

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold" style={{ color: "var(--text-primary)" }}>{t("department.title")}</h1>
        <p className="text-sm mt-1" style={{ color: "var(--text-muted)" }}>{t("department.subtitle")}</p>
      </div>

      <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} className="flex items-center justify-center">
        <div className="rounded-xl p-5 text-center min-w-[200px]" style={{ background: "var(--brand-gradient)" }}>
          <div className="w-12 h-12 rounded-full bg-white/10 flex items-center justify-center mx-auto mb-2 text-2xl">👑</div>
          <h3 className="text-lg font-bold text-white">Sera AI</h3>
          <p className="text-xs text-white/70">{t("department.ceo")}</p>
        </div>
      </motion.div>

      <div className="flex justify-center">
        <div className="w-px h-6" style={{ background: "linear-gradient(180deg, var(--brand), transparent)" }} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {departmentsData.map((dept, i) => (
          <DepartmentSection key={dept.id} dept={dept} index={i} />
        ))}
      </div>
    </div>
  )
}