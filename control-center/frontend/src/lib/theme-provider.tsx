"use client"

import { createContext, useContext, useEffect, useState } from "react"

type Theme = "light" | "dark"

const ThemeContext = createContext<{
  theme: Theme
  toggle: () => void
}>({ theme: "dark", toggle: () => {} })

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  // SSR-consistent default; localStorage is synced after mount to avoid hydration mismatch.
  const [theme, setTheme] = useState<Theme>("dark")

  useEffect(() => {
    const saved = localStorage.getItem("htx-theme")
    if (saved === "light" || saved === "dark") setTheme(saved)
  }, [])

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme)
    localStorage.setItem("htx-theme", theme)
  }, [theme])

  const toggle = () => setTheme(t => (t === "dark" ? "light" : "dark"))

  return (
    <ThemeContext.Provider value={{ theme, toggle }}>
      {children}
    </ThemeContext.Provider>
  )
}

export const useTheme = () => useContext(ThemeContext)
