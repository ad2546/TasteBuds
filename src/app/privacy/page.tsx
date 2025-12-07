"use client"

import { useRouter } from "next/navigation"
import { ArrowLeft, Shield, Lock, Eye, Database, UserX } from "lucide-react"
import { ProtectedRoute } from "@/components/protected-route"

function PrivacyPageContent() {
  const router = useRouter()

  const privacyTopics = [
    {
      icon: Shield,
      title: "Data Protection",
      description: "We use industry-standard encryption to protect your personal information and preferences.",
    },
    {
      icon: Lock,
      title: "Secure Authentication",
      description: "Your account is protected with secure password hashing and JWT token authentication.",
    },
    {
      icon: Eye,
      title: "Privacy Control",
      description: "You control what information is shared with your Taste Twins and other users.",
    },
    {
      icon: Database,
      title: "Data Storage",
      description: "Your data is stored securely and is never sold to third parties.",
    },
    {
      icon: UserX,
      title: "Account Deletion",
      description: "You can delete your account and all associated data at any time from settings.",
    },
  ]

  return (
    <div className="min-h-screen bg-[#F8F9FA] pb-20">
      {/* Header */}
      <div className="bg-white border-b border-[#E9ECEF] px-4 py-4 sticky top-0 z-10">
        <div className="max-w-md mx-auto flex items-center">
          <button onClick={() => router.back()} className="mr-4">
            <ArrowLeft className="w-6 h-6 text-[#2C3E50]" />
          </button>
          <h1 className="text-xl font-bold text-[#2C3E50]">Privacy & Security</h1>
        </div>
      </div>

      <div className="max-w-md mx-auto p-4 space-y-6">
        {/* Privacy Notice */}
        <div className="bg-gradient-to-br from-[#FF6B6B] to-[#FF8787] rounded-2xl p-6 text-white">
          <Shield className="w-12 h-12 mb-4" />
          <h2 className="text-xl font-bold mb-2">Your Privacy Matters</h2>
          <p className="text-white/90 text-sm">
            We're committed to protecting your personal information and being transparent about how we use it.
          </p>
        </div>

        {/* Privacy Topics */}
        <div className="space-y-3">
          {privacyTopics.map(({ icon: Icon, title, description }) => (
            <div key={title} className="bg-white rounded-xl p-4 shadow-sm">
              <div className="flex gap-4">
                <div className="w-12 h-12 rounded-full bg-[#FF6B6B]/10 flex items-center justify-center flex-shrink-0">
                  <Icon className="w-6 h-6 text-[#FF6B6B]" />
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-[#2C3E50] mb-1">{title}</h3>
                  <p className="text-sm text-[#6C757D]">{description}</p>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Policy Links */}
        <div className="bg-white rounded-xl shadow-sm divide-y divide-[#E9ECEF]">
          <button className="w-full px-4 py-4 text-left hover:bg-[#F8F9FA] transition-colors">
            <p className="font-medium text-[#2C3E50]">Privacy Policy</p>
            <p className="text-sm text-[#6C757D] mt-1">Read our full privacy policy</p>
          </button>
          <button className="w-full px-4 py-4 text-left hover:bg-[#F8F9FA] transition-colors">
            <p className="font-medium text-[#2C3E50]">Terms of Service</p>
            <p className="text-sm text-[#6C757D] mt-1">View terms and conditions</p>
          </button>
          <button className="w-full px-4 py-4 text-left hover:bg-[#F8F9FA] transition-colors">
            <p className="font-medium text-[#2C3E50]">Cookie Policy</p>
            <p className="text-sm text-[#6C757D] mt-1">Learn about cookies we use</p>
          </button>
        </div>

        {/* Contact */}
        <div className="bg-[#E7F5FF] border border-[#339AF0]/20 rounded-xl p-4">
          <p className="text-sm text-[#1971C2]">
            <strong>Questions about privacy?</strong>
            <br />
            Contact us at privacy@tastebuds.com
          </p>
        </div>

        {/* Last Updated */}
        <div className="text-center">
          <p className="text-xs text-[#ADB5BD]">Last updated: December 2024</p>
        </div>
      </div>
    </div>
  )
}

export default function PrivacyPage() {
  return (
    <ProtectedRoute>
      <PrivacyPageContent />
    </ProtectedRoute>
  )
}
