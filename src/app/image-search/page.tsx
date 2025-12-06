"use client"

import type React from "react"

import { useState, useRef } from "react"
import { useRouter } from "next/navigation"
import { RestaurantCard } from "@/components/restaurant-card"
import type { Restaurant } from "@/lib/api"
import { ArrowLeft, Camera, Upload, X, Loader2, Sparkles } from "lucide-react"

interface ImageSearchResult {
  detected_dish: string
  detected_cuisine: string
  confidence: number
  restaurants: (Restaurant & { similarity: number })[]
}

export default function ImageSearchPage() {
  const router = useRouter()
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [preview, setPreview] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<ImageSearchResult | null>(null)

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      const reader = new FileReader()
      reader.onloadend = () => {
        setPreview(reader.result as string)
      }
      reader.readAsDataURL(file)
    }
  }

  const handleSearch = async () => {
    if (!fileInputRef.current?.files?.[0]) return

    setLoading(true)
    try {
      const formData = new FormData()
      formData.append("file", fileInputRef.current.files[0])

      const token = localStorage.getItem("token")
      const response = await fetch("http://localhost:8000/api/v1/image-search/upload?location=San Francisco, CA", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      })

      if (response.ok) {
        const data = await response.json()
        setResult(data)
      }
    } catch (error) {
      console.error("Image search failed:", error)
    } finally {
      setLoading(false)
    }
  }

  const clearImage = () => {
    setPreview(null)
    setResult(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ""
    }
  }

  return (
    <div className="min-h-screen bg-[#F8F9FA]">
      {/* Header */}
      <div className="bg-[#FF6B6B] px-4 pt-4 pb-8">
        <div className="max-w-md mx-auto">
          <button
            onClick={() => router.back()}
            className="w-10 h-10 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center hover:bg-white/30 transition-colors mb-4"
          >
            <ArrowLeft className="w-5 h-5 text-white" />
          </button>

          <div className="text-center">
            <Camera className="w-12 h-12 text-white mx-auto mb-3" />
            <h1 className="text-2xl font-bold text-white">Snap to Find</h1>
            <p className="text-white/80 mt-1">Take a photo of food to find similar dishes</p>
          </div>
        </div>
      </div>

      <div className="max-w-md mx-auto px-4 -mt-4 pb-8">
        {/* Upload Area */}
        <div className="bg-white rounded-2xl shadow-lg p-4 mb-6">
          {!preview ? (
            <label className="block cursor-pointer">
              <div className="border-2 border-dashed border-[#DEE2E6] rounded-xl p-8 text-center hover:border-[#FF6B6B] transition-colors">
                <Upload className="w-12 h-12 text-[#ADB5BD] mx-auto mb-4" />
                <p className="font-medium text-[#2C3E50] mb-1">Upload a food photo</p>
                <p className="text-sm text-[#ADB5BD]">JPG, PNG up to 10MB</p>
              </div>
              <input ref={fileInputRef} type="file" accept="image/*" onChange={handleFileSelect} className="hidden" />
            </label>
          ) : (
            <div className="relative">
              <img
                src={preview || "/placeholder.svg"}
                alt="Food preview"
                className="w-full h-64 object-cover rounded-xl"
              />
              <button
                onClick={clearImage}
                className="absolute top-2 right-2 w-8 h-8 bg-black/50 rounded-full flex items-center justify-center"
              >
                <X className="w-5 h-5 text-white" />
              </button>
            </div>
          )}

          {preview && !result && (
            <button
              onClick={handleSearch}
              disabled={loading}
              className="w-full mt-4 h-12 rounded-xl bg-[#FF6B6B] text-white font-semibold flex items-center justify-center gap-2 hover:opacity-90 disabled:opacity-50"
            >
              {loading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <>
                  <Sparkles className="w-5 h-5" />
                  Find Similar Dishes
                </>
              )}
            </button>
          )}
        </div>

        {/* Results */}
        {result && (
          <>
            {/* Detection Result */}
            <div className="bg-[#FF6B6B]/5 rounded-2xl p-4 mb-6 border border-[#FF6B6B]/20">
              <div className="flex items-center gap-2 mb-2">
                <Sparkles className="w-5 h-5 text-[#FF6B6B]" />
                <span className="font-semibold text-[#2C3E50]">We detected:</span>
              </div>
              <p className="text-lg font-bold text-[#2C3E50]">{result.detected_dish}</p>
              <p className="text-sm text-[#6C757D]">
                {result.detected_cuisine} cuisine • {Math.round(result.confidence * 100)}% confidence
              </p>
            </div>

            {/* Restaurant Suggestions */}
            <h3 className="font-semibold text-[#2C3E50] mb-3">Restaurants with this dish</h3>
            <div className="space-y-4">
              {result.restaurants.map((restaurant) => (
                <RestaurantCard
                  key={restaurant.id || restaurant.restaurant_id}
                  restaurant={restaurant}
                  onClick={() => router.push(`/restaurant/${restaurant.id || restaurant.restaurant_id}`)}
                />
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  )
}
