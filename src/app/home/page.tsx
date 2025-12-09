"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/lib/auth-context"
import { getAvatarUrl } from "@/lib/avatar-utils"
import { api, type TasteTwin } from "@/lib/api"
import { Bell, Dice5, Search, Heart, Trophy, Sparkles, Users } from "lucide-react"
import { ProtectedRoute } from "@/components/protected-route"
import { Card, CardContent, Button, LoadingSpinner } from "@/components/ui"

function HomePageContent() {
  const router = useRouter()
  const { user } = useAuth()
  const [twins, setTwins] = useState<TasteTwin[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadTwins()
  }, [])

  const loadTwins = async () => {
    try {
      const data = await api.getTwins()
      // Backend returns user_id and common_cuisines, map to match frontend types
      const formattedTwins = data.twins.map((twin: any) => ({
        ...twin,
        twin_id: twin.user_id || twin.twin_id,
        shared_cuisines: twin.common_cuisines || twin.shared_cuisines || [],
        adventure_score: twin.adventure_score || 0,
        spice_tolerance: twin.spice_tolerance || 0,
      }))
      setTwins(formattedTwins)
    } catch (error) {
      console.error("Failed to load twins:", error)
    } finally {
      setLoading(false)
    }
  }

  const quickActions = [
    { icon: Search, label: "Search", desc: "Find restaurants", href: "/search", color: "#D32323" },
    { icon: Users, label: "Find Twins", desc: `${twins.length} taste matches`, href: "/twins", color: "#D32323" },
    { icon: Heart, label: "Date Night", desc: "Plan together", href: "/date-night", color: "#BD1F1F" },
    { icon: Trophy, label: "Challenges", desc: "Earn rewards", href: "/challenges", color: "#C41200" },
  ]

  if (loading) {
    return <LoadingSpinner fullScreen message="Loading your taste profile..." />
  }

  return (
    <div className="min-h-screen bg-neutral-50 pb-[60px] md:pb-32">
      {/* Header */}
      <div className="bg-[#FF6B6B] px-4 pt-4 pb-8">
        <div className="max-w-md mx-auto">
          <div className="flex items-center justify-between mb-6 gap-3">
            <div className="flex-1 min-w-0">
              <p className="text-white/80 text-sm">Welcome back,</p>
              <h1 className="text-2xl font-bold text-white truncate">
                {user?.name?.split(" ")[0] || user?.name || ""}
              </h1>
            </div>
            <div className="flex items-center gap-3 flex-shrink-0">
              <button
                className="w-10 h-10 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center hover:bg-white/30 transition-colors"
                aria-label="Notifications"
              >
                <Bell className="w-5 h-5 text-white" />
              </button>
              <button
                onClick={() => router.push("/profile")}
                className="w-10 h-10 rounded-full ring-2 ring-white/30 overflow-hidden hover:ring-white/50 transition-all bg-white"
                aria-label="Profile"
              >
                <img
                  src={getAvatarUrl(user?.avatar_url, user?.id)}
                  alt="Profile"
                  className="w-full h-full object-cover"
                />
              </button>
            </div>
          </div>

          {/* Taste Twins Badge */}
          <Card className="bg-white/95 backdrop-blur-sm animate-[slideUp_0.3s_ease-out]">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 bg-[#FF6B6B] rounded-full flex items-center justify-center">
                    <Users className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Your Taste Twins</p>
                    <p className="text-2xl font-bold text-gray-900">{twins.length}</p>
                  </div>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => router.push("/twins")}
                  aria-label="View twins"
                >
                  View All
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      <div className="max-w-md mx-auto px-4 -mt-4 space-y-6">
        {/* Feeling Lucky - Primary CTA */}
        <Button
          variant="gradient"
          size="lg"
          fullWidth
          onClick={() => router.push("/feeling-lucky")}
          leftIcon={<Dice5 className="w-6 h-6 text-gray-900" />}
          className="h-20 text-xl shadow-2xl animate-[scaleIn_0.3s_ease-out_0.1s_both] !bg-white !text-gray-900"
        >
          <div className="flex flex-col items-center">
            <span className="font-bold">Feeling Lucky</span>
            <span className="text-sm font-normal opacity-70">Find your perfect match</span>
          </div>
        </Button>

        {/* Quick Actions Grid */}
        <div className="grid grid-cols-2 gap-3 animate-[fadeIn_0.3s_ease-out_0.2s_both]">
          {quickActions.map(({ icon: Icon, label, desc, href, color }) => (
            <Card
              key={label}
              hoverable
              className="cursor-pointer"
              onClick={() => router.push(href)}
            >
              <CardContent className="p-4">
                <div
                  className="w-12 h-12 rounded-xl flex items-center justify-center mb-3 transition-transform group-hover:scale-110"
                  style={{ backgroundColor: `${color}15` }}
                >
                  <Icon className="w-6 h-6" style={{ color }} />
                </div>
                <h3 className="text-sm font-semibold text-gray-900 mb-1">{label}</h3>
                <p className="text-xs text-gray-600">{desc}</p>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Taste DNA Card */}
        <Card
          variant="gradient"
          hoverable
          className="cursor-pointer !bg-[#FF6B6B] animate-[fadeIn_0.3s_ease-out_0.3s_both]"
          onClick={() => router.push("/taste-dna")}
        >
          <CardContent className="p-5">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-white/90 text-sm font-medium mb-1 flex items-center gap-2">
                  <Sparkles className="w-4 h-4" />
                  Your Taste DNA
                </p>
                <p className="text-white font-semibold text-lg">View your flavor profile</p>
              </div>
              <div className="w-14 h-14 bg-white/10 rounded-full flex items-center justify-center backdrop-blur-sm">
                <Sparkles className="w-7 h-7 text-white" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default function HomePage() {
  return (
    <ProtectedRoute>
      <HomePageContent />
    </ProtectedRoute>
  )
}
