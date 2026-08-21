/* API payloads mirror editable registry JSON and intentionally remain open-shaped. */
/* eslint-disable @typescript-eslint/no-explicit-any */
const API_BASE = ""

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
  stats: () => fetchJSON<{ totalAgents: number; activeProjects: number; activeWorkflows: number; uptime: string; todayOutput: string }>("/stats"),
}
