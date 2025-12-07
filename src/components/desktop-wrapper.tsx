"use client"

import { useEffect, useState } from "react"
import { Smartphone } from "lucide-react"
import { DesktopProvider } from "@/lib/desktop-context"

export function DesktopWrapper({ children }: { children: React.ReactNode }) {
  const [isMobile, setIsMobile] = useState(false)

  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768)
    }

    checkMobile()
    window.addEventListener("resize", checkMobile)
    return () => window.removeEventListener("resize", checkMobile)
  }, [])

  if (isMobile) {
    return <DesktopProvider>{children}</DesktopProvider>
  }

  return (
    <DesktopProvider>
    <div className="min-h-screen bg-gradient-to-br from-[#FF6B6B] via-[#FF8787] to-[#FFA94D] flex items-center justify-center p-8">
      <div className="flex gap-12 items-center max-w-7xl">
        {/* Left side - Branding */}
        <div className="flex-1 text-white space-y-6">
          <div className="space-y-4">
            <h1 className="text-5xl font-bold">TasteBuds</h1>
            <p className="text-xl text-white/90">Yelp Companion</p>
            <p className="text-2xl text-white font-semibold">Find People Who Like Similar Food</p>
          </div>

          <div className="space-y-4 text-lg text-white/80">
            <div className="flex items-start gap-3">
              <div className="w-2 h-2 bg-white rounded-full mt-2" />
              <p>Connect with Taste Twins who share your food preferences</p>
            </div>
            <div className="flex items-start gap-3">
              <div className="w-2 h-2 bg-white rounded-full mt-2" />
              <p>Discover restaurants loved by people with similar tastes</p>
            </div>
            <div className="flex items-start gap-3">
              <div className="w-2 h-2 bg-white rounded-full mt-2" />
              <p>Explore Yelp reviews from your Taste Twins</p>
            </div>
            <div className="flex items-start gap-3">
              <div className="w-2 h-2 bg-white rounded-full mt-2" />
              <p>Make better dining decisions with personalized matches</p>
            </div>
          </div>

          <div className="pt-6 space-y-3">
            <div className="flex items-center gap-3 bg-white/10 backdrop-blur-sm rounded-xl p-4">
              <Smartphone className="w-6 h-6" />
              <p className="font-medium">Best experienced on mobile devices</p>
            </div>
            <p className="text-sm text-white/60">
              For the full TasteBuds experience, please open this app on your smartphone or resize your browser window.
            </p>
          </div>
        </div>

        {/* Right side - Mobile frame */}
        <div className="flex-shrink-0">
          <div className="relative">
            {/* Phone frame */}
            <div className="bg-gray-900 rounded-[3rem] p-3 shadow-2xl">
              <div className="bg-black rounded-[2.5rem] overflow-hidden">
                {/* Notch */}
                <div className="bg-black h-6 flex items-center justify-center">
                  <div className="bg-gray-900 w-32 h-4 rounded-b-2xl" />
                </div>

                {/* App content - 18:9 aspect ratio */}
                <div className="bg-white w-[360px] h-[720px] overflow-hidden flex flex-col relative">
                  <div className="flex-1 overflow-y-auto scrollbar-hide pb-[72px]">
                    {children}
                  </div>
                </div>
              </div>
            </div>

            {/* Glow effect */}
            <div className="absolute inset-0 bg-gradient-to-br from-white/20 to-transparent rounded-[3rem] pointer-events-none" />
          </div>
        </div>
      </div>
    </div>
    </DesktopProvider>
  )
}
