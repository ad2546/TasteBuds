"use client"

import { useState, useEffect } from "react"
import { useRouter, useParams } from "next/navigation"
import { api, type RestaurantDetail, type Review } from "@/lib/api"
import { ArrowLeft, Star, MapPin, Phone, Clock, ExternalLink, Heart, Navigation, Loader2, Share2 } from "lucide-react"

export default function RestaurantPage() {
  const router = useRouter()
  const params = useParams()
  const restaurantId = params.id as string

  const [restaurant, setRestaurant] = useState<RestaurantDetail | null>(null)
  const [reviews, setReviews] = useState<Review[]>([])
  const [loading, setLoading] = useState(true)
  const [saved, setSaved] = useState(false)
  const [activeImage, setActiveImage] = useState(0)

  useEffect(() => {
    loadData()
  }, [restaurantId])

  const loadData = async () => {
    try {
      console.log("Loading restaurant with ID:", restaurantId)
      const [restaurantData, reviewsData] = await Promise.all([
        api.getRestaurant(restaurantId),
        api.getRestaurantReviews(restaurantId),
      ])
      console.log("Restaurant data loaded:", restaurantData)
      setRestaurant(restaurantData)
      setReviews(reviewsData.reviews)
    } catch (error) {
      console.error("Failed to load restaurant with ID:", restaurantId, error)
      // Show user-friendly error message
      if (error instanceof Error && error.message.includes("404")) {
        console.warn("Restaurant not found in Yelp database - may have been removed or ID is invalid")
      }
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async () => {
    if (!restaurant || saved) return
    try {
      await api.saveRestaurant(restaurantId)
      setSaved(true)
    } catch (error) {
      console.error("Failed to save:", error)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-[#F8F9FA] flex items-center justify-center">
        <Loader2 className="w-8 h-8 text-[#FF6B6B] animate-spin" />
      </div>
    )
  }

  if (!restaurant) {
    return (
      <div className="min-h-screen bg-[#F8F9FA] flex flex-col items-center justify-center p-4">
        <div className="text-center max-w-md">
          <p className="text-xl font-semibold text-[#2C3E50] mb-2">Restaurant Not Available</p>
          <p className="text-[#6C757D] mb-6">This restaurant may no longer be listed on Yelp or the link may be outdated.</p>
          <button onClick={() => router.back()} className="px-6 py-3 bg-[#FF6B6B] text-white rounded-xl font-medium hover:bg-[#FF5252] transition-colors">
            Go Back
          </button>
        </div>
      </div>
    )
  }

  const images =
    restaurant.photos?.length > 0 ? restaurant.photos : [restaurant.image_url || "/cozy-italian-restaurant.png"]
  const matchPercent = Math.round((restaurant.match_score || 0) * 100)
  const category = restaurant.category || restaurant.categories?.[0]?.title || "Restaurant"

  return (
    <div className="min-h-screen bg-[#F8F9FA] pb-24">
      {/* Image Gallery */}
      <div className="relative h-72">
        <img
          src={images[activeImage] || "/placeholder.svg"}
          alt={restaurant.name}
          className="w-full h-full object-cover"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent" />

        {/* Navigation */}
        <div className="absolute top-4 left-4 right-4 flex justify-between">
          <button
            onClick={() => router.back()}
            className="w-10 h-10 bg-white/95 backdrop-blur-sm rounded-full flex items-center justify-center"
          >
            <ArrowLeft className="w-5 h-5 text-[#2C3E50]" />
          </button>
          <div className="flex gap-2">
            <button className="w-10 h-10 bg-white/95 backdrop-blur-sm rounded-full flex items-center justify-center">
              <Share2 className="w-5 h-5 text-[#2C3E50]" />
            </button>
          </div>
        </div>

        {/* Image Dots */}
        {images.length > 1 && (
          <div className="absolute bottom-4 left-0 right-0 flex justify-center gap-1.5">
            {images.map((_, i) => (
              <button
                key={i}
                onClick={() => setActiveImage(i)}
                className={`w-2 h-2 rounded-full transition-all ${i === activeImage ? "bg-white w-4" : "bg-white/50"}`}
              />
            ))}
          </div>
        )}

        {/* Match Score */}
        {matchPercent > 0 && (
          <div className="absolute bottom-4 right-4 bg-[#51CF66] text-white px-3 py-1 rounded-full text-sm font-bold">
            {matchPercent}% Match
          </div>
        )}
      </div>

      <div className="max-w-md mx-auto px-4">
        {/* Info Card */}
        <div className="bg-white rounded-2xl shadow-lg p-4 -mt-6 relative mb-4">
          <h1 className="text-xl font-bold text-[#2C3E50] mb-2">{restaurant.name}</h1>

          <div className="flex items-center gap-3 mb-3 flex-wrap">
            <div className="flex items-center">
              <Star className="w-5 h-5 text-yellow-400 fill-yellow-400" />
              <span className="ml-1 font-semibold text-[#2C3E50]">{restaurant.rating}</span>
              <span className="text-[#ADB5BD] ml-1">({restaurant.review_count})</span>
            </div>
            <span className="text-[#CED4DA]">•</span>
            <span className="text-[#6C757D]">{restaurant.price}</span>
            <span className="text-[#CED4DA]">•</span>
            <span className="text-[#6C757D]">{category}</span>
          </div>

          <div className="space-y-2 text-[#6C757D]">
            <div className="flex items-start gap-2">
              <MapPin className="w-5 h-5 mt-0.5 flex-shrink-0 text-[#ADB5BD]" />
              <span>{restaurant.location?.display_address?.join(", ") || restaurant.location?.city}</span>
            </div>
            {restaurant.phone && (
              <div className="flex items-center gap-2">
                <Phone className="w-5 h-5 flex-shrink-0 text-[#ADB5BD]" />
                <span>{restaurant.phone}</span>
              </div>
            )}
            <div className="flex items-center gap-2">
              <Clock className="w-5 h-5 flex-shrink-0 text-[#ADB5BD]" />
              <span className={restaurant.is_closed ? "text-[#FF6B6B]" : "text-[#51CF66]"}>
                {restaurant.is_closed ? "Closed" : "Open Now"}
              </span>
            </div>
          </div>
        </div>

        {/* Reviews */}
        {reviews.length > 0 && (
          <div className="bg-white rounded-2xl shadow-sm p-4 mb-4">
            <h3 className="font-semibold text-[#2C3E50] mb-4">Reviews</h3>
            <div className="space-y-4">
              {reviews.slice(0, 3).map((review) => (
                <div key={review.id} className="border-b border-[#E9ECEF] last:border-0 pb-4 last:pb-0">
                  <div className="flex items-start gap-3">
                    <img
                      src={review.user.image_url || "/placeholder.svg?height=40&width=40&query=avatar"}
                      alt={review.user.name}
                      className="w-10 h-10 rounded-full object-cover"
                    />
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-medium text-[#2C3E50]">{review.user.name}</span>
                        <div className="flex items-center">
                          {[...Array(5)].map((_, i) => (
                            <Star
                              key={i}
                              className={`w-3 h-3 ${
                                i < review.rating ? "text-yellow-400 fill-yellow-400" : "text-[#E9ECEF]"
                              }`}
                            />
                          ))}
                        </div>
                      </div>
                      <p className="text-sm text-[#6C757D] line-clamp-3">{review.text}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Fixed Bottom Actions */}
      <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-[#E9ECEF] px-4 py-3">
        <div className="max-w-md mx-auto flex gap-3">
          <button
            onClick={handleSave}
            disabled={saved}
            className={`w-14 h-12 rounded-xl flex items-center justify-center transition-all ${
              saved ? "bg-[#FF6B6B]/10" : "border-2 border-[#DEE2E6] hover:border-[#FF6B6B]"
            }`}
          >
            <Heart className={`w-6 h-6 ${saved ? "fill-[#FF6B6B] text-[#FF6B6B]" : "text-[#6C757D]"}`} />
          </button>
          <button
            onClick={() => window.open(restaurant.url, "_blank")}
            className="flex-1 h-12 rounded-xl border-2 border-[#DEE2E6] text-[#6C757D] font-medium flex items-center justify-center gap-2 hover:bg-[#F8F9FA]"
          >
            <ExternalLink className="w-5 h-5" />
            Yelp
          </button>
          <button className="flex-1 h-12 rounded-xl bg-[#FF6B6B] text-white font-medium flex items-center justify-center gap-2 hover:bg-[#FF5252]">
            <Navigation className="w-5 h-5" />
            Directions
          </button>
        </div>
      </div>
    </div>
  )
}
