"use client"

import { motion } from "framer-motion"
import { Workflow, ChevronRight } from "lucide-react"
import { useLang } from "@/lib/language-provider"

interface WorkflowPreviewProps {
  name: string
  description: string
  status: string
  nodes: { id: string; label: string }[]
  index: number
}

export function WorkflowPreview({ name, description, status, nodes, index }: WorkflowPreviewProps) {
  const { t } = useLang()

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.08 }}
      className="htx-card p-4 cursor-pointer group"
    >
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <Workflow className="w-4 h-4" style={{ color: "var(--brand)" }} />
          <h4 className="text-sm font-semibold" style={{ color: "var(--text-primary)" }}>{name}</h4>
          <span className="badge badge-running text-[10px]">{t(status === "completed" ? "workflows.completed" : "workflows.running")}</span>
        </div>
        <ChevronRight className="w-4 h-4 opacity-0 group-hover:opacity-100 transition-opacity" style={{ color: "var(--text-muted)" }} />
      </div>
      <p className="text-xs mb-2" style={{ color: "var(--text-muted)" }}>{description}</p>
      <div className="flex items-center gap-1 text-xs" style={{ color: "var(--text-muted)" }}>
        <span className="text-[10px] px-1.5 py-0.5 rounded" style={{ background: "var(--bg-surface-hover)", border: "1px solid var(--border)" }}>{nodes[0]?.label}</span>
        {nodes.slice(1).map(n => (
          <span key={n.id} className="flex items-center gap-1">
            <span className="w-1 h-px inline-block" style={{ background: "var(--border-strong)" }} />
            <span className="text-[10px] px-1.5 py-0.5 rounded" style={{ background: "var(--bg-surface-hover)", border: "1px solid var(--border)" }}>{n.label}</span>
          </span>
        ))}
      </div>
    </motion.div>
  )
}
