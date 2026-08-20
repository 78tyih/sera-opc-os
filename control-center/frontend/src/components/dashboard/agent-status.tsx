"use client"

import { motion } from "framer-motion"
import { Bot, Cpu } from "lucide-react"

interface AgentStatusProps {
  id: string
  name: string
  role: string
  status: string
  model: string
  skills: string[]
  index: number
}

export function AgentStatus({ name, role, status, model, skills, index }: AgentStatusProps) {
  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.08 }}
      className="htx-card p-3 flex items-center gap-3 cursor-pointer"
    >
      <div className="w-9 h-9 rounded-lg flex items-center justify-center shrink-0" style={{ background: "var(--brand-gradient)" }}>
        <Bot className="w-4 h-4 text-white" />
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium" style={{ color: "var(--text-primary)" }}>{name}</span>
          <span className={`status-dot ${status}`} />
        </div>
        <span className="text-xs" style={{ color: "var(--text-muted)" }}>{role}</span>
      </div>
      <div className="hidden md:flex items-center gap-2 text-xs shrink-0" style={{ color: "var(--text-muted)" }}>
        <Cpu className="w-3.5 h-3.5" />
        <span style={{ color: "var(--text-secondary)" }}>{model}</span>
      </div>
      <div className="hidden lg:flex flex-wrap gap-1 shrink-0">
        {skills.slice(0, 2).map(s => (
          <span key={s} className="text-[10px] px-1.5 py-0.5 rounded" style={{ background: "var(--bg-surface-hover)", color: "var(--text-muted)", border: "1px solid var(--border)" }}>
            {s}
          </span>
        ))}
      </div>
    </motion.div>
  )
}