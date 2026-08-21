"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"
import { useLang } from "@/lib/language-provider"
import {
  LayoutDashboard,
  FolderKanban,
  Bot,
  Workflow,
  Building2,
  ChevronRight,
  Sun,
  Moon,
  Languages,
  GitBranch,
  Terminal,
} from "lucide-react"
import { useState } from "react"
import { useTheme } from "@/lib/theme-provider"

const navItems = [
  { href: "/dashboard", label: "nav.dashboard", icon: LayoutDashboard },
  { href: "/canvas", label: "nav.canvas", icon: GitBranch },
  { href: "/projects", label: "nav.projects", icon: FolderKanban },
  { href: "/agents", label: "nav.agents", icon: Bot },
  { href: "/workflows", label: "nav.workflows", icon: Workflow },
  { href: "/department", label: "nav.department", icon: Building2 },
  { href: "/console", label: "nav.console", icon: Terminal },
]

export function Sidebar() {
  const pathname = usePathname()
  const { theme, toggle } = useTheme()
  const { lang, setLang, t } = useLang()
  const [collapsed, setCollapsed] = useState(false)

  return (
    <aside
      className="fixed left-0 top-0 h-screen border-r flex flex-col transition-all duration-300 z-50"
      style={{
        width: collapsed ? 60 : 220,
        background: "var(--bg-surface)",
        borderColor: "var(--border)",
      }}
    >
      {/* Logo */}
      <div className="flex items-center gap-3 px-4 border-b shrink-0" style={{ height: 64, borderColor: "var(--border)" }}>
        <div className="w-8 h-8 rounded-lg flex items-center justify-center shrink-0" style={{ background: "var(--brand-gradient)" }}>
          <span className="text-white font-bold text-sm">S</span>
        </div>
        {!collapsed && (
          <div className="flex flex-col">
            <span className="text-sm font-semibold" style={{ color: "var(--text-primary)" }}>Sera OPC OS</span>
            <span className="text-[10px]" style={{ color: "var(--text-muted)" }}>Control Center</span>
          </div>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 py-4 px-2 space-y-1 overflow-y-auto">
        {navItems.map(({ href, label, icon: Icon }) => {
          const isActive = pathname === href || (href === "/dashboard" && pathname === "/")
          return (
            <Link
              key={href}
              href={href}
              className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all duration-200 group"
              style={{
                color: isActive ? "var(--brand)" : "var(--text-muted)",
                background: isActive ? "var(--brand-soft)" : "transparent",
                border: isActive ? `1px solid ${"var(--brand)"}20` : "1px solid transparent",
              }}
              onMouseEnter={e => { if (!isActive) e.currentTarget.style.background = "var(--bg-surface-hover)"; e.currentTarget.style.color = "var(--text-primary)" }}
              onMouseLeave={e => { if (!isActive) { e.currentTarget.style.background = "transparent"; e.currentTarget.style.color = "var(--text-muted)" }}}
            >
              <Icon className="w-5 h-5 shrink-0" style={{ color: isActive ? "var(--brand)" : "inherit" }} />
              {!collapsed && <span className="font-medium">{t(label)}</span>}
            </Link>
          )
        })}
      </nav>

      {/* Theme Toggle */}
      {!collapsed && (
        <div className="px-3 py-1">
          <button
            onClick={toggle}
            className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all duration-200"
            style={{ color: "var(--text-muted)" }}
            onMouseEnter={e => { e.currentTarget.style.background = "var(--bg-surface-hover)"; e.currentTarget.style.color = "var(--text-primary)" }}
            onMouseLeave={e => { e.currentTarget.style.background = "transparent"; e.currentTarget.style.color = "var(--text-muted)" }}
          >
            {theme === "dark" ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
            <span className="font-medium">{lang === "zh" ? (theme === "dark" ? "日间" : "夜间") : (theme === "dark" ? "Light" : "Dark")}</span>
          </button>
        </div>
      )}

      {/* Language Switcher */}
      {!collapsed && (
        <div className="px-3 py-1">
          <button
            onClick={() => setLang(lang === "zh" ? "en" : "zh")}
            className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all duration-200"
            style={{ color: "var(--text-muted)" }}
            onMouseEnter={e => { e.currentTarget.style.background = "var(--bg-surface-hover)"; e.currentTarget.style.color = "var(--text-primary)" }}
            onMouseLeave={e => { e.currentTarget.style.background = "transparent"; e.currentTarget.style.color = "var(--text-muted)" }}
          >
            <Languages className="w-5 h-5" />
            <span className="font-medium">{lang === "zh" ? "English" : "中文"}</span>
          </button>
        </div>
      )}

      {/* Collapse */}
      <div className="p-2 border-t" style={{ borderColor: "var(--border)" }}>
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="w-full flex items-center justify-center p-2 rounded-lg transition-all"
          style={{ color: "var(--text-muted)" }}
          onMouseEnter={e => { e.currentTarget.style.background = "var(--bg-surface-hover)"; e.currentTarget.style.color = "var(--text-primary)" }}
          onMouseLeave={e => { e.currentTarget.style.background = "transparent"; e.currentTarget.style.color = "var(--text-muted)" }}
        >
          <ChevronRight className={cn("w-4 h-4 transition-transform", collapsed ? "" : "rotate-180")} />
        </button>
      </div>

      {/* Bottom status */}
      {!collapsed && (
        <div className="px-4 py-3 border-t" style={{ borderColor: "var(--border)" }}>
          <div className="flex items-center gap-2">
            <span className="status-dot active" />
            <span className="text-xs" style={{ color: "var(--text-muted)" }}>{t("nav.all-operational")}</span>
          </div>
        </div>
      )}
    </aside>
  )
}