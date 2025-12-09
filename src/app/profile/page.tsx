"use client"

import { useRouter } from "next/navigation"
import { useAuth } from "@/lib/auth-context"
import { getAvatarUrl } from "@/lib/avatar-utils"
import { User, Settings, LogOut, ChevronRight, Heart, Trophy, Sparkles, Bell, HelpCircle, Shield } from "lucide-react"
import { ProtectedRoute } from "@/components/protected-route"

function ProfilePageContent() {
  const router = useRouter()
  const { user, logout } = useAuth()

  const handleLogout = () => {
    logout()
    router.push("/login")
  }

  const menuItems = [
    { icon: Sparkles, label: "Taste DNA", href: "/taste-dna", color: "#FFA94D" },
    { icon: Heart, label: "Saved Restaurants", href: "/saved", color: "#FF6B6B" },
    { icon: Trophy, label: "Achievements", href: "/achievements", color: "#51CF66" },
    { icon: Bell, label: "Notifications", href: "/notifications", color: "#4ECDC4" },
    { icon: Settings, label: "Settings", href: "/settings", color: "#6C757D" },
    { icon: HelpCircle, label: "Help & Support", href: "/help", color: "#6C757D" },
    { icon: Shield, label: "Privacy", href: "/privacy", color: "#6C757D" },
  ]

  return (
    <div className="min-h-screen bg-[#F8F9FA] pb-[60px] md:pb-0">
      {/* Profile Header */}
      <div className="bg-[#FF6B6B] px-4 pt-8 pb-16">
        <div className="max-w-md mx-auto text-center">
          <div className="relative inline-block">
            <img
              src={getAvatarUrl(user?.avatar_url, user?.id)}
              alt={user?.name}
              className="w-24 h-24 rounded-full ring-4 ring-white object-cover bg-white"
            />
            <button className="absolute bottom-0 right-0 w-8 h-8 bg-white rounded-full flex items-center justify-center shadow-md">
              <User className="w-4 h-4 text-[#6C757D]" />
            </button>
          </div>
          <h1 className="text-xl font-bold text-white mt-4">{user?.name}</h1>
          <p className="text-white/80 text-sm">{user?.email}</p>
        </div>
      </div>

      <div className="max-w-md mx-auto px-4 -mt-8 pb-6">
        {/* Stats Card */}
        <div className="bg-white rounded-2xl shadow-lg p-4 mb-6">
          <div className="grid grid-cols-3 divide-x divide-[#E9ECEF]">
            <div className="text-center px-2">
              <p className="text-2xl font-bold text-[#FF6B6B]">2</p>
              <p className="text-xs text-[#6C757D]">Taste Twins</p>
            </div>
            <div className="text-center px-2">
              <p className="text-2xl font-bold text-[#4ECDC4]">12</p>
              <p className="text-xs text-[#6C757D]">Saved Places</p>
            </div>
            <div className="text-center px-2">
              <p className="text-2xl font-bold text-[#51CF66]">850</p>
              <p className="text-xs text-[#6C757D]">XP Points</p>
            </div>
          </div>
        </div>

        {/* Menu Items */}
        <div className="bg-white rounded-2xl shadow-sm overflow-hidden mb-6">
          {menuItems.map(({ icon: Icon, label, href, color }, index) => (
            <button
              key={label}
              onClick={() => router.push(href)}
              className={`w-full flex items-center gap-4 px-4 py-3.5 hover:bg-[#F8F9FA] transition-colors ${
                index !== menuItems.length - 1 ? "border-b border-[#E9ECEF]" : ""
              }`}
            >
              <div
                className="w-10 h-10 rounded-lg flex items-center justify-center"
                style={{ backgroundColor: `${color}15` }}
              >
                <Icon className="w-5 h-5" style={{ color }} />
              </div>
              <span className="flex-1 text-left font-medium text-[#2C3E50]">{label}</span>
              <ChevronRight className="w-5 h-5 text-[#CED4DA]" />
            </button>
          ))}
        </div>

        {/* Logout Button */}
        <button
          onClick={handleLogout}
          className="w-full flex items-center justify-center gap-2 h-12 rounded-xl border-2 border-[#FF6B6B] text-[#FF6B6B] font-medium hover:bg-[#FFE5E5] transition-colors"
        >
          <LogOut className="w-5 h-5" />
          Log Out
        </button>
      </div>
    </div>
  )
}

export default function ProfilePage() {
  return (
    <ProtectedRoute>
      <ProfilePageContent />
    </ProtectedRoute>
  )
}
