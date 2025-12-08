"use client"

import type React from "react"

import { useState } from "react"
import { api, type Restaurant } from "@/lib/api"
import { RestaurantCard } from "@/components/restaurant-card"
import { useRouter } from "next/navigation"
import { SearchIcon, SlidersHorizontal, Loader2, MapPin } from "lucide-react"

export default function SearchPage() {
  const router = useRouter()
  const [query, setQuery] = useState("")
  const [results, setResults] = useState<Restaurant[]>([])
  const [loading, setLoading] = useState(false)
  const [searched, setSearched] = useState(false)
  const [location] = useState("San Francisco, CA")

  const handleSearch = async (e?: React.FormEvent) => {
    e?.preventDefault()
    setLoading(true)
    setSearched(true)

    try {
      const data = await api.searchRestaurants({
        location,
        term: query || undefined,
        limit: 20,
      })
      setResults(data.businesses)
    } catch (error) {
      console.error("Search failed:", error)
    } finally {
      setLoading(false)
    }
  }

  const popularCategories = [
    { label: "Japanese", emoji: "🍣" },
    { label: "Italian", emoji: "🍝" },
    { label: "Mexican", emoji: "🌮" },
    { label: "Thai", emoji: "🍜" },
    { label: "Indian", emoji: "🍛" },
    { label: "Korean", emoji: "🥘" },
  ]

  return (
    <div className="min-h-screen bg-[#F8F9FA]">
      {/* Header */}
      <div className="bg-white border-b border-[#E9ECEF] px-4 py-4 sticky top-0 z-10">
        <div className="max-w-md mx-auto">
          <form onSubmit={handleSearch} className="flex gap-2">
            <div className="flex-1 relative">
              <SearchIcon className="absolute left-4 top-3.5 w-5 h-5 text-[#ADB5BD]" />
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search restaurants, cuisines..."
                className="w-full h-12 px-4 pl-12 rounded-xl border border-[#DEE2E6] bg-white text-[#2C3E50] placeholder:text-[#ADB5BD] focus:border-[#FF6B6B] focus:ring-2 focus:ring-[#FF6B6B]/20 outline-none transition-all"
              />
            </div>
            <button
              type="button"
              className="w-12 h-12 rounded-xl bg-[#F8F9FA] border border-[#DEE2E6] flex items-center justify-center hover:bg-[#E9ECEF] transition-colors"
            >
              <SlidersHorizontal className="w-5 h-5 text-[#6C757D]" />
            </button>
          </form>

          <div className="flex items-center gap-1 mt-3 text-sm text-[#6C757D]">
            <MapPin className="w-4 h-4" />
            <span>{location}</span>
          </div>
        </div>
      </div>

      <div className="max-w-md mx-auto p-4 pb-32">
        {!searched ? (
          <>
            {/* Popular Categories */}
            <h2 className="font-semibold text-[#2C3E50] mb-3">Popular Categories</h2>
            <div className="grid grid-cols-3 gap-3 mb-6">
              {popularCategories.map(({ label, emoji }) => (
                <button
                  key={label}
                  onClick={() => {
                    setQuery(label)
                    handleSearch()
                  }}
                  className="bg-white rounded-xl p-4 shadow-sm hover:shadow-md transition-shadow text-center"
                >
                  <span className="text-2xl mb-2 block">{emoji}</span>
                  <span className="text-sm font-medium text-[#2C3E50]">{label}</span>
                </button>
              ))}
            </div>

            {/* Quick Search Tips */}
            <div className="bg-white rounded-xl p-4 shadow-sm">
              <h3 className="font-medium text-[#2C3E50] mb-2">Search Tips</h3>
              <ul className="text-sm text-[#6C757D] space-y-1">
                <li>• Try &ldquo;sushi near me&rdquo; or &ldquo;best pizza&rdquo;</li>
                <li>• Filter by price range or cuisine type</li>
                <li>• Look for high match scores from your twins</li>
              </ul>
            </div>
          </>
        ) : loading ? (
          <div className="flex flex-col items-center justify-center py-12">
            <Loader2 className="w-8 h-8 text-[#FF6B6B] animate-spin mb-4" />
            <p className="text-[#6C757D]">Searching restaurants...</p>
          </div>
        ) : results.length > 0 ? (
          <div className="space-y-4">
            <p className="text-sm text-[#6C757D]">{results.length} results found</p>
            {results.map((restaurant) => (
              <RestaurantCard
                key={restaurant.id}
                restaurant={restaurant}
                onClick={() => {
                  if (restaurant.url) {
                    window.open(restaurant.url, '_blank')
                  }
                }}
              />
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <SearchIcon className="w-12 h-12 text-[#CED4DA] mx-auto mb-4" />
            <p className="text-[#6C757D]">No restaurants found</p>
            <p className="text-sm text-[#ADB5BD]">Try a different search term</p>
          </div>
        )}
      </div>
    </div>
  )
}
