"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/lib/auth-context"
import { getAvatarUrl } from "@/lib/avatar-utils"
import { api, type Challenge, type LeaderboardEntry } from "@/lib/api"
import { Trophy, Target, Flame, Crown, Loader2 } from "lucide-react"

export default function ChallengesPage() {
  const router = useRouter()
  const { isAuthenticated, isLoading: authLoading } = useAuth()
  const [challenges, setChallenges] = useState<Challenge[]>([])
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([])
  const [yourRank, setYourRank] = useState(0)
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<"challenges" | "leaderboard">("challenges")

  useEffect(() => {
    if (!authLoading) {
      if (!isAuthenticated) {
        router.push("/login")
        return
      }
      loadData()
    }
  }, [authLoading, isAuthenticated, router])

  const loadData = async () => {
    try {
      const [challengesData, leaderboardData] = await Promise.all([
        api.getChallenges(),
        api.getLeaderboard("adventure"),
      ])
      // Backend returns active_challenges array with challenge object inside
      const formattedChallenges = (challengesData as any).active_challenges.map((item: any) => ({
        id: item.challenge.id,
        title: item.challenge.title,
        description: item.challenge.description,
        target_count: item.challenge.target_count,
        user_progress: item.progress,
        reward_xp: item.challenge.points_reward,
        active: item.challenge.active,
        start_date: item.challenge.start_date,
        end_date: item.challenge.end_date,
      }))
      setChallenges(formattedChallenges)

      // Backend returns entries instead of leaderboard
      const leaderboardEntries = (leaderboardData as any).entries || (leaderboardData as any).leaderboard || []
      setLeaderboard(leaderboardEntries)
      setYourRank((leaderboardData as any).user_rank || 0)
    } catch (error) {
      console.error("Failed to load:", error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-[#F8F9FA] flex items-center justify-center">
        <Loader2 className="w-8 h-8 text-[#FF6B6B] animate-spin" />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-[#F8F9FA]">
      {/* Header */}
      <div className="bg-[#FF6B6B] px-4 pt-6 pb-12">
        <div className="max-w-md mx-auto">
          <h1 className="text-2xl font-bold text-white">Challenges</h1>
          <p className="text-white/80">Complete challenges to earn rewards</p>
        </div>
      </div>

      <div className="max-w-md mx-auto px-4 -mt-6">
        {/* Tabs */}
        <div className="bg-white rounded-xl shadow-lg p-1 flex mb-6">
          <button
            onClick={() => setActiveTab("challenges")}
            className={`flex-1 py-2.5 rounded-lg font-medium transition-colors ${
              activeTab === "challenges" ? "bg-[#FF6B6B] text-white" : "text-[#6C757D] hover:bg-[#F8F9FA]"
            }`}
          >
            <Target className="w-4 h-4 inline mr-2" />
            Challenges
          </button>
          <button
            onClick={() => setActiveTab("leaderboard")}
            className={`flex-1 py-2.5 rounded-lg font-medium transition-colors ${
              activeTab === "leaderboard" ? "bg-[#FF6B6B] text-white" : "text-[#6C757D] hover:bg-[#F8F9FA]"
            }`}
          >
            <Trophy className="w-4 h-4 inline mr-2" />
            Leaderboard
          </button>
        </div>

        {activeTab === "challenges" ? (
          <div className="space-y-4">
            {challenges.map((challenge) => {
              const progress = (challenge.user_progress / challenge.target_count) * 100
              return (
                <div key={challenge.id} className="bg-white rounded-xl shadow-sm p-4">
                  <div className="flex items-start gap-3">
                    <div className="w-12 h-12 rounded-xl bg-[#FFA94D]/10 flex items-center justify-center">
                      <Flame className="w-6 h-6 text-[#FFA94D]" />
                    </div>
                    <div className="flex-1">
                      <h3 className="font-semibold text-[#2C3E50]">{challenge.title}</h3>
                      <p className="text-sm text-[#6C757D]">{challenge.description}</p>

                      {/* Progress Bar */}
                      <div className="mt-3">
                        <div className="flex justify-between text-xs text-[#ADB5BD] mb-1">
                          <span>
                            {challenge.user_progress} / {challenge.target_count}
                          </span>
                          <span>{challenge.reward_xp} XP</span>
                        </div>
                        <div className="h-2 bg-[#E9ECEF] rounded-full overflow-hidden">
                          <div
                            className="h-full bg-[#FF6B6B] transition-all"
                            style={{ width: `${Math.min(progress, 100)}%` }}
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        ) : (
          <div className="bg-white rounded-xl shadow-sm overflow-hidden">
            {/* Your Rank */}
            <div className="bg-[#FF6B6B] p-4 text-white">
              <p className="text-sm opacity-80">Your Rank</p>
              <p className="text-3xl font-bold">{yourRank ? `#${yourRank}` : "N/A"}</p>
            </div>

            {/* Leaderboard List */}
            <div className="divide-y divide-[#E9ECEF]">
              {leaderboard.length > 0 ? (
                leaderboard.map((entry) => (
                <div key={entry.user_id} className="flex items-center gap-3 p-4">
                  <div
                    className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm ${
                      entry.rank === 1
                        ? "bg-yellow-400 text-yellow-900"
                        : entry.rank === 2
                          ? "bg-gray-300 text-gray-700"
                          : entry.rank === 3
                            ? "bg-amber-600 text-white"
                            : "bg-[#E9ECEF] text-[#6C757D]"
                    }`}
                  >
                    {entry.rank <= 3 ? <Crown className="w-4 h-4" /> : entry.rank}
                  </div>
                  <img
                    src={getAvatarUrl(entry.avatar_url, entry.user_id)}
                    alt={entry.name}
                    className="w-10 h-10 rounded-full object-cover bg-white"
                  />
                  <div className="flex-1">
                    <p className="font-medium text-[#2C3E50]">{entry.name}</p>
                    <p className="text-sm text-[#ADB5BD]">{entry.score} XP</p>
                  </div>
                </div>
              ))) : (
                <div className="p-8 text-center">
                  <Trophy className="w-12 h-12 text-[#CED4DA] mx-auto mb-3" />
                  <p className="text-[#6C757D] font-medium">No leaderboard data yet</p>
                  <p className="text-sm text-[#ADB5BD] mt-1">Complete challenges to appear on the leaderboard!</p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
