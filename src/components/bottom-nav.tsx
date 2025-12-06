"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { Home, Search, Heart, Trophy, User } from "lucide-react"

const navItems = [
  { href: "/home", icon: Home, label: "Home" },
  { href: "/search", icon: Search, label: "Search" },
  { href: "/saved", icon: Heart, label: "Saved" },
  { href: "/challenges", icon: Trophy, label: "Challenges" },
  { href: "/profile", icon: User, label: "Profile" },
]

export function BottomNav() {
  const pathname = usePathname()

  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-white border-t border-[#E9ECEF] px-4 py-2 z-50">
      <div className="max-w-md mx-auto flex items-center justify-around">
        {navItems.map(({ href, icon: Icon, label }) => {
          const isActive = pathname === href
          return (
            <Link
              key={href}
              href={href}
              className={`flex flex-col items-center gap-1 px-3 py-2 rounded-xl transition-colors ${
                isActive ? "text-[#FF6B6B]" : "text-[#ADB5BD] hover:text-[#6C757D]"
              }`}
            >
              <Icon className={`w-6 h-6 ${isActive ? "fill-[#FF6B6B]/20" : ""}`} />
              <span className="text-xs font-medium">{label}</span>
            </Link>
          )
        })}
      </div>
    </nav>
  )
}
