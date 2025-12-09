"use client"

import { useRouter } from "next/navigation"
import { ArrowLeft, Bell, Globe, Lock, User, Moon } from "lucide-react"
import { ProtectedRoute } from "@/components/protected-route"

function SettingsPageContent() {
  const router = useRouter()

  const settingsSections = [
    {
      title: "Account",
      items: [
        { icon: User, label: "Edit Profile", description: "Update your name and photo" },
        { icon: Lock, label: "Change Password", description: "Update your password" },
      ],
    },
    {
      title: "Preferences",
      items: [
        { icon: Bell, label: "Notifications", description: "Manage notification preferences" },
        { icon: Moon, label: "Dark Mode", description: "Coming soon" },
        { icon: Globe, label: "Language", description: "English (US)" },
      ],
    },
  ]

  return (
    <div className="min-h-screen bg-[#F8F9FA] pb-[60px] md:pb-0">
      {/* Header */}
      <div className="bg-white border-b border-[#E9ECEF] px-4 py-4 sticky top-0 z-10">
        <div className="max-w-md mx-auto flex items-center">
          <button onClick={() => router.back()} className="mr-4">
            <ArrowLeft className="w-6 h-6 text-[#2C3E50]" />
          </button>
          <h1 className="text-xl font-bold text-[#2C3E50]">Settings</h1>
        </div>
      </div>

      <div className="max-w-md mx-auto p-4 space-y-6">
        {settingsSections.map((section) => (
          <div key={section.title}>
            <h2 className="text-sm font-semibold text-[#6C757D] uppercase mb-3 px-2">
              {section.title}
            </h2>
            <div className="bg-white rounded-2xl shadow-sm overflow-hidden">
              {section.items.map(({ icon: Icon, label, description }, index) => (
                <button
                  key={label}
                  className={`w-full flex items-center gap-4 px-4 py-4 hover:bg-[#F8F9FA] transition-colors ${
                    index !== section.items.length - 1 ? "border-b border-[#E9ECEF]" : ""
                  }`}
                >
                  <div className="w-10 h-10 rounded-lg bg-[#FF6B6B]/10 flex items-center justify-center">
                    <Icon className="w-5 h-5 text-[#FF6B6B]" />
                  </div>
                  <div className="flex-1 text-left">
                    <p className="font-medium text-[#2C3E50]">{label}</p>
                    <p className="text-sm text-[#6C757D]">{description}</p>
                  </div>
                </button>
              ))}
            </div>
          </div>
        ))}

        {/* Coming Soon Notice */}
        <div className="bg-[#FFF3CD] border border-[#FFEAA7] rounded-xl p-4 text-center">
          <p className="text-sm text-[#856404]">
            Settings functionality coming soon! We're working on adding more customization options.
          </p>
        </div>
      </div>
    </div>
  )
}

export default function SettingsPage() {
  return (
    <ProtectedRoute>
      <SettingsPageContent />
    </ProtectedRoute>
  )
}
