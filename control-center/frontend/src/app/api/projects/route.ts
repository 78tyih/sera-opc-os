import { NextResponse } from "next/server"
import { createServiceClient } from "@/lib/supabase"

export const dynamic = "force-dynamic"

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url)
  const category = searchParams.get("category")
  const status = searchParams.get("status")

  try {
    const sb = createServiceClient()
    let query = sb.from("projects").select("*")

    if (category) query = query.eq("category", category)
    if (status) query = query.eq("status", status)

    query = query.order("name")

    const { data: projects, error } = await query
    if (error) throw error

    return NextResponse.json({ projects, total: projects?.length || 0 })
  } catch (e) {
    console.warn("Supabase projects fetch failed, falling back to JSON", e)
    const projectsData = (await import("@/data/projects.json")).default
    let data = projectsData
    if (category) data = data.filter(p => p.category === category)
    if (status) data = data.filter(p => p.status === status)
    return NextResponse.json({ projects: data, total: data.length })
  }
}