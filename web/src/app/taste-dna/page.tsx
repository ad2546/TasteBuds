"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { api, type TasteDNA, type TasteDNACard } from "@/lib/api"
import { ArrowLeft, Share2, Flame, Sparkles, Loader2, RefreshCw } from "lucide-react"
import { ProtectedRoute } from "@/components/protected-route"

function TasteDNAPageContent() {
  const router = useRouter()
  const [profile, setProfile] = useState<TasteDNA | null>(null)
  const [card, setCard] = useState<TasteDNACard | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [profileData, cardData] = await Promise.all([api.getTasteDNA(), api.getTasteDNACard()])
      setProfile(profileData)
      setCard(cardData)
    } catch (error) {
      console.error("Failed to load taste DNA:", error)
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

  const adventurePercent = Math.round((profile?.adventure_score || 0) * 100)
  const spicePercent = Math.round((profile?.spice_tolerance || 0) * 100)
  const diversityPercent = Math.round((profile?.cuisine_diversity || 0) * 100)

  return (
    <div className="min-h-screen bg-neutral-50">
      {/* Header */}
      <div className="bg-[#FF6B6B] px-4 pt-4 pb-8">
        <div className="max-w-md mx-auto">
          <div className="flex items-center justify-between mb-4">
            <button
              onClick={() => router.back()}
              className="w-10 h-10 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center hover:bg-white/30 transition-colors"
              aria-label="Go back"
            >
              <ArrowLeft className="w-5 h-5 text-white" />
            </button>
            <h1 className="text-xl font-semibold text-white">Your Taste DNA</h1>
            <button
              className="w-10 h-10 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center hover:bg-white/30 transition-colors"
              aria-label="Share"
            >
              <Share2 className="w-5 h-5 text-white" />
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-md mx-auto px-4 -mt-4 pb-20">
        {/* DNA Card */}
        <div className="bg-white rounded-2xl shadow-xl p-6 mb-6 relative overflow-hidden border-2 border-[#FF6B6B]/20">
          <div className="relative">
            <div className="flex items-center gap-2 mb-4">
              <div className="w-8 h-8 bg-[#FF6B6B] rounded-lg flex items-center justify-center">
                <Sparkles className="w-5 h-5 text-white" />
              </div>
              <span className="text-gray-600 text-sm font-medium">TASTE DNA</span>
            </div>

            <h2 className="text-2xl font-bold text-gray-900 mb-1">{card?.user_name}</h2>
            <p className="text-gray-600 text-sm mb-6">{card?.share_text}</p>

            {/* Stats Grid */}
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-[#FF6B6B]/10 border border-[#FF6B6B]/20 rounded-xl p-3">
                <p className="text-gray-600 text-xs mb-1">Adventure</p>
                <p className="text-gray-900 text-2xl font-bold">{adventurePercent}%</p>
              </div>
              <div className="bg-[#FFA94D]/10 border border-[#FFA94D]/20 rounded-xl p-3">
                <p className="text-gray-600 text-xs mb-1">Spice Level</p>
                <p className="text-gray-900 text-2xl font-bold">{spicePercent}%</p>
              </div>
            </div>
          </div>
        </div>

        {/* Detailed Stats */}
        <div className="bg-white rounded-2xl shadow-lg p-6 mb-6">
          <h3 className="font-semibold text-[#2C3E50] mb-4">Your Flavor Profile</h3>

          {/* Adventure Score */}
          <div className="mb-5">
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm text-[#6C757D]">Adventure Score</span>
              <span className="text-sm font-semibold text-[#FF6B6B]">{adventurePercent}%</span>
            </div>
            <div className="h-3 bg-[#E9ECEF] rounded-full overflow-hidden">
              <div
                className="h-full bg-[#FF6B6B] transition-all duration-1000"
                style={{ width: `${adventurePercent}%` }}
              />
            </div>
            <p className="text-xs text-[#ADB5BD] mt-1">
              {adventurePercent >= 70
                ? "You love trying new cuisines!"
                : adventurePercent >= 40
                  ? "You enjoy a mix of familiar and new."
                  : "You prefer classic favorites."}
            </p>
          </div>

          {/* Spice Tolerance */}
          <div className="mb-5">
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm text-[#6C757D] flex items-center gap-1">
                <Flame className="w-4 h-4 text-[#FFA94D]" />
                Spice Tolerance
              </span>
              <span className="text-sm font-semibold text-[#FFA94D]">{spicePercent}%</span>
            </div>
            <div className="h-3 bg-[#E9ECEF] rounded-full overflow-hidden">
              <div
                className="h-full bg-[#FFA94D] transition-all duration-1000"
                style={{ width: `${spicePercent}%` }}
              />
            </div>
            <p className="text-xs text-[#ADB5BD] mt-1">
              {spicePercent >= 70
                ? "Bring on the heat!"
                : spicePercent >= 40
                  ? "Medium spice is your sweet spot."
                  : "You prefer milder flavors."}
            </p>
          </div>

          {/* Cuisine Diversity */}
          <div>
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm text-[#6C757D]">Cuisine Diversity</span>
              <span className="text-sm font-semibold text-[#4ECDC4]">{diversityPercent}%</span>
            </div>
            <div className="h-3 bg-[#E9ECEF] rounded-full overflow-hidden">
              <div
                className="h-full bg-[#4ECDC4] transition-all duration-1000"
                style={{ width: `${diversityPercent}%` }}
              />
            </div>
          </div>
        </div>

        {/* Favorite Cuisines */}
        <div className="bg-white rounded-2xl shadow-lg p-6 mb-6">
          <h3 className="font-semibold text-[#2C3E50] mb-4">Top Cuisines</h3>
          <div className="flex flex-wrap gap-2">
            {(profile?.preferred_cuisines || card?.top_cuisines || []).map((cuisine, i) => (
              <span
                key={cuisine}
                className={`px-4 py-2 rounded-full text-sm font-medium ${
                  i === 0 ? "bg-[#FF6B6B] text-white" : i === 1 ? "bg-[#FFA94D] text-white" : "bg-[#4ECDC4] text-white"
                }`}
              >
                {cuisine}
              </span>
            ))}
          </div>
        </div>

        {/* Dietary Restrictions */}
        {profile?.dietary_restrictions && profile.dietary_restrictions.length > 0 && (
          <div className="bg-white rounded-2xl shadow-lg p-6">
            <h3 className="font-semibold text-[#2C3E50] mb-4">Dietary Preferences</h3>
            <div className="flex flex-wrap gap-2">
              {profile.dietary_restrictions.map((restriction) => (
                <span
                  key={restriction}
                  className="px-4 py-2 rounded-full text-sm font-medium bg-[#E9ECEF] text-[#6C757D]"
                >
                  {restriction}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Retake Quiz Button */}
        <button
          onClick={() => router.push("/quiz")}
          className="w-full mt-6 h-12 rounded-xl bg-[#FF6B6B] text-white font-medium flex items-center justify-center gap-2 hover:opacity-90 transition-opacity shadow-lg"
        >
          <RefreshCw className="w-5 h-5" />
          Retake Quiz
        </button>
      </div>
    </div>
  )
}

export default function TasteDNAPage() {
  return (
    <ProtectedRoute>
      <TasteDNAPageContent />
    </ProtectedRoute>
  )
}
