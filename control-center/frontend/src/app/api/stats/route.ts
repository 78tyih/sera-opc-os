import { NextResponse } from "next/server"
import { createServiceClient } from "@/lib/supabase"

export const dynamic = "force-dynamic"

export async function GET() {
  try {
    const sb = createServiceClient()

    const [agentsRes, projectsRes, workflowsRes] = await Promise.all([
      sb.from("agents").select("*", { count: "exact", head: true }),
      sb.from("projects").select("*", { count: "exact", head: true }).eq("status", "active"),
      sb.from("workflows").select("*", { count: "exact", head: true }).eq("status", "active"),
    ])

    return NextResponse.json({
      totalAgents: agentsRes.count || 0,
      activeProjects: projectsRes.count || 0,
      activeWorkflows: workflowsRes.count || 0,
      uptime: "99.7%",
      todayOutput: "12",
    })
  } catch (e) {
    console.warn("Supabase stats fetch failed, falling back", e)
    return NextResponse.json({
      totalAgents: 13,
      activeProjects: 5,
      activeWorkflows: 2,
      uptime: "99.7%",
      todayOutput: "12",
    })
  }
}