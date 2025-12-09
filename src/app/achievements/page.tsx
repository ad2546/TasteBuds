"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { api, type Achievement } from "@/lib/api"
import { ArrowLeft, Trophy, Lock, Loader2 } from "lucide-react"

export default function AchievementsPage() {
  const router = useRouter()
  const [achievements, setAchievements] = useState<Achievement[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadAchievements()
  }, [])

  const loadAchievements = async () => {
    try {
      const data = await api.getAchievements()
      setAchievements(data.achievements)
    } catch (error) {
      console.error("Failed to load achievements:", error)
    } finally {
      setLoading(false)
    }
  }

  // Sample locked achievements for display
  const lockedAchievements = [
    { id: "first_visit", title: "First Step 🎯", description: "Mark your first restaurant as visited" },
    { id: "explorer_5", title: "Explorer 🗺️", description: "Visit 5 restaurants" },
    { id: "explorer_10", title: "Food Tourist ✈️", description: "Visit 10 restaurants" },
    { id: "explorer_25", title: "Gastronome 👨‍🍳", description: "Visit 25 restaurants" },
    { id: "explorer_50", title: "Culinary Legend 🏆", description: "Visit 50 restaurants" },
    { id: "spice_master", title: "Spice Master 🌶️", description: "Visit 5 spicy restaurants" },
    { id: "world_traveler", title: "World Traveler 🌍", description: "Try 8 different cuisines" },
    { id: "social_butterfly", title: "Social Butterfly 🦋", description: "Connect with 10 taste twins" },
  ]

  if (loading) {
    return (
      <div className="min-h-screen bg-[#F8F9FA] flex items-center justify-center">
        <Loader2 className="w-8 h-8 text-[#FF6B6B] animate-spin" />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-[#F8F9FA] pb-[60px] md:pb-0">
      {/* Header */}
      <div className="bg-[#FF6B6B] px-4 pt-4 pb-12">
        <div className="max-w-md mx-auto">
          <button
            onClick={() => router.back()}
            className="w-10 h-10 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center hover:bg-white/30 transition-colors mb-4"
          >
            <ArrowLeft className="w-5 h-5 text-white" />
          </button>

          <div className="text-center">
            <Trophy className="w-12 h-12 text-white mx-auto mb-3" />
            <h1 className="text-2xl font-bold text-white">Achievements</h1>
            <p className="text-white/80 mt-1">{achievements.length} earned</p>
          </div>
        </div>
      </div>

      <div className="max-w-md mx-auto px-4 -mt-6 pb-8">
        {/* Earned Achievements */}
        {achievements.length > 0 && (
          <div className="mb-6">
            <h3 className="font-semibold text-[#2C3E50] mb-3">Earned</h3>
            <div className="space-y-3">
              {achievements.map((achievement) => (
                <div key={achievement.id} className="bg-white rounded-xl shadow-sm p-4 flex items-center gap-4">
                  <div className="w-14 h-14 rounded-xl bg-[#FF6B6B] flex items-center justify-center">
                    <Trophy className="w-7 h-7 text-white" />
                  </div>
                  <div className="flex-1">
                    <h4 className="font-semibold text-[#2C3E50]">{achievement.title}</h4>
                    <p className="text-sm text-[#6C757D]">{achievement.description}</p>
                    <p className="text-xs text-[#ADB5BD] mt-1">
                      Earned {new Date(achievement.earned_at).toLocaleDateString()}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Locked Achievements */}
        <div>
          <h3 className="font-semibold text-[#2C3E50] mb-3">Locked</h3>
          <div className="space-y-3">
            {lockedAchievements.map((achievement) => (
              <div key={achievement.id} className="bg-white/60 rounded-xl p-4 flex items-center gap-4">
                <div className="w-14 h-14 rounded-xl bg-[#E9ECEF] flex items-center justify-center">
                  <Lock className="w-6 h-6 text-[#ADB5BD]" />
                </div>
                <div className="flex-1">
                  <h4 className="font-semibold text-[#ADB5BD]">{achievement.title}</h4>
                  <p className="text-sm text-[#CED4DA]">{achievement.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
