"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import { Plus, FolderKanban } from "lucide-react"
import { ProjectCard } from "@/components/dashboard/project-card"
import { useLang } from "@/lib/language-provider"
import projectsData from "@/data/projects.json"

const categories = [
  { key: "All", label: "cat.all" },
  { key: "Product", label: "cat.product" },
  { key: "Content", label: "cat.content" },
  { key: "Infrastructure", label: "cat.infrastructure" },
  { key: "Business", label: "cat.business" },
]

const statuses = [
  { key: "All", label: "cat.all" },
  { key: "active", label: "status.active" },
  { key: "planning", label: "status.planning" },
]

export default function ProjectsPage() {
  const { t } = useLang()
  const [activeCategory, setActiveCategory] = useState("All")
  const [activeStatus, setActiveStatus] = useState("All")

  const filtered = projectsData.filter(p => {
    if (activeCategory !== "All" && p.category !== activeCategory) return false
    if (activeStatus !== "All" && p.status !== activeStatus) return false
    return true
  })

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold" style={{ color: "var(--text-primary)" }}>{t("projects.title")}</h1>
        </div>
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          className="btn-brand flex items-center gap-2 px-4 py-2 text-sm"
        >
          <Plus className="w-4 h-4" />
          {t("projects.new")}
        </motion.button>
      </div>

      <div className="flex items-center gap-3 flex-wrap">
        <div className="flex items-center gap-1 rounded-lg border p-1" style={{ background: "var(--bg-surface)", borderColor: "var(--border)" }}>
          {categories.map(cat => (
            <button
              key={cat.key}
              onClick={() => setActiveCategory(cat.key)}
              className="px-3 py-1.5 rounded-md text-xs font-medium transition-all"
              style={{
                background: activeCategory === cat.key ? "var(--brand-soft)" : "transparent",
                color: activeCategory === cat.key ? "var(--brand)" : "var(--text-muted)",
              }}
            >
              {t(cat.label)}
            </button>
          ))}
        </div>
        <div className="flex items-center gap-1 rounded-lg border p-1" style={{ background: "var(--bg-surface)", borderColor: "var(--border)" }}>
          {statuses.map(st => (
            <button
              key={st.key}
              onClick={() => setActiveStatus(st.key)}
              className="px-3 py-1.5 rounded-md text-xs font-medium transition-all"
              style={{
                background: activeStatus === st.key ? "var(--brand-soft)" : "transparent",
                color: activeStatus === st.key ? "var(--brand)" : "var(--text-muted)",
              }}
            >
              {t(st.label)}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filtered.map((proj, i) => (
          <ProjectCard key={proj.id} {...proj} index={i} />
        ))}
      </div>

      {filtered.length === 0 && (
        <div className="text-center py-20">
          <FolderKanban className="w-12 h-12 mx-auto mb-4" style={{ color: "var(--border-strong)" }} />
          <p style={{ color: "var(--text-muted)" }}>{t("projects.no-match")}</p>
        </div>
      )}
    </div>
  )
}