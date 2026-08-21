import { createClient } from "@supabase/supabase-js"

// 客户端 Supabase 实例（懒初始化）
let clientInstance: ReturnType<typeof createClient> | null = null

export function getSupabase() {
  if (clientInstance) return clientInstance

  const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL
  const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY

  if (!supabaseUrl || !supabaseAnonKey) {
    throw new Error("Missing NEXT_PUBLIC_SUPABASE_URL or NEXT_PUBLIC_SUPABASE_ANON_KEY")
  }

  clientInstance = createClient(supabaseUrl, supabaseAnonKey, {
    auth: { persistSession: true },
  })
  return clientInstance
}

// 服务端客户端（用于 API Routes）
export function createServiceClient() {
  const url = process.env.SUPABASE_URL || process.env.NEXT_PUBLIC_SUPABASE_URL
  const key = process.env.SUPABASE_SERVICE_ROLE_KEY

  if (!url || !key) {
    throw new Error("Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY")
  }

  return createClient(url, key, {
    auth: { persistSession: false },
  })
}