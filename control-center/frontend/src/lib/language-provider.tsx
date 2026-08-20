"use client"

import { createContext, useContext, useState, useEffect, useCallback, type ReactNode } from "react"
import { t as translate, translateText as translateDataText, isProperNoun } from "@/lib/i18n"

type Lang = "zh" | "en"

const LangContext = createContext<{
  lang: Lang
  setLang: (l: Lang) => void
  t: (key: string) => string
  tt: (text: string) => string
}>({
  lang: "zh",
  setLang: () => {},
  t: (key: string) => key,
  tt: (text: string) => text,
})

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [lang, setLang] = useState<Lang>("zh")
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
    const saved = localStorage.getItem("sera-lang") as Lang | null
    if (saved === "en" || saved === "zh") setLang(saved)
  }, [])

  const setLangAndPersist = (l: Lang) => {
    setLang(l)
    localStorage.setItem("sera-lang", l)
  }

  const t = useCallback((key: string) => translate(key, lang), [lang])
  const tt = useCallback((text: string) => {
    if (lang === "en") return text
    if (isProperNoun(text)) return text
    return translateDataText(text, lang)
  }, [lang])

  if (!mounted) return <>{children}</>

  return (
    <LangContext.Provider value={{ lang, setLang: setLangAndPersist, t, tt }}>
      {children}
    </LangContext.Provider>
  )
}

export function useLang() {
  return useContext(LangContext)
}