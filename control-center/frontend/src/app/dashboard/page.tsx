"use client"

import { motion } from "framer-motion"
import { Bot, FolderKanban, Activity, TrendingUp } from "lucide-react"
import { ProjectCard } from "@/components/dashboard/project-card"
import { AgentStatus } from "@/components/dashboard/agent-status"
import { WorkflowPreview } from "@/components/dashboard/workflow-preview"
import { ActivityTimeline } from "@/components/dashboard/activity-timeline"
import { useLang } from "@/lib/language-provider"
import projectsData from "@/data/projects.json"
import agentsData from "@/data/agents.json"
import workflowsData from "@/data/workflows.json"

export default function DashboardPage() {
  const { t } = useLang()
  const activeAgents = agentsData.filter(a => a.status === "active").slice(0, 5)
  const activeWorkflows = workflowsData.workflows.filter(w => w.status === "active")

  const statCards = [
    { label: "dashboard.active-projects", value: "5", icon: FolderKanban },
    { label: "dashboard.running-agents", value: "8", icon: Bot },
    { label: "dashboard.today-output", value: "12", icon: Activity },
    { label: "dashboard.system-uptime", value: "99.7%", icon: TrendingUp },
  ]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold" style={{ color: "var(--text-primary)" }}>{t("dashboard.title")}</h1>
        <p className="text-sm mt-1" style={{ color: "var(--text-muted)" }}>{t("dashboard.subtitle")}</p>
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