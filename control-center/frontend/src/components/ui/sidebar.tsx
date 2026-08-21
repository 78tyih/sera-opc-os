"use client"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { Activity, Bot, BrainCircuit, Building2, Command, DatabaseZap, GitBranch, Languages, Moon, Network, Orbit, Sun, Terminal, Workflow } from "lucide-react"
import { useLang } from "@/lib/language-provider"
import { useTheme } from "@/lib/theme-provider"

const nav = [
  { href: "/dashboard", label: "nav.command", meta: "01", icon: Command },
  { href: "/memory", label: "nav.memory", meta: "02", icon: DatabaseZap },
  { href: "/context", label: "nav.context", meta: "03", icon: BrainCircuit },
  { href: "/department", label: "nav.organization", meta: "04", icon: Building2 },
  { href: "/learning", label: "nav.learning", meta: "05", icon: Orbit },
  // K3 review: /agents and /workflows still exist; keep them reachable from nav.
  { href: "/agents", label: "nav.agents", meta: "06", icon: Bot },
  { href: "/workflows", label: "nav.workflows", meta: "07", icon: Workflow },
  // K3 merge reconciliation: keep e892d6b's kernel console + workflow canvas reachable.
  { href: "/console", label: "nav.console", meta: "08", icon: Terminal },
  { href: "/canvas", label: "nav.canvas", meta: "09", icon: GitBranch },
]
export function Sidebar() {
  const pathname = usePathname()
  const { lang, setLang, t } = useLang()
  const { theme, toggle } = useTheme()
  return <aside className="sera-sidebar">
    <div className="brand-lockup"><div className="brand-mark">S</div><div><strong>SERA <span>/ OS</span></strong><small>AI COMPANY SYSTEM</small></div></div>
    <div className="nav-label">{t("nav.layers")}</div>
    <nav>{nav.map(({ href, label, meta, icon: Icon }) => <Link key={href} href={href} className={pathname === href || (href === "/dashboard" && pathname === "/") ? "active" : ""}><span>{meta}</span><Icon /><b>{t(label)}</b></Link>)}</nav>
    <div className="sidebar-spacer" />
    <div className="system-block"><div><Activity /><span><b>{t("nav.nominal")}</b><small>{t("nav.runtimes")}</small></span></div><div className="health-line"><i /><i /><i /><i /></div></div>
    <button aria-label={t(theme === "dark" ? "nav.light" : "nav.dark")} className="settings-link" onClick={toggle}>{theme === "dark" ? <Sun /> : <Moon />}<span>{t(theme === "dark" ? "nav.light" : "nav.dark")}</span></button>
    <button aria-label={t("nav.language")} className="settings-link" onClick={() => setLang(lang === "zh" ? "en" : "zh")}><Languages /><span>{t("nav.language")}</span></button>
    <Link className="settings-link" href="/projects"><Network /><span>{t("nav.registry")}</span></Link>
    {/* K3 review: removed the dead "System settings" button (no href/onClick). Re-add when wired. */}
  </aside>
}
