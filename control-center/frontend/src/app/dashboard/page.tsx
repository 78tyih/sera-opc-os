"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import { Bot, FolderKanban, Activity, TrendingUp, Send, Sparkles } from "lucide-react"
import { ProjectCard } from "@/components/dashboard/project-card"
import { AgentStatus } from "@/components/dashboard/agent-status"
import { WorkflowPreview } from "@/components/dashboard/workflow-preview"
import { ActivityTimeline } from "@/components/dashboard/activity-timeline"
import { useLang } from "@/lib/language-provider"
import { useData } from "@/lib/use-data"
import { api } from "@/lib/api-client"
import projectsData from "@/data/projects.json"
import agentsData from "@/data/agents.json"
import workflowsData from "@/data/workflows.json"
import departmentsData from "@/data/departments.json"
import Link from "next/link"

const QUICK_COMMANDS = [
  { label: "发射牛牛 AI", href: "/canvas" },
  { label: "项目进度", href: "/projects" },
  { label: "组建团队", href: "/agents" },
  { label: "系统状态", href: "/console" },
]

export default function DashboardPage() {
  const { t } = useLang()
  const { data: stats } = useData(() => api.stats())
  const [cmdInput, setCmdInput] = useState("")
  const activeAgents = agentsData.filter(a => a.status === "active").slice(0, 5)
  const activeWorkflows = workflowsData.workflows.filter(w => w.status === "active")
  const agentCount = agentsData.filter(a => a.status === "active").length

  const statCards = [
    { label: "dashboard.active-projects", value: stats?.activeProjects.toString() || "5", icon: FolderKanban },
    { label: "dashboard.running-agents", value: stats?.totalAgents.toString() || "13", icon: Bot },
    { label: "dashboard.today-output", value: stats?.todayOutput || "12", icon: Activity },
    { label: "dashboard.system-uptime", value: stats?.uptime || "99.7%", icon: TrendingUp },
  ]

  return (
    <div className="space-y-6">
      {/* Command Entry — inspired by K3 */}
      <div className="rounded-xl border p-5" style={{ background: "var(--bg-surface)", borderColor: "var(--border)" }}>
        <h1 className="text-xl font-bold mb-1" style={{ color: "var(--text-primary)" }}>今天让公司做什么？</h1>
        <p className="text-sm mb-4" style={{ color: "var(--text-muted)" }}>
          {agentsData.length} 名 AI 员工 · {departmentsData.length} 个部门 · 1 个共享大脑，随时待命
        </p>
        <div className="flex items-center gap-2">
          <div className="flex-1 flex items-center gap-2 rounded-lg border px-3 py-2.5" style={{ borderColor: "var(--border)", background: "var(--bg-base)" }}>
            <Sparkles className="w-4 h-4 shrink-0" style={{ color: "var(--brand)" }} />
            <input
              type="text"
              value={cmdInput}
              onChange={e => setCmdInput(e.target.value)}
              placeholder="向公司下达指令…"
              className="flex-1 bg-transparent text-sm outline-none"
              style={{ color: "var(--text-primary)" }}
            />
            <button className="w-8 h-8 flex items-center justify-center rounded-lg shrink-0" style={{ background: "var(--brand)", color: "#fff" }}>
              <Send className="w-4 h-4" />
            </button>
          </div>
        </div>
        <div className="flex flex-wrap gap-2 mt-3">
          {QUICK_COMMANDS.map(cmd => (
            <Link
              key={cmd.label}
              href={cmd.href}
              className="px-3 py-1.5 rounded-lg text-xs transition-all border"
              style={{ background: "var(--bg-base)", borderColor: "var(--border)", color: "var(--text-secondary)" }}
            >
              {cmd.label}
            </Link>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((stat, i) => {
          const Icon = stat.icon
          return (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
              className="htx-card p-5"
            >
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs uppercase tracking-wider" style={{ color: "var(--text-muted)" }}>{t(stat.label)}</span>
                <Icon className="w-5 h-5" style={{ color: "var(--brand)" }} />
              </div>
              <div className="text-2xl font-bold" style={{ color: "var(--text-primary)" }}>{stat.value}</div>
            </motion.div>
          )
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <div className="flex items-center justify-between mb-3">
            <span className="section-title">{t("dashboard.active-projects")}</span>
            <span className="text-xs" style={{ color: "var(--brand)", cursor: "pointer" }}>{t("dashboard.view-all")} →</span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {projectsData.filter(p => p.status === "active").slice(0, 4).map((proj, i) => (
              <ProjectCard key={proj.id} {...proj} index={i} />
            ))}
          </div>
        </div>

        <div>
          <span className="section-title mb-3 block">{t("dashboard.activity")}</span>
          <ActivityTimeline />
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div>
          <div className="flex items-center justify-between mb-3">
            <span className="section-title">{t("dashboard.active-agents")}</span>
            <span className="text-xs" style={{ color: "var(--brand)", cursor: "pointer" }}>{t("dashboard.view-all")} →</span>
          </div>
          <div className="space-y-2">
            {activeAgents.map((agent, i) => (
              <AgentStatus key={agent.id} {...agent} index={i} />
            ))}
          </div>
        </div>
        <div>
          <div className="flex items-center justify-between mb-3">
            <span className="section-title">{t("dashboard.running-workflows")}</span>
            <span className="text-xs" style={{ color: "var(--brand)", cursor: "pointer" }}>{t("dashboard.view-all")} →</span>
          </div>
          <div className="space-y-3">
            {activeWorkflows.map((wf, i) => (
              <WorkflowPreview key={wf.id} name={wf.name} description={wf.description} status={wf.status} nodes={wf.nodes} index={i} />
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}