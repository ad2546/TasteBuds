"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { api, type FeelingLuckyResponse, type AIChatResponse } from "@/lib/api"
import { ArrowLeft, Star, MapPin, Phone, ExternalLink, Heart, Navigation, RefreshCw, Sparkles, MessageCircle, Send, Wand2 } from "lucide-react"
import { ProtectedRoute } from "@/components/protected-route"

function FeelingLuckyPageContent() {
  const router = useRouter()
  const [restaurant, setRestaurant] = useState<FeelingLuckyResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [saved, setSaved] = useState(false)
  const [location] = useState("San Francisco, CA")

  // AI Search states
  const [showAISearch, setShowAISearch] = useState(true)
  const [aiQuery, setAiQuery] = useState("")
  const [aiLoading, setAiLoading] = useState(false)
  const [aiResponse, setAiResponse] = useState<AIChatResponse | null>(null)

  // Q&A states
  const [showQA, setShowQA] = useState(false)
  const [question, setQuestion] = useState("")
  const [answer, setAnswer] = useState("")
  const [qaLoading, setQaLoading] = useState(false)

  const handleAISearch = async () => {
    if (!aiQuery.trim()) return

    setAiLoading(true)
    setShowAISearch(false)
    setLoading(true)

    try {
      // Use AI smart search with user's natural language query
      const result = await api.aiSmartSearch(aiQuery, 37.7749, -122.4194)
      setAiResponse(result)

      // If we got businesses, show the first one
      if (result.businesses && result.businesses.length > 0) {
        const firstBusiness = result.businesses[0]

        // Get image from contextual_info.photos or fallback to image_url
        const imageUrl = firstBusiness.contextual_info?.photos?.[0]?.original_url ||
                        firstBusiness.image_url ||
                        "https://via.placeholder.com/400x300?text=No+Image"

        // Get short summary from Yelp AI summaries
        const aiSummary = firstBusiness.summaries?.short ||
                         firstBusiness.summaries?.medium ||
                         result.text ||
                         "AI recommended based on your preferences"

        setRestaurant({
          ...firstBusiness,
          id: firstBusiness.id,
          name: firstBusiness.name,
          image_url: imageUrl,
          rating: firstBusiness.rating,
          review_count: firstBusiness.review_count,
          price: firstBusiness.price,
          category: firstBusiness.categories?.[0]?.title || "Restaurant",
          location: {
            address: firstBusiness.location?.formatted_address ||
                    firstBusiness.location?.display_address?.join(", ") ||
                    firstBusiness.location?.address1,
            city: firstBusiness.location?.city,
          },
          match_score: 0.95,
          explanation: aiSummary,
          twin_recommendations: [],
        })
      }
    } catch (error) {
      console.error("AI search failed:", error)
    } finally {
      setAiLoading(false)
      setLoading(false)
    }
  }

  const loadLucky = async () => {
    setLoading(true)
    setShowAISearch(false)
    try {
      const data = await api.getFeelingLucky(location)
      const restaurantData = (data as any).restaurant || data
      setRestaurant({
        ...restaurantData,
        category: restaurantData.categories?.[0]?.title || "Restaurant",
        location: {
          ...restaurantData.location,
          address: restaurantData.location?.display_address?.join(", ") || restaurantData.location?.address1,
          city: restaurantData.location?.city,
        },
        match_score: (data as any).confidence || 0.85,
        twin_recommendations: (data as any).twin_recommendations || [],
        explanation: (data as any).explanation || "Recommended based on your taste preferences",
      })
      setSaved(false)
    } catch (error) {
      console.error("Failed to load:", error)
    } finally {
      setLoading(false)
    }
  }

  const handleAskQuestion = async () => {
    if (!question.trim() || !restaurant) return

    setQaLoading(true)
    try {
      const result = await api.aiAskAboutRestaurant(
        restaurant.id || restaurant.restaurant_id || "",
        question,
        37.7749,
        -122.4194
      )
      setAnswer(result.text || "I couldn't find an answer to that question.")
      setQuestion("")
    } catch (error) {
      console.error("Failed to get answer:", error)
      setAnswer("Sorry, I couldn't answer that question right now.")
    } finally {
      setQaLoading(false)
    }
  }

  const handleSave = async () => {
    if (!restaurant || saved) return
    try {
      await api.saveRestaurant(restaurant.id || restaurant.restaurant_id || "")
      setSaved(true)
    } catch (error) {
      console.error("Failed to save:", error)
    }
  }

  const matchPercent = Math.round((restaurant?.match_score || 0) * 100)

  // AI Search Screen
  if (showAISearch) {
    return (
      <div className="min-h-screen bg-white flex flex-col items-center justify-center p-4">
        <div className="w-full max-w-md">
          {/* Header */}
          <button
            onClick={() => router.back()}
            className="mb-8 flex items-center gap-2 text-[#6C757D] hover:text-[#2C3E50]"
          >
            <ArrowLeft className="w-5 h-5" />
            Back
          </button>

          {/* AI Search Box */}
          <div className="bg-white rounded-2xl shadow-xl p-6 mb-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 bg-[#FF6B6B] rounded-full flex items-center justify-center">
                <Wand2 className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-[#2C3E50]">AI Restaurant Discovery</h1>
                <p className="text-sm text-[#6C757D]">Tell me what you're looking for</p>
              </div>
            </div>

            <div className="space-y-3">
              <textarea
                value={aiQuery}
                onChange={(e) => setAiQuery(e.target.value)}
                placeholder="e.g., 'Find me a cozy Italian spot for a first date' or 'I want spicy Thai food with outdoor seating'"
                className="w-full h-24 px-4 py-3 rounded-xl border border-[#DEE2E6] bg-white text-[#2C3E50] placeholder:text-[#ADB5BD] focus:border-[#FF6B6B] focus:ring-2 focus:ring-[#FF6B6B]/20 outline-none transition-all resize-none"
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault()
                    handleAISearch()
                  }
                }}
              />

              <button
                onClick={handleAISearch}
                disabled={aiLoading || !aiQuery.trim()}
                className="w-full h-12 rounded-xl bg-[#FF6B6B] text-white font-semibold flex items-center justify-center gap-2 hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {aiLoading ? (
                  <>
                    <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    Searching with AI...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-5 h-5" />
                    Search with AI
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Quick Options */}
          <div className="space-y-3">
            <p className="text-sm text-[#6C757D] text-center">Or try one of these:</p>
            <div className="grid grid-cols-1 gap-2">
              {[
                "Find me a romantic spot for date night",
                "I want adventurous fusion cuisine",
                "Show me budget-friendly Mexican places",
                "Find upscale Japanese with great ambiance",
              ].map((suggestion) => (
                <button
                  key={suggestion}
                  onClick={() => {
                    setAiQuery(suggestion)
                    setTimeout(() => {
                      // Auto-trigger search after setting query
                      const event = new Event('click')
                      handleAISearch()
                    }, 100)
                  }}
                  className="text-left px-4 py-3 rounded-xl bg-white border border-[#E9ECEF] text-[#6C757D] text-sm hover:border-[#FF6B6B] hover:text-[#FF6B6B] transition-all"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>

          {/* Divider */}
          <div className="flex items-center gap-4 my-6">
            <div className="flex-1 h-px bg-[#E9ECEF]" />
            <span className="text-sm text-[#ADB5BD]">or</span>
            <div className="flex-1 h-px bg-[#E9ECEF]" />
          </div>

          {/* Traditional Feeling Lucky */}
          <button
            onClick={loadLucky}
            className="w-full h-14 rounded-xl bg-white border-2 border-[#4ECDC4] text-[#4ECDC4] font-semibold flex items-center justify-center gap-2 hover:bg-[#4ECDC4]/5 transition-all"
          >
            <Sparkles className="w-5 h-5" />
            Use Traditional Feeling Lucky
          </button>
        </div>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-neutral-50 flex flex-col items-center justify-center p-4">
        <div className="relative">
          <div className="w-24 h-24 rounded-full border-4 border-[#FF6B6B]/20 border-t-[#FF6B6B] animate-spin" />
          <Sparkles className="absolute inset-0 m-auto w-10 h-10 text-[#FFA94D]" />
        </div>
        <p className="mt-6 text-xl font-semibold text-gray-900">
          {aiQuery ? "AI is finding your perfect match..." : "Finding your perfect match..."}
        </p>
        <p className="text-gray-600 mt-2">
          {aiQuery ? "Understanding your preferences" : "Analyzing your taste DNA"}
        </p>
      </div>
    )
  }

  if (!restaurant) {
    return (
      <div className="min-h-screen bg-[#F8F9FA] flex flex-col items-center justify-center p-4">
        <Sparkles className="w-16 h-16 text-[#ADB5BD] mb-4" />
        <p className="text-[#6C757D] mb-4">No restaurants found</p>
        <button
          onClick={() => setShowAISearch(true)}
          className="px-6 py-3 bg-[#FF6B6B] text-white rounded-xl font-medium"
        >
          Try Again
        </button>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-[#F8F9FA] pb-[60px] md:pb-0">
      {/* Header Image */}
      <div className="relative h-72">
        <img
          src={restaurant.image_url || "/placeholder.svg?height=288&width=400&query=restaurant food"}
          alt={restaurant.name}
          className="w-full h-full object-cover"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent" />

        {/* Back Button */}
        <button
          onClick={() => setShowAISearch(true)}
          className="absolute top-4 left-4 w-10 h-10 bg-white/95 backdrop-blur-sm rounded-full flex items-center justify-center"
        >
          <ArrowLeft className="w-5 h-5 text-[#2C3E50]" />
        </button>

        {/* Refresh Button */}
        <button
          onClick={() => setShowAISearch(true)}
          className="absolute top-4 right-4 w-10 h-10 bg-white/95 backdrop-blur-sm rounded-full flex items-center justify-center"
        >
          <RefreshCw className="w-5 h-5 text-[#2C3E50]" />
        </button>

        {/* Match Score */}
        <div className="absolute bottom-4 left-4 right-4 flex items-end justify-between">
          <div>
            <div className="inline-flex items-center gap-1 bg-[#51CF66] text-white px-3 py-1 rounded-full text-sm font-bold mb-2">
              <Sparkles className="w-4 h-4" />
              {matchPercent}% Match
            </div>
            <h1 className="text-2xl font-bold text-white">{restaurant.name}</h1>
          </div>
        </div>
      </div>

      <div className="max-w-md mx-auto p-4 space-y-4 -mt-4">
        {/* Info Card */}
        <div className="bg-white rounded-2xl shadow-lg p-4">
          <div className="flex items-center gap-4 mb-4">
            <div className="flex items-center">
              <Star className="w-5 h-5 text-yellow-400 fill-yellow-400" />
              <span className="ml-1 font-semibold text-[#2C3E50]">{restaurant.rating}</span>
              <span className="text-[#ADB5BD] ml-1">({restaurant.review_count})</span>
            </div>
            <span className="text-[#CED4DA]">•</span>
            <span className="text-[#6C757D]">{restaurant.price}</span>
            <span className="text-[#CED4DA]">•</span>
            <span className="text-[#6C757D]">{restaurant.category}</span>
          </div>

          <div className="flex items-start gap-2 text-[#6C757D]">
            <MapPin className="w-5 h-5 mt-0.5 flex-shrink-0" />
            <span>{restaurant.location?.address || restaurant.location?.city}</span>
          </div>
        </div>

        {/* AI Explanation */}
        {aiResponse?.text && (
          <div className="bg-[#FF6B6B]/5 rounded-2xl p-4 border border-[#FF6B6B]/20">
            <h3 className="font-semibold text-[#2C3E50] mb-2 flex items-center gap-2">
              <Wand2 className="w-5 h-5 text-[#FF6B6B]" />
              AI Recommendation
            </h3>
            <p className="text-[#6C757D] text-sm leading-relaxed">{aiResponse.text}</p>
          </div>
        )}

        {/* Why This Match */}
        <div className="bg-[#4ECDC4]/10 rounded-2xl p-4 border border-[#4ECDC4]/20">
          <h3 className="font-semibold text-[#2C3E50] mb-2 flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-[#4ECDC4]" />
            Why this matches you
          </h3>
          <p className="text-[#6C757D] text-sm leading-relaxed">{restaurant.explanation}</p>
        </div>

        {/* AI Q&A Section */}
        <div className="bg-white rounded-2xl shadow-sm p-4">
          <button
            onClick={() => setShowQA(!showQA)}
            className="w-full flex items-center justify-between"
          >
            <h3 className="font-semibold text-[#2C3E50] flex items-center gap-2">
              <MessageCircle className="w-5 h-5 text-[#FF6B6B]" />
              Ask AI about this restaurant
            </h3>
            <span className="text-[#FF6B6B] text-sm">{showQA ? "Hide" : "Ask"}</span>
          </button>

          {showQA && (
            <div className="mt-4 space-y-3">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  placeholder="e.g., Is this place kid-friendly?"
                  className="flex-1 h-10 px-4 rounded-lg border border-[#DEE2E6] text-sm focus:border-[#FF6B6B] focus:ring-2 focus:ring-[#FF6B6B]/20 outline-none"
                  onKeyDown={(e) => {
                    if (e.key === "Enter") {
                      e.preventDefault()
                      handleAskQuestion()
                    }
                  }}
                />
                <button
                  onClick={handleAskQuestion}
                  disabled={qaLoading || !question.trim()}
                  className="px-4 h-10 rounded-lg bg-[#FF6B6B] text-white flex items-center justify-center disabled:opacity-50"
                >
                  {qaLoading ? (
                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  ) : (
                    <Send className="w-4 h-4" />
                  )}
                </button>
              </div>

              {/* Quick Questions */}
              <div className="flex flex-wrap gap-2">
                {["Parking available?", "Good for kids?", "Vegan options?", "Outdoor seating?"].map((q) => (
                  <button
                    key={q}
                    onClick={() => {
                      setQuestion(q)
                      setTimeout(handleAskQuestion, 100)
                    }}
                    className="text-xs px-3 py-1.5 rounded-full bg-[#F8F9FA] text-[#6C757D] hover:bg-[#FF6B6B]/10 hover:text-[#FF6B6B]"
                  >
                    {q}
                  </button>
                ))}
              </div>

              {answer && (
                <div className="p-3 rounded-lg bg-[#F8F9FA] border border-[#E9ECEF]">
                  <p className="text-sm text-[#2C3E50]">{answer}</p>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Action Buttons */}
        <div className="grid grid-cols-2 gap-3">
          <button
            onClick={handleSave}
            disabled={saved}
            className={`h-12 rounded-xl font-medium flex items-center justify-center gap-2 transition-all ${
              saved
                ? "bg-[#FF6B6B]/10 text-[#FF6B6B]"
                : "bg-white border-2 border-[#FF6B6B] text-[#FF6B6B] hover:bg-[#FFE5E5]"
            }`}
          >
            <Heart className={`w-5 h-5 ${saved ? "fill-[#FF6B6B]" : ""}`} />
            {saved ? "Saved" : "Save"}
          </button>
          <button className="h-12 rounded-xl bg-[#FF6B6B] text-white font-medium flex items-center justify-center gap-2 hover:bg-[#FF5252] transition-colors">
            <Navigation className="w-5 h-5" />
            Directions
          </button>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <button className="h-12 rounded-xl bg-white border border-[#DEE2E6] text-[#6C757D] font-medium flex items-center justify-center gap-2 hover:bg-[#F8F9FA] transition-colors">
            <Phone className="w-5 h-5" />
            Call
          </button>
          <button className="h-12 rounded-xl bg-white border border-[#DEE2E6] text-[#6C757D] font-medium flex items-center justify-center gap-2 hover:bg-[#F8F9FA] transition-colors">
            <ExternalLink className="w-5 h-5" />
            Yelp
          </button>
        </div>
      </div>
    </div>
  )
}

export default function FeelingLuckyPage() {
  return (
    <ProtectedRoute>
      <FeelingLuckyPageContent />
    </ProtectedRoute>
  )
}
