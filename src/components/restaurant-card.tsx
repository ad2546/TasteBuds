"use client"

import type React from "react"

import { useState } from "react"
import { Heart, Star, MapPin, CheckCircle } from "lucide-react"
import { type Restaurant, api } from "@/lib/api"

interface RestaurantCardProps {
  restaurant: Restaurant
  onClick?: () => void
}

export function RestaurantCard({ restaurant, onClick }: RestaurantCardProps) {
  const [saved, setSaved] = useState(false)
  const [saving, setSaving] = useState(false)
  const [visited, setVisited] = useState(false)
  const [marking, setMarking] = useState(false)

  const handleSave = async (e: React.MouseEvent) => {
    e.stopPropagation()
    if (saving) return

    setSaving(true)
    try {
      await api.saveRestaurant(restaurant.id || restaurant.restaurant_id || "")
      setSaved(true)
    } catch (error) {
      console.error("Failed to save:", error)
    } finally {
      setSaving(false)
    }
  }

  const handleBeenHere = async (e: React.MouseEvent) => {
    e.stopPropagation()
    if (marking || visited) return

    setMarking(true)
    try {
      await api.logInteraction(restaurant.id || restaurant.restaurant_id || "", {
        action_type: "visited",
        context: "search",
      })
      setVisited(true)
    } catch (error) {
      console.error("Failed to mark as visited:", error)
    } finally {
      setMarking(false)
    }
  }

  const matchPercent = Math.round((restaurant.match_score || 0) * 100)
  const category = restaurant.category || restaurant.categories?.[0]?.title || "Restaurant"

  return (
    <div
      onClick={onClick}
      className="bg-white rounded-2xl overflow-hidden shadow-md hover:shadow-xl transition-shadow cursor-pointer group"
    >
      {/* Image */}
      <div className="relative h-48 overflow-hidden">
        <img
          src={restaurant.image_url || "/placeholder.svg?height=192&width=400&query=restaurant food"}
          alt={restaurant.name}
          className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300"
        />

        {/* Match Score Badge */}
        {matchPercent > 0 && (
          <div className="absolute top-3 right-3 bg-white/95 backdrop-blur-sm px-3 py-1.5 rounded-full font-semibold text-sm flex items-center gap-1">
            <span className="text-[#51CF66]">{matchPercent}%</span>
            <span className="text-[#6C757D]">Match</span>
          </div>
        )}

        {/* Save Heart */}
        <button
          onClick={handleSave}
          disabled={saving || saved}
          className="absolute top-3 left-3 w-10 h-10 bg-white/95 backdrop-blur-sm rounded-full flex items-center justify-center hover:scale-110 transition-transform"
        >
          <Heart
            className={`w-5 h-5 transition-colors ${saved ? "fill-[#FF6B6B] text-[#FF6B6B]" : "text-[#6C757D]"}`}
          />
        </button>
      </div>

      {/* Content */}
      <div className="p-4">
        {/* Been Here Button */}
        <button
          onClick={handleBeenHere}
          disabled={marking || visited}
          className={`w-full mb-3 px-3 py-2 rounded-lg flex items-center justify-center gap-2 text-sm font-medium transition-all ${
            visited
              ? "bg-[#51CF66]/10 text-[#51CF66] border-2 border-[#51CF66]"
              : "bg-[#F8F9FA] text-[#6C757D] border-2 border-[#DEE2E6] hover:border-[#51CF66] hover:text-[#51CF66]"
          }`}
        >
          <CheckCircle className={`w-4 h-4 ${visited ? "fill-[#51CF66]" : ""}`} />
          {visited ? "Been Here!" : "Been Here?"}
        </button>
        <h3 className="font-bold text-lg text-[#2C3E50] mb-1 truncate">{restaurant.name}</h3>
        <div className="flex items-center gap-2 mb-2 flex-wrap">
          <div className="flex items-center">
            <Star className="w-4 h-4 text-yellow-400 fill-yellow-400" />
            <span className="ml-1 text-sm font-medium text-[#2C3E50]">{restaurant.rating}</span>
          </div>
          <span className="text-[#CED4DA]">•</span>
          <span className="text-sm text-[#6C757D]">{restaurant.price || "$$"}</span>
          <span className="text-[#CED4DA]">•</span>
          <span className="text-sm text-[#6C757D] truncate">{category}</span>
        </div>
        <div className="flex items-center text-sm text-[#ADB5BD]">
          <MapPin className="w-4 h-4 mr-1" />
          {restaurant.distance ? `${(restaurant.distance / 1000).toFixed(1)} mi away` : restaurant.location?.city}
        </div>
      </div>
    </div>
  )
}
