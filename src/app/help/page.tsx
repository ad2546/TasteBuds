"use client"

import { useRouter } from "next/navigation"
import { ArrowLeft, HelpCircle, MessageCircle, BookOpen, Mail, ChevronRight } from "lucide-react"
import { ProtectedRoute } from "@/components/protected-route"

function HelpPageContent() {
  const router = useRouter()

  const faqItems = [
    {
      question: "How does TasteDNA work?",
      answer: "TasteDNA analyzes your food preferences to create a unique taste profile and match you with similar users.",
    },
    {
      question: "What are Taste Twins?",
      answer: "Taste Twins are users who share similar food preferences with you, helping you discover new restaurants.",
    },
    {
      question: "How do I save restaurants?",
      answer: "Simply tap the heart icon on any restaurant card to add it to your saved list.",
    },
    {
      question: "Can I change my preferences?",
      answer: "Yes! Retake the quiz anytime from your Taste DNA page to update your preferences.",
    },
  ]

  const supportOptions = [
    {
      icon: MessageCircle,
      title: "Chat Support",
      description: "Get help from our support team",
      color: "#4ECDC4",
    },
    {
      icon: Mail,
      title: "Email Us",
      description: "support@tastebuds.com",
      color: "#FF6B6B",
    },
    {
      icon: BookOpen,
      title: "Documentation",
      description: "Learn more about features",
      color: "#FFA94D",
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
          <h1 className="text-xl font-bold text-[#2C3E50]">Help & Support</h1>
        </div>
      </div>

      <div className="max-w-md mx-auto p-4 space-y-6">
        {/* Support Options */}
        <div>
          <h2 className="text-sm font-semibold text-[#6C757D] uppercase mb-3 px-2">Contact Us</h2>
          <div className="bg-white rounded-2xl shadow-sm overflow-hidden">
            {supportOptions.map(({ icon: Icon, title, description, color }, index) => (
              <button
                key={title}
                className={`w-full flex items-center gap-4 px-4 py-4 hover:bg-[#F8F9FA] transition-colors ${
                  index !== supportOptions.length - 1 ? "border-b border-[#E9ECEF]" : ""
                }`}
              >
                <div
                  className="w-12 h-12 rounded-full flex items-center justify-center"
                  style={{ backgroundColor: `${color}15` }}
                >
                  <Icon className="w-6 h-6" style={{ color }} />
                </div>
                <div className="flex-1 text-left">
                  <p className="font-medium text-[#2C3E50]">{title}</p>
                  <p className="text-sm text-[#6C757D]">{description}</p>
                </div>
                <ChevronRight className="w-5 h-5 text-[#CED4DA]" />
              </button>
            ))}
          </div>
        </div>

        {/* FAQ Section */}
        <div>
          <h2 className="text-sm font-semibold text-[#6C757D] uppercase mb-3 px-2">
            Frequently Asked Questions
          </h2>
          <div className="space-y-3">
            {faqItems.map((item, index) => (
              <div key={index} className="bg-white rounded-xl p-4 shadow-sm">
                <div className="flex items-start gap-3">
                  <HelpCircle className="w-5 h-5 text-[#FF6B6B] flex-shrink-0 mt-0.5" />
                  <div>
                    <h3 className="font-semibold text-[#2C3E50] mb-2">{item.question}</h3>
                    <p className="text-sm text-[#6C757D]">{item.answer}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* App Info */}
        <div className="bg-white rounded-xl p-4 shadow-sm text-center">
          <p className="text-sm text-[#6C757D] mb-1">TasteBuds App</p>
          <p className="text-xs text-[#ADB5BD]">Version 1.0.0</p>
        </div>
      </div>
    </div>
  )
}

export default function HelpPage() {
  return (
    <ProtectedRoute>
      <HelpPageContent />
    </ProtectedRoute>
  )
}
