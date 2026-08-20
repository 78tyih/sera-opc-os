"use client"

import { motion } from "framer-motion"
import { FolderKanban, ArrowUpRight } from "lucide-react"
import { useLang } from "@/lib/language-provider"

interface ProjectCardProps {
  id: string
  name: string
  category: string
  status: string
  priority: string
  progress: number
  description: string
  agents: string[]
  index: number
}

const categoryColors: Record<string, string> = {
  Product: "#0066FF",
  Content: "#F59E0B",
  Infrastructure: "#10B981",
  Business: "#8B5CF6",
}

export function ProjectCard({ name, category, status, progress, description, index }: ProjectCardProps) {
  const { t, tt } = useLang()
  const color = categoryColors[category] || "var(--text-muted)"

  const statusLabel = status === "active" ? t("status.active")
    : status === "planning" ? t("status.planning")
    : status === "completed" ? t("status.completed")
    : status

  const catLabel = category === "Product" ? t("cat.product")
    : category === "Content" ? t("cat.content")
    : category === "Infrastructure" ? t("cat.infrastructure")
    : category === "Business" ? t("cat.business")
    : category

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.08 }}
      className="htx-card p-5 cursor-pointer group relative overflow-hidden"
    >
      <div className="brand-bar absolute top-0 left-0 right-0" />

      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg flex items-center justify-center" style={{ background: `${color}15` }}>
            <FolderKanban className="w-4 h-4" style={{ color }} />
          </div>
          <div>
            <h3 className="text-sm font-semibold" style={{ color: "var(--text-primary)" }}>{name}</h3>
            <span className="text-[10px] uppercase tracking-wider" style={{ color: "var(--text-muted)" }}>{catLabel}</span>
          </div>
        </div>
        <ArrowUpRight className="w-4 h-4 opacity-0 group-hover:opacity-100 transition-opacity" style={{ color: "var(--text-muted)" }} />
      </div>

      <p className="text-xs mb-3 line-clamp-2" style={{ color: "var(--text-secondary)" }}>{tt(description)}</p>

      <div className="flex items-center justify-between mb-2">
        <span className="text-xs" style={{ color: "var(--text-muted)" }}>{statusLabel}</span>
        <span className="text-xs font-semibold" style={{ color }}>{progress}%</span>
      </div>

      <div className="progress-bar">
        <motion.div
          className="progress-fill"
          initial={{ width: 0 }}
          animate={{ width: `${progress}%` }}
          transition={{ duration: 1, delay: index * 0.1, ease: "easeOut" }}
          style={{ background: color === "#0066FF" ? "var(--brand-gradient)" : `linear-gradient(90deg, ${color}, ${color}88)` }}
        />
      </div>
    </motion.div>
  )
}