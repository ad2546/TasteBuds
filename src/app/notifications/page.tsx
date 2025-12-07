"use client"

import { useRouter } from "next/navigation"
import { ArrowLeft, Bell, Heart, Users, Trophy, MapPin } from "lucide-react"
import { ProtectedRoute } from "@/components/protected-route"

function NotificationsPageContent() {
  const router = useRouter()

  const notifications = [
    {
      icon: Users,
      iconColor: "#FF6B6B",
      title: "New Taste Twin Found!",
      message: "You matched with Sarah K. - 94% taste similarity",
      time: "2 hours ago",
      unread: true,
    },
    {
      icon: Heart,
      iconColor: "#51CF66",
      title: "Restaurant Recommendation",
      message: "Based on your TasteDNA, we found 3 new restaurants you might love",
      time: "5 hours ago",
      unread: true,
    },
    {
      icon: Trophy,
      iconColor: "#FFA94D",
      title: "Achievement Unlocked!",
      message: 'You earned the "Adventurous Eater" badge',
      time: "1 day ago",
      unread: false,
    },
    {
      icon: MapPin,
      iconColor: "#4ECDC4",
      title: "New Restaurant Nearby",
      message: "A highly-rated Italian restaurant just opened near you",
      time: "2 days ago",
      unread: false,
    },
  ]

  return (
    <div className="min-h-screen bg-[#F8F9FA]">
      {/* Header */}
      <div className="bg-white border-b border-[#E9ECEF] px-4 py-4 sticky top-0 z-10">
        <div className="max-w-md mx-auto flex items-center justify-between">
          <div className="flex items-center">
            <button onClick={() => router.back()} className="mr-4">
              <ArrowLeft className="w-6 h-6 text-[#2C3E50]" />
            </button>
            <h1 className="text-xl font-bold text-[#2C3E50]">Notifications</h1>
          </div>
          <button className="text-sm text-[#FF6B6B] font-medium">Mark all read</button>
        </div>
      </div>

      <div className="max-w-md mx-auto p-4 space-y-3">
        {notifications.length > 0 ? (
          notifications.map((notification, index) => (
            <div
              key={index}
              className={`bg-white rounded-xl p-4 shadow-sm hover:shadow-md transition-shadow cursor-pointer ${
                notification.unread ? "border-l-4 border-[#FF6B6B]" : ""
              }`}
            >
              <div className="flex gap-3">
                <div
                  className="w-12 h-12 rounded-full flex items-center justify-center flex-shrink-0"
                  style={{ backgroundColor: `${notification.iconColor}15` }}
                >
                  <notification.icon className="w-6 h-6" style={{ color: notification.iconColor }} />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between gap-2">
                    <h3 className="font-semibold text-[#2C3E50]">{notification.title}</h3>
                    {notification.unread && (
                      <div className="w-2 h-2 rounded-full bg-[#FF6B6B] flex-shrink-0 mt-1.5" />
                    )}
                  </div>
                  <p className="text-sm text-[#6C757D] mt-1">{notification.message}</p>
                  <p className="text-xs text-[#ADB5BD] mt-2">{notification.time}</p>
                </div>
              </div>
            </div>
          ))
        ) : (
          <div className="text-center py-12">
            <Bell className="w-16 h-16 text-[#CED4DA] mx-auto mb-4" />
            <p className="text-[#6C757D] font-medium">No notifications yet</p>
            <p className="text-sm text-[#ADB5BD] mt-1">
              We'll notify you about new matches and recommendations
            </p>
          </div>
        )}
      </div>
    </div>
  )
}

export default function NotificationsPage() {
  return (
    <ProtectedRoute>
      <NotificationsPageContent />
    </ProtectedRoute>
  )
}
