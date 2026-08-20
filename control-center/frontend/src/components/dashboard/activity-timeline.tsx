"use client"

import { motion } from "framer-motion"
import { Clock, Video, Palette, TrendingUp } from "lucide-react"
import { useLang } from "@/lib/language-provider"

const zhActivities = [
  { icon: Video, color: "#F59E0B", content: "Video Agent 完成 PropFirm TV 渲染", time: "2 分钟前" },
  { icon: Palette, color: "#0066FF", content: "产品发布管道 — 品牌设计步骤已启动", time: "15 分钟前" },
  { icon: TrendingUp, color: "#10B981", content: "TradeSpan 项目进度更新至 62%", time: "1 小时前" },
  { icon: Clock, color: "#8B5CF6", content: "每日情报简报生成完成", time: "2 小时前" },
  { icon: Video, color: "#EF4444", content: "Content Factory 发布新视频", time: "3 小时前" },
]

const enActivities = [
  { icon: Video, color: "#F59E0B", content: "Video Agent rendered PropFirm TV", time: "2 min ago" },
  { icon: Palette, color: "#0066FF", content: "Product Launch Pipeline — Brand Design started", time: "15 min ago" },
  { icon: TrendingUp, color: "#10B981", content: "TradeSpan project progress at 62%", time: "1 hour ago" },
  { icon: Clock, color: "#8B5CF6", content: "Daily Intelligence Brief generated", time: "2 hours ago" },
  { icon: Video, color: "#EF4444", content: "Content Factory published new video", time: "3 hours ago" },
]

export function ActivityTimeline() {
  const { lang, t } = useLang()
  const activities = lang === "zh" ? zhActivities : enActivities

  return (
    <div className="htx-card p-5">
      <h3 className="text-sm font-semibold mb-4" style={{ color: "var(--text-primary)" }}>
        {t("dashboard.activity")}
      </h3>
      <div className="space-y-0 relative">
        <div className="absolute left-4 top-0 bottom-0 w-px" style={{ background: "var(--border)" }} />
        {activities.map((a, i) => {
          const Icon = a.icon
          return (
            <motion.div
              key={i}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.1 }}
              className="relative flex items-start gap-4 pb-5 last:pb-0"
            >
              <div className="relative z-10 w-8 h-8 rounded-full flex items-center justify-center shrink-0" style={{ background: `${a.color}15`, border: `2px solid ${a.color}20` }}>
                <Icon className="w-3.5 h-3.5" style={{ color: a.color }} />
              </div>
              <div className="flex-1 min-w-0 pt-1">
                <p className="text-xs leading-relaxed" style={{ color: "var(--text-secondary)" }}>{a.content}</p>
                <span className="text-[10px]" style={{ color: "var(--text-muted)" }}>{a.time}</span>
              </div>
            </motion.div>
          )
        })}
      </div>
    </div>
  )
}