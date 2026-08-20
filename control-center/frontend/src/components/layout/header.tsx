"use client"

import { Bell, Search, Settings } from "lucide-react"
import { motion } from "framer-motion"
import { useTheme } from "@/lib/theme-provider"
import { useLang } from "@/lib/language-provider"

export function Header() {
  const { theme } = useTheme()
  const { t } = useLang()

  return (
    <header
      className="h-16 border-b flex items-center justify-between px-6 sticky top-0 z-40"
      style={{
        background: theme === "dark" ? "rgba(11, 15, 25, 0.8)" : "rgba(255, 255, 255, 0.8)",
        borderColor: "var(--border)",
        backdropFilter: "blur(12px)",
      }}
    >
      {/* Left: Search */}
      <div className="relative">
        <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2" style={{ color: "var(--text-muted)" }} />
        <input
          type="text"
          placeholder={t("nav.search")}
          className="pl-9 pr-4 py-2 rounded-lg text-sm w-72 focus:outline-none transition-all"
          style={{
            background: "var(--bg-surface-hover)",
            border: "1px solid var(--border)",
            color: "var(--text-primary)",
          }}
        />
      </div>

      {/* Right: Actions */}
      <div className="flex items-center gap-3">
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className="relative p-2 rounded-lg transition-colors"
          style={{ color: "var(--text-muted)" }}
          onMouseEnter={e => e.currentTarget.style.background = "var(--bg-surface-hover)"}
          onMouseLeave={e => e.currentTarget.style.background = "transparent"}
        >
          <Bell className="w-5 h-5" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full" style={{ background: "var(--error)" }} />
        </motion.button>
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className="p-2 rounded-lg transition-colors"
          style={{ color: "var(--text-muted)" }}
          onMouseEnter={e => e.currentTarget.style.background = "var(--bg-surface-hover)"}
          onMouseLeave={e => e.currentTarget.style.background = "transparent"}
        >
          <Settings className="w-5 h-5" />
        </motion.button>
        <div
          className="w-8 h-8 rounded-full flex items-center justify-center text-white text-xs font-bold ml-2"
          style={{ background: "var(--brand-gradient)" }}
        >
          SA
        </div>
      </div>
    </header>
  )
}