"use client"

import { motion } from "framer-motion"
import { Building2, Bot, FolderKanban, Users, ChevronRight, Layers, GitBranch, Zap, Cpu, Shield } from "lucide-react"
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

const ARCHITECTURE_LAYERS = [
  { label: "Learning OS", desc: "经验 → 规则 → 更好的上下文", icon: Layers, color: "#8B5CF6", layer: "L4" },
  { label: "Context OS", desc: "此刻该知道什么", icon: Cpu, color: "var(--brand)", layer: "L3" },
  { label: "Organization OS", desc: "员工是谁、如何分配", icon: Shield, color: "#10B981", layer: "L2" },
  { label: "Workflow OS", desc: "业务流程如何串联", icon: GitBranch, color: "#F59E0B", layer: "L1" },
  { label: "Execution OS", desc: "工具与机器落地", icon: Zap, color: "#EC4899", layer: "L0" },
]

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
        <h1 className="text-lg font-bold" style={{ color: "var(--text-primary)" }}>组织 · 公司架构</h1>
        <p className="text-sm mt-1" style={{ color: "var(--text-muted)" }}>5 纵向 + 1 横向 + 1 反馈环</p>
      </div>

      {/* Architecture Layers — inspired by K3 */}
      <div className="rounded-xl border p-5" style={{ background: "var(--bg-surface)", borderColor: "var(--border)" }}>
        <div className="flex items-center gap-2 mb-4">
          <Layers className="w-4 h-4" style={{ color: "var(--brand)" }} />
          <span className="text-xs font-semibold uppercase tracking-wider" style={{ color: "var(--text-secondary)" }}>Sera OPC OS 架构层级</span>
        </div>

        {/* CEO */}
        <div className="flex items-center justify-center mb-3">
          <div className="flex items-center gap-3 px-4 py-2 rounded-xl border" style={{ background: "var(--bg-base)", borderColor: "#8B5CF630" }}>
            <div className="w-8 h-8 rounded-lg flex items-center justify-center text-xs font-bold" style={{ background: "#8B5CF615", color: "#8B5CF6" }}>👑</div>
            <div>
              <span className="text-sm font-semibold" style={{ color: "var(--text-primary)" }}>CEO</span>
              <span className="text-xs ml-2" style={{ color: "var(--text-muted)" }}>Founder · person.sera</span>
            </div>
            <span className="text-[10px] px-1.5 py-0.5 rounded font-medium" style={{ color: "#8B5CF6", background: "#8B5CF615" }}>品味、价值观、最终裁决</span>
          </div>
        </div>

        {/* Down arrow */}
        <div className="flex justify-center mb-2">
          <div className="w-px h-4" style={{ background: "var(--border)" }} />
        </div>

        {/* Vertical Layers */}
        <div className="flex flex-col gap-2 max-w-lg mx-auto">
          {ARCHITECTURE_LAYERS.map((layer, i) => {
            const Icon = layer.icon
            return (
              <div key={layer.label} className="flex items-center gap-3 p-3 rounded-lg border transition-all" style={{
                background: "var(--bg-base)",
                borderColor: "var(--border)",
              }}>
                <div className="w-8 h-8 rounded-lg flex items-center justify-center shrink-0" style={{ background: `${layer.color}15` }}>
                  <Icon className="w-4 h-4" style={{ color: layer.color }} />
                </div>
                <div className="flex-1 min-w-0">
                  <span className="text-sm font-medium" style={{ color: "var(--text-primary)" }}>{layer.label}</span>
                  <span className="text-xs ml-2" style={{ color: "var(--text-muted)" }}>{layer.desc}</span>
                </div>
                <span className="text-[10px] px-2 py-0.5 rounded font-medium shrink-0" style={{ background: `${layer.color}15`, color: layer.color }}>{layer.layer}</span>
              </div>
            )
          })}
        </div>

        {/* Horizontal Base */}
        <div className="mt-3 flex justify-center">
          <div className="flex items-center gap-2 px-4 py-2 rounded-lg border text-xs" style={{ background: "var(--bg-base)", borderColor: "var(--brand)30", color: "var(--brand)" }}>
            <GitBranch className="w-3.5 h-3.5" />
            <span className="font-semibold">BASE Memory OS</span>
            <span style={{ color: "var(--text-muted)" }}>SMOP · Kernel · Graph — 横贯所有层</span>
          </div>
        </div>

        {/* Feedback Loop */}
        <div className="mt-3 flex justify-center">
          <div className="flex items-center gap-2 px-4 py-2 rounded-lg border text-xs" style={{ background: "var(--bg-base)", borderColor: "#8B5CF630", color: "#8B5CF6" }}>
            <span className="text-lg">↻</span>
            <span className="font-semibold">LOOP Learning OS</span>
            <span style={{ color: "var(--text-muted)" }}>经验 → 规则 → 更好的上下文 — 写回 Memory ↑</span>
          </div>
        </div>

        <p className="text-xs text-center mt-3" style={{ color: "var(--text-muted)" }}>
          任何 Agent 接入即继承全部层 —— 它加入的不是工具箱，而是一家正在运转的公司
        </p>
      </div>

      {/* Department sections */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {departmentsData.map((dept, i) => (
          <DepartmentSection key={dept.id} dept={dept} index={i} />
        ))}
      </div>
    </div>
  )
}