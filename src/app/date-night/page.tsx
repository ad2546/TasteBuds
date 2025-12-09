"use client"

import { useState, useEffect, Suspense } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import { getAvatarUrl } from "@/lib/avatar-utils"
import { api, type TasteTwin, type CompatibilityResponse, type Restaurant } from "@/lib/api"
import { RestaurantCard } from "@/components/restaurant-card"
import { ArrowLeft, Heart, Loader2, Sparkles, Users } from "lucide-react"

function DateNightPageContent() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const partnerId = searchParams.get("partner")

  const [twins, setTwins] = useState<TasteTwin[]>([])
  const [selectedTwin, setSelectedTwin] = useState<TasteTwin | null>(null)
  const [compatibility, setCompatibility] = useState<CompatibilityResponse | null>(null)
  const [suggestions, setSuggestions] = useState<{
    perfect_matches: Restaurant[]
    you_will_love: Restaurant[]
    they_will_love: Restaurant[]
  } | null>(null)
  const [loading, setLoading] = useState(true)
  const [loadingSuggestions, setLoadingSuggestions] = useState(false)

  useEffect(() => {
    loadTwins()
  }, [])

  useEffect(() => {
    if (partnerId && twins.length > 0) {
      const twin = twins.find((t) => t.twin_id === partnerId)
      if (twin) {
        handleSelectTwin(twin)
      }
    }
  }, [partnerId, twins])

  const loadTwins = async () => {
    try {
      const data = await api.getTwins()
      setTwins(data.twins)
    } catch (error) {
      console.error("Failed to load twins:", error)
    } finally {
      setLoading(false)
    }
  }

  const handleSelectTwin = async (twin: TasteTwin) => {
    setSelectedTwin(twin)
    setLoadingSuggestions(true)

    try {
      const [compatData, suggestData] = await Promise.all([
        api.getCompatibility(twin.twin_id),
        api.getDateNightSuggestions(twin.twin_id, "San Francisco, CA"),
      ])
      setCompatibility(compatData)
      setSuggestions(suggestData)
    } catch (error) {
      console.error("Failed to load suggestions:", error)
    } finally {
      setLoadingSuggestions(false)
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
    <div className="min-h-screen bg-[#F8F9FA] pb-[60px] md:pb-0">
      {/* Header */}
      <div className="bg-[#FF6B6B] px-4 pt-4 pb-8">
        <div className="max-w-md mx-auto">
          <button
            onClick={() => router.back()}
            className="w-10 h-10 rounded-full bg-white/20 flex items-center justify-center mb-4"
          >
            <ArrowLeft className="w-5 h-5 text-white" />
          </button>

          <div className="text-center">
            <Heart className="w-12 h-12 text-white mx-auto mb-3" />
            <h1 className="text-2xl font-bold text-white">Date Night</h1>
            <p className="text-white/80 mt-1">Find the perfect spot for two</p>
          </div>
        </div>
      </div>

      <div className="max-w-md mx-auto px-4 -mt-4 pb-6">
        {!selectedTwin ? (
          <>
            {/* Select Partner */}
            <div className="bg-white rounded-2xl shadow-lg p-4 mb-4">
              <h3 className="font-semibold text-[#2C3E50] mb-3 flex items-center gap-2">
                <Users className="w-5 h-5 text-[#FF6B6B]" />
                Choose your dining partner
              </h3>

              {twins.length > 0 ? (
                <div className="space-y-3">
                  {twins.map((twin) => (
                    <button
                      key={twin.twin_id}
                      onClick={() => handleSelectTwin(twin)}
                      className="w-full flex items-center gap-3 p-3 rounded-xl border border-[#E9ECEF] hover:border-[#FF6B6B] hover:bg-[#FFE5E5]/20 transition-all"
                    >
                      <img
                        src={getAvatarUrl(twin.avatar_url, twin.twin_id)}
                        alt={twin.name}
                        className="w-12 h-12 rounded-full object-cover bg-white"
                      />
                      <div className="flex-1 text-left">
                        <p className="font-medium text-[#2C3E50]">{twin.name}</p>
                        <p className="text-sm text-[#ADB5BD]">{Math.round(twin.similarity_score * 100)}% taste match</p>
                      </div>
                      <Heart className="w-5 h-5 text-[#FF6B6B]" />
                    </button>
                  ))}
                </div>
              ) : (
                <div className="text-center py-6">
                  <p className="text-[#6C757D]">No taste twins found</p>
                  <p className="text-sm text-[#ADB5BD]">Find twins first to plan a date night</p>
                </div>
              )}
            </div>
          </>
        ) : loadingSuggestions ? (
          <div className="flex flex-col items-center justify-center py-12">
            <Loader2 className="w-8 h-8 text-[#FF6B6B] animate-spin mb-4" />
            <p className="text-[#6C757D]">Finding perfect spots for you two...</p>
          </div>
        ) : (
          <>
            {/* Compatibility Card */}
            <div className="bg-white rounded-2xl shadow-lg p-4 mb-6">
              <div className="flex items-center gap-3 mb-4">
                <img
                  src={getAvatarUrl(selectedTwin.avatar_url, selectedTwin.twin_id)}
                  alt={selectedTwin.name}
                  className="w-12 h-12 rounded-full object-cover ring-2 ring-[#FF6B6B] bg-white"
                />
                <div>
                  <p className="font-semibold text-[#2C3E50]">Date with {selectedTwin.name}</p>
                  <button onClick={() => setSelectedTwin(null)} className="text-sm text-[#FF6B6B]">
                    Change partner
                  </button>
                </div>
              </div>

              {compatibility && (
                <>
                  {/* Compatibility Score */}
                  <div className="bg-[#FF6B6B]/5 rounded-xl p-4 mb-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm text-[#6C757D]">Dining Compatibility</span>
                      <span className="text-lg font-bold text-[#FF6B6B]">
                        {Math.round(compatibility.compatibility_score * 100)}%
                      </span>
                    </div>
                    <div className="h-2 bg-white rounded-full overflow-hidden">
                      <div
                        className="h-full bg-[#FF6B6B]"
                        style={{ width: `${compatibility.compatibility_score * 100}%` }}
                      />
                    </div>
                  </div>

                  {/* Shared & Compromise */}
                  <div className="grid grid-cols-2 gap-3">
                    <div className="bg-[#51CF66]/10 rounded-xl p-3">
                      <p className="text-xs text-[#51CF66] font-medium mb-2">You Both Love</p>
                      <div className="flex flex-wrap gap-1">
                        {compatibility.shared_cuisines.slice(0, 3).map((c) => (
                          <span key={c} className="text-xs bg-[#51CF66]/20 text-[#51CF66] px-2 py-0.5 rounded-full">
                            {c}
                          </span>
                        ))}
                      </div>
                    </div>
                    <div className="bg-[#4ECDC4]/10 rounded-xl p-3">
                      <p className="text-xs text-[#4ECDC4] font-medium mb-2">Compromise</p>
                      <div className="flex flex-wrap gap-1">
                        {compatibility.compromise_cuisines.slice(0, 3).map((c) => (
                          <span key={c} className="text-xs bg-[#4ECDC4]/20 text-[#4ECDC4] px-2 py-0.5 rounded-full">
                            {c}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>

                  <p className="text-sm text-[#6C757D] mt-4">{compatibility.analysis}</p>
                </>
              )}
            </div>

            {/* Restaurant Suggestions */}
            {suggestions && (
              <>
                {suggestions.perfect_matches.length > 0 && (
                  <div className="mb-6">
                    <h3 className="font-semibold text-[#2C3E50] mb-3 flex items-center gap-2">
                      <Sparkles className="w-5 h-5 text-[#FFA94D]" />
                      Perfect for Both
                    </h3>
                    <div className="space-y-4">
                      {suggestions.perfect_matches.map((restaurant) => (
                        <RestaurantCard
                          key={restaurant.id || restaurant.restaurant_id}
                          restaurant={restaurant}
                          onClick={() => {
                            if (restaurant.url) {
                              window.open(restaurant.url, '_blank')
                            }
                          }}
                        />
                      ))}
                    </div>
                  </div>
                )}

                {suggestions.you_will_love.length > 0 && (
                  <div className="mb-6">
                    <h3 className="font-semibold text-[#2C3E50] mb-3">You Will Love</h3>
                    <div className="space-y-4">
                      {suggestions.you_will_love.slice(0, 2).map((restaurant) => (
                        <RestaurantCard
                          key={restaurant.id || restaurant.restaurant_id}
                          restaurant={restaurant}
                          onClick={() => {
                            if (restaurant.url) {
                              window.open(restaurant.url, '_blank')
                            }
                          }}
                        />
                      ))}
                    </div>
                  </div>
                )}

                {suggestions.they_will_love.length > 0 && (
                  <div>
                    <h3 className="font-semibold text-[#2C3E50] mb-3">{selectedTwin.name.split(" ")[0]} Will Love</h3>
                    <div className="space-y-4">
                      {suggestions.they_will_love.slice(0, 2).map((restaurant) => (
                        <RestaurantCard
                          key={restaurant.id || restaurant.restaurant_id}
                          restaurant={restaurant}
                          onClick={() => {
                            if (restaurant.url) {
                              window.open(restaurant.url, '_blank')
                            }
                          }}
                        />
                      ))}
                    </div>
                  </div>
                )}
              </>
            )}
          </>
        )}
      </div>
    </div>
  )
}

export default function DateNightPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-[#F8F9FA] flex items-center justify-center">
        <Loader2 className="w-8 h-8 text-[#FF6B6B] animate-spin" />
      </div>
    }>
      <DateNightPageContent />
    </Suspense>
  )
}
