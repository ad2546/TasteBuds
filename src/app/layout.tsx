import type React from "react"
import type { Metadata, Viewport } from "next"
import { AuthProvider } from "@/lib/auth-context"
import { BottomNav } from "@/components/ui"
import "./globals.css"

export const metadata: Metadata = {
  title: "TasteSync - Discover Your Perfect Restaurant",
  description:
    "Find restaurants that match your unique taste DNA. Discover your taste twins and get personalized recommendations.",
}

export const viewport: Viewport = {
  themeColor: "#FF6B6B",
  width: "device-width",
  initialScale: 1,
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="font-sans antialiased">
        <AuthProvider>
          {children}
          <BottomNav />
        </AuthProvider>
      </body>
    </html>
  )
}
