"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { api, type TasteTwin } from "@/lib/api"
import { TwinAvatar } from "@/components/twin-avatar"
import { ArrowLeft, RefreshCw, Loader2, Users, Flame, Sparkles } from "lucide-react"
import { ProtectedRoute } from "@/components/protected-route"

function TwinsPageContent() {
  const router = useRouter()
  const [twins, setTwins] = useState<TasteTwin[]>([])
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)

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

  const handleRefresh = async () => {
    setRefreshing(true)
    try {
      await fetch("http://localhost:8000/api/v1/twins/refresh", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
      })
      await loadTwins()
    } catch (error) {
      console.error("Failed to refresh:", error)
    } finally {
      setRefreshing(false)
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
      <div className="bg-[#FF6B6B] px-4 pt-4 pb-12">
        <div className="max-w-md mx-auto">
          <div className="flex items-center justify-between mb-6">
            <button
              onClick={() => router.back()}
              className="w-10 h-10 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center hover:bg-white/30 transition-colors"
            >
              <ArrowLeft className="w-5 h-5 text-white" />
            </button>
            <button
              onClick={handleRefresh}
              disabled={refreshing}
              className="w-10 h-10 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center hover:bg-white/30 transition-colors disabled:opacity-50"
            >
              <RefreshCw className={`w-5 h-5 text-white ${refreshing ? "animate-spin" : ""}`} />
            </button>
          </div>

          <div className="text-center">
            <Users className="w-12 h-12 text-white mx-auto mb-3" />
            <h1 className="text-2xl font-bold text-white">Taste Twins</h1>
            <p className="text-white/80 mt-1">People who share your taste</p>
          </div>
        </div>
      </div>

      <div className="max-w-md mx-auto px-4 -mt-6">
        {twins.length > 0 ? (
          <div className="space-y-4">
            {twins.map((twin) => (
              <div
                key={twin.twin_id}
                onClick={() => router.push(`/date-night?partner=${twin.twin_id}`)}
                className="bg-white rounded-2xl shadow-lg p-4 cursor-pointer hover:shadow-xl transition-shadow"
              >
                <div className="flex items-start gap-4">
                  <TwinAvatar twin={twin} size="lg" />

                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-1">
                      <h3 className="font-semibold text-[#2C3E50]">{twin.name}</h3>
                      <span className="text-sm font-bold text-[#FF6B6B]">
                        {Math.round(twin.similarity_score * 100)}% Match
                      </span>
                    </div>

                    {/* Shared Cuisines */}
                    <div className="flex flex-wrap gap-1 mb-3">
                      {twin.shared_cuisines.slice(0, 3).map((cuisine) => (
                        <span key={cuisine} className="px-2 py-0.5 bg-[#FF6B6B]/10 text-[#FF6B6B] text-xs rounded-full">
                          {cuisine}
                        </span>
                      ))}
                    </div>

                    {/* Stats */}
                    <div className="flex items-center gap-4 text-xs text-[#ADB5BD]">
                      <div className="flex items-center gap-1">
                        <Sparkles className="w-3 h-3 text-[#FFA94D]" />
                        <span>{Math.round(twin.adventure_score * 100)}% Adventure</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <Flame className="w-3 h-3 text-[#FF6B6B]" />
                        <span>{Math.round(twin.spice_tolerance * 100)}% Spice</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="bg-white rounded-2xl shadow-lg p-8 text-center">
            <Users className="w-12 h-12 text-[#CED4DA] mx-auto mb-4" />
            <h3 className="font-semibold text-[#2C3E50] mb-2">No Taste Twins Yet</h3>
            <p className="text-sm text-[#6C757D] mb-4">
              Complete your taste quiz to find people with similar food preferences.
            </p>
            <button
              onClick={() => router.push("/quiz")}
              className="px-6 py-2 bg-[#FF6B6B] text-white rounded-xl font-medium hover:opacity-90 transition-opacity"
            >
              Take Quiz
            </button>
          </div>
        )}
      </div>
    </div>
  )
}

export default function TwinsPage() {
  return (
    <ProtectedRoute>
      <TwinsPageContent />
    </ProtectedRoute>
  )
}
