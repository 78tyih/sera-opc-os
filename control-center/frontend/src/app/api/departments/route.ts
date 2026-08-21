import { NextResponse } from "next/server"
import { createServiceClient } from "@/lib/supabase"

export const dynamic = "force-dynamic"

export async function GET() {
  try {
    const sb = createServiceClient()
    const { data: departments, error } = await sb.from("departments").select("*").order("name")
    if (error) throw error
    return NextResponse.json({ departments: departments || [] })
  } catch (e) {
    console.warn("Supabase departments fetch failed, falling back to JSON", e)
    const departmentsData = (await import("@/data/departments.json")).default
    return NextResponse.json({ departments: departmentsData })
  }
}