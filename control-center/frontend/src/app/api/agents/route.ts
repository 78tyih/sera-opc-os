import { NextResponse } from "next/server"
import { createServiceClient } from "@/lib/supabase"

export const dynamic = "force-dynamic"

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url)
  const department = searchParams.get("department")
  const status = searchParams.get("status")

  try {
    const sb = createServiceClient()
    let query = sb.from("agents").select("*")

    if (department) query = query.eq("department", department)
    if (status) query = query.eq("status", status)

    query = query.order("name")

    const { data: agents, error } = await query
    if (error) throw error

    return NextResponse.json({ agents, total: agents?.length || 0 })
  } catch (e) {
    console.warn("Supabase agents fetch failed, falling back to JSON", e)
    const agentsData = (await import("@/data/agents.json")).default
    let data = agentsData
    if (department) data = data.filter(a => a.department === department)
    if (status) data = data.filter(a => a.status === status)
    return NextResponse.json({ agents: data, total: data.length })
  }
}