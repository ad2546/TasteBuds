import type React from "react"
import type { Metadata, Viewport } from "next"
import { AuthProvider } from "@/lib/auth-context"
import { BottomNav } from "@/components/ui"
import { DesktopWrapper } from "@/components/desktop-wrapper"
import "./globals.css"

export const metadata: Metadata = {
  title: "TasteBuds Yelp Companion - Find People Who Like Similar Food",
  description:
    "Connect with people who share your food preferences. TasteBuds helps you find Taste Twins with similar tastes, discover restaurants together, and explore Yelp reviews from people like you.",
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
          <DesktopWrapper>
            {children}
            <BottomNav />
          </DesktopWrapper>
        </AuthProvider>
      </body>
    </html>
  )
}
