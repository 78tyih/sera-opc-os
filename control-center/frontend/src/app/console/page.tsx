"use client"

import { motion } from "framer-motion"
import { Database, GitBranch, Activity, Zap, Clock, Shield, Cpu, Layers } from "lucide-react"
import { useLang } from "@/lib/language-provider"

const KERNEL_STATS = {
  objects: 128,
  relations: 342,
  events: 1042,
  rules: 7,
  experiences: 3,
  decisions: 12,
}

const EVENT_STREAM = [
  { id: "e1", type: "context_built", object: "task.niuniu.brand", summary: "build_context(task.niuniu.brand) → 6,120 tok / 8,000", at: "04:12:08", color: "var(--brand)" },
  { id: "e2", type: "learn", object: "experience.brand.contrast", summary: "learn() — root_cause: 品牌对比度不足导致转化低", at: "04:11:52", color: "var(--success)" },
  { id: "e3", type: "object_created", object: "decision.niuniu.logo", summary: "新 Logo 决策记录写入", at: "04:10:31", color: "#F59E0B" },
  { id: "e4", type: "staging_pass", object: "project.niuniu", summary: "Staging Gate 6/6 验证通过", at: "04:09:15", color: "var(--success)" },
  { id: "e5", type: "context_built", object: "task.tradespan.video", summary: "build_context(task.tradespan.video) → 命中 Task A 根因", at: "04:08:00", color: "var(--brand)" },
  { id: "e6", type: "learn", object: "experience.landing.trust", summary: "learn() — root_cause: 缺信任徽章/真实数据", at: "03:45:22", color: "var(--success)" },
  { id: "e7", type: "rule_promoted", object: "rule.financial.trust", summary: "Experience 晋升为 Rule (3次验证通过)", at: "03:45:10", color: "#8B5CF6" },
  { id: "e8", type: "access", object: "project.tradespan", summary: "Context Governor 引用 TradeSpan 项目", at: "03:44:58", color: "var(--text-muted)" },
  { id: "e9", type: "object_created", object: "project.propfirmtv", summary: "PropFirm TV 项目初始化", at: "02:30:00", color: "#F59E0B" },
  { id: "e10", type: "status_changed", object: "agent.video", summary: "Video Agent 状态: idle → active", at: "02:15:00", color: "var(--text-muted)" },
]

const KERNEL_LAYERS = [
  { label: "Learning OS", desc: "经验 → 规则 → 更好的上下文", icon: Layers, color: "#8B5CF6" },
  { label: "Context OS", desc: "此刻该知道什么", icon: Cpu, color: "var(--brand)" },
  { label: "Organization OS", desc: "员工是谁、如何分配", icon: Shield, color: "#10B981" },
  { label: "Workflow OS", desc: "业务流程如何串联", icon: GitBranch, color: "#F59E0B" },
  { label: "Execution OS", desc: "工具与机器落地", icon: Zap, color: "#EC4899" },
]

export default function ConsolePage() {
  const { t } = useLang()

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-lg font-bold" style={{ color: "var(--text-primary)" }}>总控台</h1>
        <p className="text-sm mt-1" style={{ color: "var(--text-muted)" }}>系统全局监控 · Kernel V0 实时数据</p>
      </div>

      {/* Kernel Stats */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
        {[
          { label: "objects", value: KERNEL_STATS.objects, sub: "记忆对象", icon: Database, color: "var(--brand)" },
          { label: "relations", value: KERNEL_STATS.relations, sub: "关系", icon: GitBranch, color: "#10B981" },
          { label: "events", value: KERNEL_STATS.events, sub: "事件流水", icon: Activity, color: "#F59E0B" },
          { label: "rules", value: KERNEL_STATS.rules, sub: "组织规则", icon: Shield, color: "#8B5CF6" },
          { label: "experiences", value: KERNEL_STATS.experiences, sub: "经验", icon: Zap, color: "#EC4899" },
          { label: "decisions", value: KERNEL_STATS.decisions, sub: "决策", icon: Clock, color: "var(--text-muted)" },
        ].map((stat, i) => {
          const Icon = stat.icon
          return (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.06 }}
              className="htx-card p-4"
            >
              <div className="flex items-center gap-2 mb-2">
                <Icon className="w-4 h-4" style={{ color: stat.color }} />
                <span className="text-[10px] uppercase tracking-wider" style={{ color: "var(--text-muted)" }}>{stat.sub}</span>
              </div>
              <span className="text-2xl font-bold" style={{ color: stat.color }}>{stat.value}</span>
            </motion.div>
          )
        })}
      </div>

      {/* Architecture Layers */}
      <div className="rounded-xl border p-5" style={{ background: "var(--bg-surface)", borderColor: "var(--border)" }}>
        <div className="flex items-center gap-2 mb-4">
          <Layers className="w-4 h-4" style={{ color: "var(--brand)" }} />
          <span className="text-xs font-semibold uppercase tracking-wider" style={{ color: "var(--text-secondary)" }}>内核层级</span>
          <span className="text-[10px] ml-auto" style={{ color: "var(--text-muted)" }}>任何 Agent 接入即继承全部层</span>
        </div>
        <div className="flex flex-col gap-2">
          {KERNEL_LAYERS.map((layer, i) => {
            const Icon = layer.icon
            return (
              <div key={layer.label} className="flex items-center gap-3 p-3 rounded-lg" style={{ background: "var(--bg-base)" }}>
                <div className="w-8 h-8 rounded-lg flex items-center justify-center shrink-0" style={{ background: `${layer.color}15` }}>
                  <Icon className="w-4 h-4" style={{ color: layer.color }} />
                </div>
                <div>
                  <span className="text-sm font-medium" style={{ color: "var(--text-primary)" }}>{layer.label}</span>
                  <span className="text-xs ml-2" style={{ color: "var(--text-muted)" }}>{layer.desc}</span>
                </div>
                <span className="ml-auto text-[10px] px-2 py-0.5 rounded font-medium" style={{ background: `${layer.color}15`, color: layer.color }}>L{i + 1}</span>
              </div>
            )
          })}
        </div>
      </div>

      {/* Event Stream */}
      <div className="rounded-xl border overflow-hidden" style={{ background: "var(--bg-surface)", borderColor: "var(--border)" }}>
        <div className="flex items-center gap-2 px-4 py-3 border-b" style={{ borderColor: "var(--border)" }}>
          <Activity className="w-4 h-4" style={{ color: "var(--brand)" }} />
          <span className="text-xs font-semibold uppercase tracking-wider" style={{ color: "var(--text-secondary)" }}>Event Stream</span>
          <span className="text-[10px] ml-2" style={{ color: "var(--text-muted)" }}>append-only</span>
          <div className="ml-auto flex items-center gap-2">
            <span className="w-2 h-2 rounded-full" style={{ background: "var(--success)", animation: "pulse 2s infinite" }} />
            <span className="text-[10px]" style={{ color: "var(--success)" }}>Live</span>
          </div>
        </div>
        <div className="divide-y" style={{ borderColor: "var(--border)" }}>
          {EVENT_STREAM.map((evt, i) => (
            <motion.div
              key={evt.id}
              initial={{ opacity: 0, x: -8 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.03 }}
              className="flex items-start gap-3 px-4 py-2.5"
            >
              <span className="text-[10px] font-mono w-14 shrink-0 pt-0.5" style={{ color: "var(--text-muted)" }}>{evt.at}</span>
              <span className="text-[10px] px-1.5 py-0.5 rounded font-medium shrink-0" style={{ background: `${evt.color}15`, color: evt.color }}>
                {evt.type}
              </span>
              <div className="min-w-0 flex-1">
                <span className="text-xs" style={{ color: "var(--text-secondary)" }}>{evt.summary}</span>
              </div>
              <span className="text-[10px] font-mono shrink-0" style={{ color: "var(--text-muted)" }}>{evt.object}</span>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  )
}