"use client"

import { usePathname } from "next/navigation"

export function MainContent({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()
  const isCanvas = pathname === "/canvas"

  return (
    <main
      className={isCanvas ? "flex-1 flex flex-col overflow-hidden" : "flex-1 p-6"}
      style={{ background: isCanvas ? "var(--bg-base)" : undefined }}
    >
      {children}
    </main>
  )
}