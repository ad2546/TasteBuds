"use client"

import { useRouter } from "next/navigation"
import { ArrowLeft, Heart, Users, Sparkles, Target, Zap, Globe } from "lucide-react"

export default function AboutPage() {
  const router = useRouter()

  const features = [
    {
      icon: Sparkles,
      title: "TasteDNA",
      description: "Unique taste profile based on your food preferences",
      color: "#FFA94D",
    },
    {
      icon: Users,
      title: "Taste Twins",
      description: "Find people who share your culinary interests",
      color: "#FF6B6B",
    },
    {
      icon: Heart,
      title: "Smart Recommendations",
      description: "Personalized restaurant suggestions just for you",
      color: "#51CF66",
    },
    {
      icon: Zap,
      title: "Instant Discovery",
      description: "Explore new restaurants with Feeling Lucky",
      color: "#4ECDC4",
    },
  ]

  return (
    <div className="min-h-screen bg-[#F8F9FA]">
      {/* Header */}
      <div className="bg-white border-b border-[#E9ECEF] px-4 py-4 sticky top-0 z-10">
        <div className="max-w-md mx-auto flex items-center">
          <button onClick={() => router.back()} className="mr-4">
            <ArrowLeft className="w-6 h-6 text-[#2C3E50]" />
          </button>
          <h1 className="text-xl font-bold text-[#2C3E50]">About TasteBuds</h1>
        </div>
      </div>

      <div className="max-w-md mx-auto p-4 space-y-6">
        {/* Hero Section */}
        <div className="bg-gradient-to-br from-[#FF6B6B] to-[#FF8787] rounded-2xl p-8 text-white text-center">
          <div className="w-20 h-20 bg-white/20 backdrop-blur-sm rounded-full flex items-center justify-center mx-auto mb-4">
            <Heart className="w-10 h-10" />
          </div>
          <h2 className="text-2xl font-bold mb-2">Find People Who Like Similar Food</h2>
          <p className="text-white/90">
            TasteBuds Yelp Companion helps you discover people who share your taste preferences and explore Yelp restaurants together
          </p>
        </div>

        {/* Mission */}
        <div className="bg-white rounded-xl p-6 shadow-sm">
          <div className="flex items-center gap-3 mb-4">
            <Target className="w-6 h-6 text-[#FF6B6B]" />
            <h3 className="text-lg font-bold text-[#2C3E50]">Our Mission</h3>
          </div>
          <p className="text-[#6C757D]">
            We believe that food brings people together. TasteBuds Yelp Companion uses advanced matching algorithms to connect you
            with people who have similar food preferences, helping you discover restaurants through the lens of your Taste Twins.
          </p>
        </div>

        {/* Features */}
        <div>
          <h3 className="text-sm font-semibold text-[#6C757D] uppercase mb-3 px-2">Key Features</h3>
          <div className="grid grid-cols-1 gap-3">
            {features.map(({ icon: Icon, title, description, color }) => (
              <div key={title} className="bg-white rounded-xl p-4 shadow-sm">
                <div className="flex gap-4">
                  <div
                    className="w-12 h-12 rounded-full flex items-center justify-center flex-shrink-0"
                    style={{ backgroundColor: `${color}15` }}
                  >
                    <Icon className="w-6 h-6" style={{ color }} />
                  </div>
                  <div className="flex-1">
                    <h4 className="font-semibold text-[#2C3E50] mb-1">{title}</h4>
                    <p className="text-sm text-[#6C757D]">{description}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Stats */}
        <div className="bg-white rounded-xl p-6 shadow-sm">
          <div className="flex items-center gap-3 mb-4">
            <Globe className="w-6 h-6 text-[#4ECDC4]" />
            <h3 className="text-lg font-bold text-[#2C3E50]">Powered by Yelp</h3>
          </div>
          <p className="text-sm text-[#6C757D] mb-4">
            All restaurant data is sourced directly from Yelp's extensive database, ensuring you get accurate,
            up-to-date information about millions of restaurants.
          </p>
          <div className="grid grid-cols-3 gap-4 pt-4 border-t border-[#E9ECEF]">
            <div className="text-center">
              <p className="text-2xl font-bold text-[#FF6B6B]">Real-time</p>
              <p className="text-xs text-[#6C757D] mt-1">Data Updates</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-[#51CF66]">100%</p>
              <p className="text-xs text-[#6C757D] mt-1">Accurate</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-[#4ECDC4]">Millions</p>
              <p className="text-xs text-[#6C757D] mt-1">Restaurants</p>
            </div>
          </div>
        </div>

        {/* Version Info */}
        <div className="text-center py-4">
          <p className="text-sm text-[#ADB5BD] mb-1">Version 1.0.0</p>
          <p className="text-xs text-[#CED4DA]">Made with ❤️ for food lovers</p>
        </div>
      </div>
    </div>
  )
}
