import type { Metadata } from "next"
import { Geist, Geist_Mono } from "next/font/google"
import "./globals.css"
import { ThemeProvider } from "@/lib/theme-provider"
import { LanguageProvider } from "@/lib/language-provider"
import { Sidebar } from "@/components/ui/sidebar"
import { Header } from "@/components/layout/header"

const geistSans = Geist({ variable: "--font-geist-sans", subsets: ["latin"] })
const geistMono = Geist_Mono({ variable: "--font-geist-mono", subsets: ["latin"] })

export const metadata: Metadata = {
  title: "Sera Agent OS — Control Center",
  description: "Personal AI Operating System Control Center",
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN" suppressHydrationWarning>
      <body className={`${geistSans.variable} ${geistMono.variable} antialiased`}>
        <ThemeProvider>
          <LanguageProvider>
            <Sidebar />
            <div className="ml-[220px] min-h-screen" style={{ background: "var(--bg-base)" }}>
              <Header />
              <main className="p-6">
                {children}
              </main>
            </div>
          </LanguageProvider>
        </ThemeProvider>
      </body>
    </html>
  )
}