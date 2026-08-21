import { NextResponse } from "next/server"
import { createServiceClient } from "@/lib/supabase"

export const dynamic = "force-dynamic"

export async function GET() {
  try {
    const sb = createServiceClient()
    const { data: workflows, error } = await sb.from("workflows").select("*").order("name")
    if (error) throw error

    // Fetch nodes and edges for each workflow
    const workflowsWithDetails = await Promise.all(
      (workflows || []).map(async (w) => {
        const { data: nodes } = await sb.from("workflow_nodes").select("*").eq("workflow_id", w.id).order("id")
        const { data: edges } = await sb.from("workflow_edges").select("*").eq("workflow_id", w.id).order("id")
        return { ...w, nodes: nodes || [], edges: edges || [] }
      })
    )

    return NextResponse.json({ workflows: workflowsWithDetails })
  } catch (e) {
    console.warn("Supabase workflows fetch failed, falling back to JSON", e)
    const workflowsData = (await import("@/data/workflows.json")).default
    return NextResponse.json(workflowsData)
  }
}