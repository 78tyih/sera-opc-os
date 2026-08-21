# Control Center V2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Upgrade Sera OPC OS Control Center from mock JSON frontend to real API-backed, deployable console with CMS data source and new pages.

**Architecture:** 
- Phase 1: Vercel deployment with custom domain (quick win, get live URL)
- Phase 2: Next.js API Routes layer that serves data from JSON → later switches to real backend
- Phase 3: Tencent Docs / WeCom sheets as CMS data source for non-developer content editing
- Phase 4: New pages (Settings, Logs, Agent Detail, Workflow Editor)

**Tech Stack:** Next.js 16 / React 19 / Tailwind CSS v4 / shadcn/ui / Framer Motion / React Flow / Vercel

**Current State:** 5 pages with mock JSON data, Vercel CLI installed but not linked

---

## Phase 1: Vercel Deployment + Custom Domain

### Task 1.1: Initialize Vercel Project

**Files:**
- Modify: `vercel.json` (create)
- Modify: `next.config.js` (create if needed)

- [ ] **Step 1: Create vercel.json**

```json
{
  "framework": "nextjs",
  "buildCommand": "next build",
  "outputDirectory": ".next",
  "installCommand": "npm install"
}
```

Run: `cat > /Users/a1234/sera-agent-console/vercel.json << 'EOF'
{
  "framework": "nextjs",
  "buildCommand": "next build",
  "outputDirectory": ".next",
  "installCommand": "npm install"
}
EOF`

- [ ] **Step 2: Link Vercel project**

Run: `cd /Users/a1234/sera-agent-console && vercel link --yes`
Expected: Project linked to Vercel account

- [ ] **Step 3: Initial deploy to preview**

Run: `cd /Users/a1234/sera-agent-console && vercel deploy`
Expected: Preview URL returned (e.g., https://sera-agent-console-xxx.vercel.app)

- [ ] **Step 4: Promote to production**

Run: `cd /Users/a1234/sera-agent-console && vercel --prod`
Expected: Production URL (e.g., https://sera-agent-console.vercel.app)

- [ ] **Step 5: Configure custom domain**

Run: `cd /Users/a1234/sera-agent-console && vercel domains add sera.ai` (or user's preferred domain)
Expected: Domain verification instructions

- [ ] **Step 6: Commit**

```bash
cd /Users/a1234/sera-agent-console && git add vercel.json && git commit -m "chore: add vercel config"
```

---

## Phase 2: Real API Backend (Next.js API Routes)

### Task 2.1: Create API Route Architecture

**Files:**
- Create: `src/app/api/agents/route.ts`
- Create: `src/app/api/projects/route.ts`
- Create: `src/app/api/workflows/route.ts`
- Create: `src/app/api/departments/route.ts`
- Create: `src/lib/api.ts`

- [ ] **Step 1: Create agents API route**

```ts
// src/app/api/agents/route.ts
import { NextResponse } from "next/server"
import agentsData from "@/data/agents.json"

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url)
  const department = searchParams.get("department")
  const status = searchParams.get("status")

  let data = agentsData
  if (department) data = data.filter(a => a.department === department)
  if (status) data = data.filter(a => a.status === status)

  return NextResponse.json({ agents: data, total: data.length })
}
```

- [ ] **Step 2: Create projects API route**

```ts
// src/app/api/projects/route.ts
import { NextResponse } from "next/server"
import projectsData from "@/data/projects.json"

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url)
  const category = searchParams.get("category")
  const status = searchParams.get("status")

  let data = projectsData
  if (category) data = data.filter(p => p.category === category)
  if (status) data = data.filter(p => p.status === status)

  return NextResponse.json({ projects: data, total: data.length })
}
```

- [ ] **Step 3: Create workflows API route**

```ts
// src/app/api/workflows/route.ts
import { NextResponse } from "next/server"
import workflowsData from "@/data/workflows.json"

export async function GET() {
  return NextResponse.json({ workflows: workflowsData.workflows })
}
```

- [ ] **Step 4: Create departments API route**

```ts
// src/app/api/departments/route.ts
import { NextResponse } from "next/server"
import departmentsData from "@/data/departments.json"

export async function GET() {
  return NextResponse.json({ departments: departmentsData })
}
```

- [ ] **Step 5: Create API client lib**

```ts
// src/lib/api.ts
const API_BASE = process.env.NEXT_PUBLIC_API_BASE || ""

async function fetchJSON<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}/api${path}`)
  if (!res.ok) throw new Error(`API error: ${res.status}`)
  return res.json()
}

export const api = {
  agents: (params?: Record<string, string>) => {
    const qs = params ? "?" + new URLSearchParams(params).toString() : ""
    return fetchJSON<{ agents: any[]; total: number }>(`/agents${qs}`)
  },
  projects: (params?: Record<string, string>) => {
    const qs = params ? "?" + new URLSearchParams(params).toString() : ""
    return fetchJSON<{ projects: any[]; total: number }>(`/projects${qs}`)
  },
  workflows: () => fetchJSON<{ workflows: any[] }>("/workflows"),
  departments: () => fetchJSON<{ departments: any[] }>("/departments"),
}
```

- [ ] **Step 6: Add API mode env var to .env.local**

```bash
echo "NEXT_PUBLIC_DATA_SOURCE=mock" >> /Users/a1234/sera-agent-console/.env.local
```

- [ ] **Step 7: Commit**

```bash
cd /Users/a1234/sera-agent-console && git add src/app/api/ src/lib/api.ts && git commit -m "feat: add API route layer with mock data source"
```

---

### Task 2.2: Migrate Pages to Use API

**Files:**
- Modify: `src/app/dashboard/page.tsx`
- Modify: `src/app/agents/page.tsx`
- Modify: `src/app/projects/page.tsx`
- Modify: `src/app/workflows/page.tsx`
- Modify: `src/app/department/page.tsx`

- [ ] **Step 1: Create useData custom hook**

```ts
// src/lib/use-data.ts
"use client"

import { useState, useEffect } from "react"

export function useData<T>(fetcher: () => Promise<T>) {
  const [data, setData] = useState<T | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    fetcher()
      .then(setData)
      .catch(setError)
      .finally(() => setLoading(false))
  }, [])

  return { data, loading, error }
}
```

- [ ] **Step 2: Update dashboard page to fetch from API**

```tsx
// In src/app/dashboard/page.tsx, add:
import { api } from "@/lib/api"
import { useData } from "@/lib/use-data"

// Replace static imports from data/ with:
const { data: agentsData, loading } = useData(() => api.agents({ status: "active" }))
const { data: projectsData } = useData(() => api.projects())
const { data: workflowsData } = useData(() => api.workflows())
```

- [ ] **Step 3: Update agents page**

Same pattern — replace `import agentsData from "@/data/agents.json"` with API call

- [ ] **Step 4: Update projects page**

Same pattern

- [ ] **Step 5: Update workflows page**

Same pattern

- [ ] **Step 6: Update department page**

Same pattern

- [ ] **Step 7: Build and verify**

Run: `cd /Users/a1234/sera-agent-console && npm run build`
Expected: Build succeeds with no errors

- [ ] **Step 8: Commit**

```bash
cd /Users/a1234/sera-agent-console && git add -A && git commit -m "feat: migrate pages from direct JSON import to API layer"
```

---

## Phase 3: Data Source Upgrade (Tencent Docs / WeCom Sheets)

### Task 3.1: Create Tencent Docs Sheet Adapter

**Files:**
- Create: `src/lib/data-sources/tencent-docs.ts`
- Create: `src/lib/data-sources/types.ts`
- Create: `src/lib/data-sources/index.ts`

- [ ] **Step 1: Define data source types**

```ts
// src/lib/data-sources/types.ts
export type DataSourceType = "mock" | "tencent-docs" | "wecom"

export interface DataSourceConfig {
  type: DataSourceType
  apiKey?: string
  appId?: string
  sheetId?: string
}

export interface AgentRecord {
  id: string
  name: string
  department: string
  role: string
  skills: string
  tools: string
  model: string
  status: string
  description: string
}

export interface ProjectRecord {
  id: string
  name: string
  category: string
  status: string
  priority: string
  progress: number
  description: string
  agents: string
}

export interface WorkflowRecord {
  id: string
  name: string
  description: string
  nodes: string  // JSON string
  edges: string  // JSON string
  lastRun: string
  status: string
}

export interface DepartmentRecord {
  id: string
  description: string
  agents: string  // JSON string array
  projects: string  // JSON string array
}
```

- [ ] **Step 2: Create Tencent Docs adapter**

```ts
// src/lib/data-sources/tencent-docs.ts
import type { DataSourceConfig, AgentRecord, ProjectRecord, WorkflowRecord, DepartmentRecord } from "./types"

export class TencentDocsAdapter {
  private config: DataSourceConfig

  constructor(config: DataSourceConfig) {
    this.config = config
  }

  async fetchSheet(sheetId: string, range: string): Promise<any[][]> {
    // In production, this would call Tencent Docs Open API
    // For now, return empty array — will be implemented when API keys are configured
    console.warn("Tencent Docs adapter: API keys not configured")
    return []
  }

  async getAgents(): Promise<AgentRecord[]> {
    const rows = await this.fetchSheet(this.config.sheetId || "", "agents!A2:I")
    return rows.map(row => ({
      id: row[0], name: row[1], department: row[2], role: row[3],
      skills: row[4], tools: row[5], model: row[6], status: row[7], description: row[8],
    }))
  }

  async getProjects(): Promise<ProjectRecord[]> {
    const rows = await this.fetchSheet(this.config.sheetId || "", "projects!A2:H")
    return rows.map(row => ({
      id: row[0], name: row[1], category: row[2], status: row[3],
      priority: row[4], progress: Number(row[5]), description: row[6], agents: row[7],
    }))
  }

  async getWorkflows(): Promise<WorkflowRecord[]> {
    const rows = await this.fetchSheet(this.config.sheetId || "", "workflows!A2:G")
    return rows.map(row => ({
      id: row[0], name: row[1], description: row[2],
      nodes: row[3], edges: row[4], lastRun: row[5], status: row[6],
    }))
  }

  async getDepartments(): Promise<DepartmentRecord[]> {
    const rows = await this.fetchSheet(this.config.sheetId || "", "departments!A2:D")
    return rows.map(row => ({
      id: row[0], description: row[1], agents: row[2], projects: row[3],
    }))
  }
}
```

- [ ] **Step 3: Create data source factory**

```ts
// src/lib/data-sources/index.ts
import { TencentDocsAdapter } from "./tencent-docs"
import type { DataSourceConfig, DataSourceType } from "./types"

export function createDataSource(config: DataSourceConfig) {
  switch (config.type) {
    case "tencent-docs":
      return new TencentDocsAdapter(config)
    default:
      throw new Error(`Unknown data source type: ${config.type}`)
  }
}

export function getDataSourceConfig(): DataSourceConfig {
  return {
    type: (process.env.NEXT_PUBLIC_DATA_SOURCE as DataSourceType) || "mock",
    apiKey: process.env.TENCENT_DOCS_API_KEY,
    appId: process.env.TENCENT_DOCS_APP_ID,
    sheetId: process.env.TENCENT_DOCS_SHEET_ID,
  }
}
```

- [ ] **Step 4: Update API routes to support data source switching**

```ts
// Modify src/app/api/agents/route.ts to use data source:
import { NextResponse } from "next/server"
import { getDataSourceConfig, createDataSource } from "@/lib/data-sources"
import agentsData from "@/data/agents.json"

export async function GET(request: Request) {
  const config = getDataSourceConfig()
  const { searchParams } = new URL(request.url)

  if (config.type !== "mock") {
    try {
      const source = createDataSource(config)
      const agents = await source.getAgents()
      return NextResponse.json({ agents, total: agents.length })
    } catch (e) {
      console.warn("Data source failed, falling back to mock", e)
    }
  }

  let data = agentsData
  if (searchParams.get("department")) data = data.filter(a => a.department === searchParams.get("department"))
  if (searchParams.get("status")) data = data.filter(a => a.status === searchParams.get("status"))
  return NextResponse.json({ agents: data, total: data.length })
}
```

- [ ] **Step 5: Add environment variables template**

```bash
cat >> /Users/a1234/sera-agent-console/.env.example << 'EOF'
# Data Source
NEXT_PUBLIC_DATA_SOURCE=mock
TENCENT_DOCS_API_KEY=
TENCENT_DOCS_APP_ID=
TENCENT_DOCS_SHEET_ID=
EOF
```

- [ ] **Step 6: Commit**

```bash
cd /Users/a1234/sera-agent-console && git add src/lib/data-sources/ .env.example && git commit -m "feat: add data source abstraction layer with Tencent Docs adapter"
```

---

## Phase 4: New Pages

### Task 4.1: Settings Page (/settings)

**Files:**
- Create: `src/app/settings/page.tsx`
- Modify: `src/components/layout/header.tsx` (add settings link to user menu)

- [ ] **Step 1: Create settings page**

```tsx
// src/app/settings/page.tsx
"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import { Settings, Globe, Moon, Sun, Database, RefreshCw, Save } from "lucide-react"
import { useLang } from "@/lib/language-provider"
import { useTheme } from "@/lib/theme-provider"

export default function SettingsPage() {
  const { t, lang, setLang } = useLang()
  const { theme, setTheme } = useTheme()
  const [dataSource, setDataSource] = useState("mock")
  const [saved, setSaved] = useState(false)

  const handleSave = () => {
    localStorage.setItem("sera-data-source", dataSource)
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  return (
    <div className="max-w-2xl space-y-8">
      <div>
        <h1 className="text-2xl font-bold" style={{ color: "var(--text-primary)" }}>{t("nav.settings")}</h1>
        <p className="text-sm mt-1" style={{ color: "var(--text-muted)" }}>{t("settings.subtitle")}</p>
      </div>

      {/* Language */}
      <div className="htx-card p-5">
        <div className="flex items-center gap-3 mb-4">
          <Globe className="w-5 h-5" style={{ color: "var(--brand)" }} />
          <h3 className="text-sm font-semibold" style={{ color: "var(--text-primary)" }}>{t("settings.language")}</h3>
        </div>
        <div className="flex gap-2">
          <button onClick={() => setLang("zh")}
            className="px-4 py-2 rounded-lg text-sm font-medium transition-all"
            style={{ background: lang === "zh" ? "var(--brand-soft)" : "var(--bg-surface)", color: lang === "zh" ? "var(--brand)" : "var(--text-muted)", border: "1px solid", borderColor: lang === "zh" ? "rgba(0,102,255,0.2)" : "var(--border)" }}>
            中文
          </button>
          <button onClick={() => setLang("en")}
            className="px-4 py-2 rounded-lg text-sm font-medium transition-all"
            style={{ background: lang === "en" ? "var(--brand-soft)" : "var(--bg-surface)", color: lang === "en" ? "var(--brand)" : "var(--text-muted)", border: "1px solid", borderColor: lang === "en" ? "rgba(0,102,255,0.2)" : "var(--border)" }}>
            English
          </button>
        </div>
      </div>

      {/* Theme */}
      <div className="htx-card p-5">
        <div className="flex items-center gap-3 mb-4">
          {theme === "dark" ? <Moon className="w-5 h-5" style={{ color: "var(--brand)" }} /> : <Sun className="w-5 h-5" style={{ color: "var(--brand)" }} />}
          <h3 className="text-sm font-semibold" style={{ color: "var(--text-primary)" }}>{t("settings.theme")}</h3>
        </div>
        <div className="flex gap-2">
          <button onClick={() => setTheme("dark")}
            className="px-4 py-2 rounded-lg text-sm font-medium transition-all"
            style={{ background: theme === "dark" ? "var(--brand-soft)" : "var(--bg-surface)", color: theme === "dark" ? "var(--brand)" : "var(--text-muted)", border: "1px solid", borderColor: theme === "dark" ? "rgba(0,102,255,0.2)" : "var(--border)" }}>
            {t("settings.dark")}
          </button>
          <button onClick={() => setTheme("light")}
            className="px-4 py-2 rounded-lg text-sm font-medium transition-all"
            style={{ background: theme === "light" ? "var(--brand-soft)" : "var(--bg-surface)", color: theme === "light" ? "var(--brand)" : "var(--text-muted)", border: "1px solid", borderColor: theme === "light" ? "rgba(0,102,255,0.2)" : "var(--border)" }}>
            {t("settings.light")}
          </button>
        </div>
      </div>

      {/* Data Source */}
      <div className="htx-card p-5">
        <div className="flex items-center gap-3 mb-4">
          <Database className="w-5 h-5" style={{ color: "var(--brand)" }} />
          <h3 className="text-sm font-semibold" style={{ color: "var(--text-primary)" }}>{t("settings.data-source")}</h3>
        </div>
        <select value={dataSource} onChange={e => setDataSource(e.target.value)}
          className="w-full px-3 py-2 rounded-lg text-sm"
          style={{ background: "var(--bg-surface)", color: "var(--text-primary)", border: "1px solid var(--border)" }}>
          <option value="mock">Mock (JSON)</option>
          <option value="tencent-docs">Tencent Docs</option>
          <option value="wecom">WeCom Sheets</option>
        </select>
        <button onClick={handleSave}
          className="mt-3 flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium"
          style={{ background: "var(--brand-gradient)", color: "white" }}>
          {saved ? <RefreshCw className="w-4 h-4" /> : <Save className="w-4 h-4" />}
          {saved ? t("settings.saved") : t("settings.save")}
        </button>
      </div>
    </div>
  )
}
```

- [ ] **Step 2: Add settings i18n keys**

```ts
// In src/lib/i18n.ts, add to dict:
"nav.settings": { zh: "设置", en: "Settings" },
"settings.subtitle": { zh: "系统配置", en: "System Configuration" },
"settings.language": { zh: "语言", en: "Language" },
"settings.theme": { zh: "主题", en: "Theme" },
"settings.dark": { zh: "深色", en: "Dark" },
"settings.light": { zh: "浅色", en: "Light" },
"settings.data-source": { zh: "数据源", en: "Data Source" },
"settings.save": { zh: "保存", en: "Save" },
"settings.saved": { zh: "已保存", en: "Saved" },
```

- [ ] **Step 3: Add Settings to sidebar navigation**

```tsx
// In src/components/ui/sidebar.tsx, add Settings link
// Add { label: "nav.settings", icon: Settings, href: "/settings" } to navItems
```

- [ ] **Step 4: Build and verify**

Run: `cd /Users/a1234/sera-agent-console && npm run build`
Expected: Build succeeds

- [ ] **Step 5: Commit**

```bash
cd /Users/a1234/sera-agent-console && git add -A && git commit -m "feat: add settings page with language, theme, and data source config"
```

---

### Task 4.2: Agent Detail Page (/agents/[id])

**Files:**
- Create: `src/app/agents/[id]/page.tsx`
- Create: `src/app/agents/[id]/loading.tsx`

- [ ] **Step 1: Create agent detail page**

```tsx
// src/app/agents/[id]/page.tsx
"use client"

import { useParams, useRouter } from "next/navigation"
import { motion } from "framer-motion"
import { ArrowLeft, Bot, Cpu, Wrench, Activity, Clock, CheckCircle2, AlertCircle } from "lucide-react"
import { useLang, useData } from "@/lib/language-provider"
import { api } from "@/lib/api"
import { useData } from "@/lib/use-data"

export default function AgentDetailPage() {
  const { id } = useParams<{ id: string }>()
  const router = useRouter()
  const { t, tt } = useLang()
  const { data: agentsData, loading } = useData(() => api.agents())
  const agent = agentsData?.agents.find(a => a.id === id)

  if (loading) return <AgentDetailSkeleton />
  if (!agent) return <div className="text-center py-20" style={{ color: "var(--text-muted)" }}>Agent not found</div>

  return (
    <div className="max-w-4xl space-y-6">
      <button onClick={() => router.back()}
        className="flex items-center gap-2 text-sm" style={{ color: "var(--text-muted)" }}>
        <ArrowLeft className="w-4 h-4" /> Back
      </button>

      {/* Header */}
      <div className="htx-card p-6">
        <div className="flex items-start gap-4">
          <div className="w-14 h-14 rounded-xl flex items-center justify-center" style={{ background: "var(--brand-gradient)" }}>
            <Bot className="w-7 h-7 text-white" />
          </div>
          <div className="flex-1">
            <h1 className="text-xl font-bold" style={{ color: "var(--text-primary)" }}>{tt(agent.name)}</h1>
            <p className="text-sm" style={{ color: "var(--text-muted)" }}>{tt(agent.role)}</p>
            <div className="flex items-center gap-4 mt-2 text-xs" style={{ color: "var(--text-muted)" }}>
              <span className="flex items-center gap-1"><Cpu className="w-3 h-3" /> {agent.model}</span>
              <span className={`status-dot ${agent.status}`} />
              {agent.status === "active" ? t("agents.active") : t("agents.idle")}
            </div>
          </div>
        </div>
      </div>

      {/* Skills & Tools */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="htx-card p-5">
          <h3 className="text-sm font-semibold mb-3" style={{ color: "var(--text-primary)" }}>{t("agents.skills")}</h3>
          <div className="flex flex-wrap gap-2">
            {agent.skills.map(s => (
              <span key={s} className="px-3 py-1 rounded-lg text-xs" style={{ background: "var(--bg-surface-hover)", color: "var(--text-secondary)", border: "1px solid var(--border)" }}>
                {tt(s)}
              </span>
            ))}
          </div>
        </div>
        <div className="htx-card p-5">
          <h3 className="text-sm font-semibold mb-3" style={{ color: "var(--text-primary)" }}>{t("agents.tools")}</h3>
          <div className="flex flex-wrap gap-2">
            {agent.tools.map(t => (
              <span key={t} className="px-3 py-1 rounded-lg text-xs" style={{ background: "var(--bg-surface-hover)", color: "var(--text-secondary)", border: "1px solid var(--border)" }}>
                {t}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* Description */}
      <div className="htx-card p-5">
        <h3 className="text-sm font-semibold mb-2" style={{ color: "var(--text-primary)" }}>{t("agents.description")}</h3>
        <p className="text-sm" style={{ color: "var(--text-secondary)" }}>{tt(agent.description)}</p>
      </div>

      {/* Activity History */}
      <div className="htx-card p-5">
        <h3 className="text-sm font-semibold mb-4" style={{ color: "var(--text-primary)" }}>{t("agents.activity")}</h3>
        <div className="space-y-3">
          {[1,2,3,4,5].map(i => (
            <div key={i} className="flex items-center gap-3 p-3 rounded-lg" style={{ background: "var(--bg-base)" }}>
              <div className="w-8 h-8 rounded-lg flex items-center justify-center" style={{ background: i % 2 === 0 ? "rgba(16,185,129,0.1)" : "rgba(0,102,255,0.1)" }}>
                {i % 2 === 0 ? <CheckCircle2 className="w-4 h-4" style={{ color: "var(--success)" }} /> : <Activity className="w-4 h-4" style={{ color: "var(--brand)" }} />}
              </div>
              <div className="flex-1">
                <div className="text-sm" style={{ color: "var(--text-primary)" }}>
                  {i % 2 === 0 ? "Completed task: " : "Processing: "} Task #{i}
                </div>
                <div className="text-xs" style={{ color: "var(--text-muted)" }}>
                  {new Date(Date.now() - i * 3600000).toLocaleString()}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

function AgentDetailSkeleton() {
  return (
    <div className="max-w-4xl space-y-6 animate-pulse">
      <div className="h-8 w-24 rounded" style={{ background: "var(--bg-surface)" }} />
      <div className="h-32 rounded-xl" style={{ background: "var(--bg-surface)" }} />
      <div className="grid grid-cols-2 gap-4">
        <div className="h-40 rounded-xl" style={{ background: "var(--bg-surface)" }} />
        <div className="h-40 rounded-xl" style={{ background: "var(--bg-surface)" }} />
      </div>
    </div>
  )
}
```

- [ ] **Step 2: Add i18n keys**

```ts
// In src/lib/i18n.ts:
"agents.skills": { zh: "技能", en: "Skills" },
"agents.tools": { zh: "工具", en: "Tools" },
"agents.description": { zh: "描述", en: "Description" },
"agents.activity": { zh: "活动历史", en: "Activity History" },
```

- [ ] **Step 3: Make agent cards clickable in agents page**

```tsx
// In src/app/agents/page.tsx, wrap AgentCard with:
import { useRouter } from "next/navigation"
const router = useRouter()
// Add onClick to agent card:
onClick={() => router.push(`/agents/${agent.id}`)}
```

- [ ] **Step 4: Build and verify**

Run: `cd /Users/a1234/sera-agent-console && npm run build`
Expected: Build succeeds

- [ ] **Step 5: Commit**

```bash
cd /Users/a1234/sera-agent-console && git add -A && git commit -m "feat: add agent detail page with activity history"
```

---

### Task 4.3: Logs Page (/logs)

**Files:**
- Create: `src/app/logs/page.tsx`

- [ ] **Step 1: Create logs page**

```tsx
// src/app/logs/page.tsx
"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import { Search, Filter, ChevronDown, Activity, AlertCircle, CheckCircle2, Loader2, Clock } from "lucide-react"
import { useLang } from "@/lib/language-provider"

const mockLogs = Array.from({ length: 50 }, (_, i) => ({
  id: `log-${i}`,
  level: ["info", "warn", "error", "success"][Math.floor(Math.random() * 4)],
  message: [
    "Agent Product Agent completed task: Market Research #42",
    "Workflow Product Launch Pipeline executed successfully",
    "API rate limit approaching for Tencent Docs adapter",
    "Agent Brand Agent started processing: Brand Identity Review",
    "Data source switched from mock to tencent-docs",
    "Scheduled task Daily Intelligence Brief triggered",
    "Connection to Sera OPC OS backend established",
    "Cache refreshed for agents data (12 items)",
  ][Math.floor(Math.random() * 8)],
  source: ["system", "agent", "api", "workflow"][Math.floor(Math.random() * 4)],
  timestamp: new Date(Date.now() - i * 1800000).toISOString(),
}))

const levelIcons: Record<string, React.ElementType> = {
  info: Activity, warn: AlertCircle, error: AlertCircle, success: CheckCircle2,
}
const levelColors: Record<string, string> = {
  info: "var(--brand)", warn: "#F59E0B", error: "#EF4444", success: "var(--success)",
}

export default function LogsPage() {
  const { t } = useLang()
  const [search, setSearch] = useState("")
  const [levelFilter, setLevelFilter] = useState("all")
  const [sourceFilter, setSourceFilter] = useState("all")

  const filtered = mockLogs.filter(log => {
    if (levelFilter !== "all" && log.level !== levelFilter) return false
    if (sourceFilter !== "all" && log.source !== sourceFilter) return false
    if (search && !log.message.toLowerCase().includes(search.toLowerCase())) return false
    return true
  })

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold" style={{ color: "var(--text-primary)" }}>{t("logs.title")}</h1>
        <p className="text-sm mt-1" style={{ color: "var(--text-muted)" }}>{t("logs.subtitle")}</p>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-3 flex-wrap">
        <div className="relative flex-1 max-w-xs">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4" style={{ color: "var(--text-muted)" }} />
          <input
            type="text"
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder={t("logs.search")}
            className="w-full pl-9 pr-3 py-2 rounded-lg text-sm"
            style={{ background: "var(--bg-surface)", color: "var(--text-primary)", border: "1px solid var(--border)" }}
          />
        </div>
        <select value={levelFilter} onChange={e => setLevelFilter(e.target.value)}
          className="px-3 py-2 rounded-lg text-sm" style={{ background: "var(--bg-surface)", color: "var(--text-primary)", border: "1px solid var(--border)" }}>
          <option value="all">{t("logs.all-levels")}</option>
          <option value="info">Info</option>
          <option value="warn">Warning</option>
          <option value="error">Error</option>
          <option value="success">Success</option>
        </select>
        <select value={sourceFilter} onChange={e => setSourceFilter(e.target.value)}
          className="px-3 py-2 rounded-lg text-sm" style={{ background: "var(--bg-surface)", color: "var(--text-primary)", border: "1px solid var(--border)" }}>
          <option value="all">{t("logs.all-sources")}</option>
          <option value="system">System</option>
          <option value="agent">Agent</option>
          <option value="api">API</option>
          <option value="workflow">Workflow</option>
        </select>
      </div>

      {/* Logs */}
      <div className="htx-card overflow-hidden">
        <div className="divide-y" style={{ borderColor: "var(--border)" }}>
          {filtered.map((log, i) => {
            const Icon = levelIcons[log.level]
            const color = levelColors[log.level]
            return (
              <motion.div
                key={log.id}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.02 }}
                className="flex items-start gap-3 p-3"
                style={{ background: log.level === "error" ? "rgba(239,68,68,0.03)" : "transparent" }}
              >
                <Icon className="w-4 h-4 mt-0.5 shrink-0" style={{ color }} />
                <div className="flex-1 min-w-0">
                  <div className="text-sm" style={{ color: "var(--text-primary)" }}>{log.message}</div>
                  <div className="text-xs mt-0.5" style={{ color: "var(--text-muted)" }}>
                    {new Date(log.timestamp).toLocaleString()} · {log.source}
                  </div>
                </div>
              </motion.div>
            )
          })}
        </div>
      </div>

      {filtered.length === 0 && (
        <div className="text-center py-16" style={{ color: "var(--text-muted)" }}>
          {t("logs.no-logs")}
        </div>
      )}
    </div>
  )
}
```

- [ ] **Step 2: Add i18n keys**

```ts
// In src/lib/i18n.ts:
"logs.title": { zh: "日志", en: "Logs" },
"logs.subtitle": { zh: "系统活动日志", en: "System Activity Logs" },
"logs.search": { zh: "搜索日志...", en: "Search logs..." },
"logs.all-levels": { zh: "全部级别", en: "All Levels" },
"logs.all-sources": { zh: "全部来源", en: "All Sources" },
"logs.no-logs": { zh: "暂无日志", en: "No logs found" },
```

- [ ] **Step 3: Add Logs to sidebar**

```tsx
// In sidebar.tsx, add { label: "nav.logs", icon: FileText, href: "/logs" }
```

- [ ] **Step 4: Build and verify**

Run: `cd /Users/a1234/sera-agent-console && npm run build`
Expected: Build succeeds

- [ ] **Step 5: Commit**

```bash
cd /Users/a1234/sera-agent-console && git add -A && git commit -m "feat: add logs page with filtering and search"
```

---

### Task 4.4: Workflow Editor (/workflows/[id]/edit)

**Files:**
- Create: `src/app/workflows/[id]/edit/page.tsx`
- Modify: `src/app/workflows/page.tsx` (add "Edit" button)

- [ ] **Step 1: Create workflow editor page**

```tsx
// src/app/workflows/[id]/edit/page.tsx
"use client"

import { useCallback, useRef, useState } from "react"
import { useParams, useRouter } from "next/navigation"
import {
  ReactFlow, Background, Controls, MiniMap, Handle, Position,
  useNodesState, useEdgesState, addEdge, type NodeProps, type Edge, type Node, type Connection,
} from "@xyflow/react"
import "@xyflow/react/dist/style.css"
import { motion } from "framer-motion"
import { ArrowLeft, Save, Play, Trash2, Plus, Bot, GripVertical } from "lucide-react"
import { useLang } from "@/lib/language-provider"
import { api } from "@/lib/api"
import { useData } from "@/lib/use-data"
import workflowsData from "@/data/workflows.json"

type EditorNodeData = { label: string; agent: string; skill: string; icon: string }
type EditorNodeType = Node<EditorNodeData, 'editorNode'>

function EditorNode({ data, selected }: NodeProps<EditorNodeType>) {
  const { tt } = useLang()
  return (
    <div className={`px-4 py-3 rounded-xl min-w-[180px] transition-all`}
      style={{
        background: selected ? "var(--bg-surface)" : "var(--bg-base)",
        border: `2px solid ${selected ? "var(--brand)" : "var(--border)"}`,
        boxShadow: selected ? "0 0 0 4px rgba(0,102,255,0.1)" : "none",
      }}
    >
      <Handle type="target" position={Position.Top} style={{ background: "var(--brand)", width: 8, height: 8 }} />
      <div className="flex items-center gap-2">
        <GripVertical className="w-3 h-3" style={{ color: "var(--text-muted)", cursor: "grab" }} />
        <Bot className="w-4 h-4" style={{ color: "var(--brand)" }} />
        <div>
          <div className="text-sm font-medium" style={{ color: "var(--text-primary)" }}>{tt(data.label)}</div>
          <div className="text-[10px]" style={{ color: "var(--text-muted)" }}>{tt(data.agent)}</div>
        </div>
      </div>
      <Handle type="source" position={Position.Bottom} style={{ background: "var(--brand)", width: 8, height: 8 }} />
    </div>
  )
}

const nodeTypes = { editorNode: EditorNode }

const paletteNodes = [
  { label: "Market Research", agent: "Product Agent", skill: "Research", icon: "search" },
  { label: "Content", agent: "Content Agent", skill: "Writing", icon: "file-text" },
  { label: "Video", agent: "Video Agent", skill: "Production", icon: "video" },
  { label: "Design", agent: "Brand Agent", skill: "Visual", icon: "palette" },
  { label: "Launch", agent: "multi", skill: "Distribution", icon: "rocket" },
  { label: "Notification", agent: "system", skill: "Notify", icon: "bell" },
]

export default function WorkflowEditorPage() {
  const { id } = useParams<{ id: string }>()
  const router = useRouter()
  const { t, tt } = useLang()
  const reactFlowWrapper = useRef<HTMLDivElement>(null)
  const [reactFlowInstance, setReactFlowInstance] = useState<any>(null)

  const workflow = workflowsData.workflows.find(w => w.id === id)
  const initialNodes: EditorNodeType[] = (workflow?.nodes || []).map(n => ({
    id: n.id, type: 'editorNode' as const,
    position: { x: 0, y: 0 },
    data: { label: n.label, agent: n.agent, skill: n.skill, icon: n.icon },
  }))
  const initialEdges: Edge[] = (workflow?.edges || []).map(e => ({
    id: `${e.source}-${e.target}`, source: e.source, target: e.target,
    animated: true, type: "smoothstep",
  }))

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes)
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges)
  const [selectedNode, setSelectedNode] = useState<string | null>(null)

  const onConnect = useCallback((params: Connection) => {
    setEdges(eds => addEdge({ ...params, animated: true, type: "smoothstep" }, eds))
  }, [setEdges])

  const onDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault()
    event.dataTransfer.dropEffect = "move"
  }, [])

  const onDrop = useCallback((event: React.DragEvent) => {
    event.preventDefault()
    const label = event.dataTransfer.getData("application/reactflow")
    if (!label || !reactFlowInstance || !reactFlowWrapper.current) return

    const bounds = reactFlowWrapper.current.getBoundingClientRect()
    const position = reactFlowInstance.screenToFlowPosition({ x: event.clientX - bounds.left, y: event.clientY - bounds.top })
    const paletteItem = paletteNodes.find(n => n.label === label)
    if (!paletteItem) return

    const newNode: EditorNodeType = {
      id: `node-${Date.now()}`,
      type: 'editorNode',
      position,
      data: { label: paletteItem.label, agent: paletteItem.agent, skill: paletteItem.skill, icon: paletteItem.icon },
    }
    setNodes(nds => nds.concat(newNode))
  }, [reactFlowInstance, setNodes])

  const onNodeClick = (_: any, node: EditorNodeType) => {
    setSelectedNode(node.id)
  }

  const deleteSelected = () => {
    if (selectedNode) {
      setNodes(nds => nds.filter(n => n.id !== selectedNode))
      setEdges(eds => eds.filter(e => e.source !== selectedNode && e.target !== selectedNode))
      setSelectedNode(null)
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <button onClick={() => router.back()} className="p-2 rounded-lg" style={{ background: "var(--bg-surface)", border: "1px solid var(--border)" }}>
            <ArrowLeft className="w-4 h-4" style={{ color: "var(--text-muted)" }} />
          </button>
          <div>
            <h1 className="text-lg font-bold" style={{ color: "var(--text-primary)" }}>{tt(workflow?.name || "")} - {t("workflows.editor")}</h1>
            <p className="text-xs" style={{ color: "var(--text-muted)" }}>{t("workflows.editor-hint")}</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button onClick={deleteSelected} className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm" style={{ background: "rgba(239,68,68,0.1)", color: "#EF4444", border: "1px solid rgba(239,68,68,0.2)" }}>
            <Trash2 className="w-4 h-4" /> {t("workflows.delete")}
          </button>
          <button className="btn-brand flex items-center gap-2 px-3 py-2 text-sm">
            <Save className="w-4 h-4" /> {t("workflows.save")}
          </button>
          <button className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm" style={{ background: "var(--success)", color: "white" }}>
            <Play className="w-4 h-4" /> {t("workflows.run")}
          </button>
        </div>
      </div>

      <div className="flex gap-4">
        {/* Palette */}
        <div className="w-48 rounded-xl p-3 shrink-0" style={{ background: "var(--bg-surface)", border: "1px solid var(--border)" }}>
          <h3 className="text-xs font-semibold uppercase tracking-wider mb-3" style={{ color: "var(--text-muted)" }}>{t("workflows.nodes")}</h3>
          <div className="space-y-2">
            {paletteNodes.map(node => (
              <div
                key={node.label}
                draggable
                onDragStart={e => e.dataTransfer.setData("application/reactflow", node.label)}
                className="flex items-center gap-2 p-2 rounded-lg cursor-grab text-xs transition-colors"
                style={{ background: "var(--bg-base)", border: "1px solid var(--border)" }}
                onMouseEnter={e => e.currentTarget.style.borderColor = "var(--brand)"}
                onMouseLeave={e => e.currentTarget.style.borderColor = "var(--border)"}
              >
                <Bot className="w-3 h-3" style={{ color: "var(--brand)" }} />
                <span style={{ color: "var(--text-primary)" }}>{tt(node.label)}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Canvas */}
        <div className="flex-1 h-[600px] rounded-xl border overflow-hidden" ref={reactFlowWrapper} style={{ borderColor: "var(--border)" }}>
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onInit={setReactFlowInstance}
            onDrop={onDrop}
            onDragOver={onDragOver}
            onNodeClick={onNodeClick}
            nodeTypes={nodeTypes}
            fitView
            minZoom={0.3}
            maxZoom={2}
            deleteKeyCode="Delete"
            snapToGrid
            snapGrid={[20, 20]}
          >
            <Background color="var(--border)" gap={20} size={1} />
            <Controls style={{ background: "var(--bg-surface)", border: "1px solid var(--border)", borderRadius: 8 }} />
            <MiniMap style={{ background: "var(--bg-surface)", border: "1px solid var(--border)", borderRadius: 8 }} nodeColor="var(--brand)" maskColor="rgba(11,15,25,0.8)" />
          </ReactFlow>
        </div>
      </div>
    </div>
  )
}
```

- [ ] **Step 2: Add i18n keys**

```ts
// In src/lib/i18n.ts:
"workflows.editor": { zh: "编辑器", en: "Editor" },
"workflows.editor-hint": { zh: "拖拽节点到画布，连接它们以创建工作流", en: "Drag nodes to canvas and connect them" },
"workflows.nodes": { zh: "节点", en: "Nodes" },
"workflows.delete": { zh: "删除", en: "Delete" },
"workflows.save": { zh: "保存", en: "Save" },
```

- [ ] **Step 3: Add "Edit" button to workflow cards**

```tsx
// In src/app/workflows/page.tsx, add button next to each workflow tab:
<button onClick={() => router.push(`/workflows/${wf.id}/edit`)}
  className="text-xs px-2 py-1 rounded" style={{ color: "var(--brand)", border: "1px solid rgba(0,102,255,0.2)" }}>
  {t("workflows.edit")}
</button>
```

- [ ] **Step 4: Build and verify**

Run: `cd /Users/a1234/sera-agent-console && npm run build`
Expected: Build succeeds

- [ ] **Step 5: Commit**

```bash
cd /Users/a1234/sera-agent-console && git add -A && git commit -m "feat: add workflow editor with drag-and-drop node palette"
```

---

## Phase 5: Deploy V2 to Production

### Task 5.1: Deploy to Vercel Production

- [ ] **Step 1: Sync code to sera-agent-os repo**

```bash
rsync -av --exclude='node_modules' --exclude='.next' --exclude='.git' --exclude='next-env.d.ts' /Users/a1234/sera-agent-console/ /Users/a1234/sera-agent-os/control-center/frontend/
```

- [ ] **Step 2: Commit and push**

```bash
cd /Users/a1234/sera-agent-os && git add control-center/frontend/ && git commit -m "feat: Control Center V2 — API layer, CMS adapter, new pages"
git push origin main
```

- [ ] **Step 3: Deploy to Vercel production**

```bash
cd /Users/a1234/sera-agent-console && vercel --prod
```

Expected: Production deployment URL

---

## Summary

| Phase | Deliverable | Files | Priority |
|-------|-------------|-------|----------|
| 1 | Vercel deployment + custom domain | vercel.json | P0 |
| 2 | API Routes layer + page migration | 4 API routes + api.ts + use-data.ts | P0 |
| 3 | Data source abstraction (Tencent Docs) | data-sources/ adapter | P1 |
| 4a | Settings page | /settings | P1 |
| 4b | Agent detail page | /agents/[id] | P1 |
| 4c | Logs page | /logs | P2 |
| 4d | Workflow editor | /workflows/[id]/edit | P2 |
| 5 | Production deploy | Vercel | P0 |

**Total: ~40 steps, ~25 new/modified files**