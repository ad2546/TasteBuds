"use client"

import { useState, useEffect } from "react"
import { api, type SavedRestaurant } from "@/lib/api"
import { Loader2, Heart, Star, Trash2 } from "lucide-react"
import { ProtectedRoute } from "@/components/protected-route"

function SavedPageContent() {
  const [saved, setSaved] = useState<SavedRestaurant[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadSaved()
  }, [])

  const loadSaved = async () => {
    try {
      const data = await api.getSavedRestaurants()
      setSaved(data)
    } catch (error) {
      console.error("Failed to load saved:", error)
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
      <div className="bg-white border-b border-[#E9ECEF] px-4 py-4">
        <div className="max-w-md mx-auto">
          <h1 className="text-xl font-bold text-[#2C3E50]">Saved Restaurants</h1>
          <p className="text-sm text-[#6C757D]">{saved.length} places saved</p>
        </div>
      </div>

      <div className="max-w-md mx-auto p-4">
        {saved.length > 0 ? (
          <div className="space-y-3">
            {saved.map((item) => (
              <div key={item.restaurant_id} className="bg-white rounded-xl shadow-sm overflow-hidden flex">
                <img
                  src={item.restaurant_data?.image_url || "/placeholder.svg?height=100&width=100&query=restaurant"}
                  alt={item.restaurant_name}
                  className="w-24 h-24 object-cover"
                />
                <div className="flex-1 p-3 flex flex-col justify-between">
                  <div>
                    <h3 className="font-semibold text-[#2C3E50] truncate">{item.restaurant_name}</h3>
                    <div className="flex items-center gap-2 mt-1">
                      <Star className="w-4 h-4 text-yellow-400 fill-yellow-400" />
                      <span className="text-sm text-[#6C757D]">
                        {item.restaurant_data?.rating} • {item.restaurant_data?.price}
                      </span>
                    </div>
                    {item.notes && <p className="text-xs text-[#ADB5BD] mt-1 truncate">{item.notes}</p>}
                  </div>
                  <p className="text-xs text-[#CED4DA]">Saved {new Date(item.saved_at).toLocaleDateString()}</p>
                </div>
                <button className="px-3 flex items-center text-[#CED4DA] hover:text-[#FF6B6B] transition-colors">
                  <Trash2 className="w-5 h-5" />
                </button>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <Heart className="w-12 h-12 text-[#CED4DA] mx-auto mb-4" />
            <p className="text-[#6C757D] font-medium">No saved restaurants</p>
            <p className="text-sm text-[#ADB5BD]">Save restaurants to find them easily later</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default function SavedPage() {
  return (
    <ProtectedRoute>
      <SavedPageContent />
    </ProtectedRoute>
  )
}
