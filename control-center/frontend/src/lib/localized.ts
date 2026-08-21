export function localized(lang: "zh" | "en", zh: string, en: string) {
  return lang === "zh" ? zh : en
}
