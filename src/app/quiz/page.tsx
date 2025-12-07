"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { api, type QuizQuestion, type QuizAnswer } from "@/lib/api"
import { useAuth } from "@/lib/auth-context"
import { ChevronLeft, ChevronRight, Loader2, Sparkles } from "lucide-react"

export default function QuizPage() {
  const router = useRouter()
  const { refreshUser } = useAuth()
  const [questions, setQuestions] = useState<QuizQuestion[]>([])
  const [currentIndex, setCurrentIndex] = useState(0)
  const [answers, setAnswers] = useState<Record<string, any>>({})
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    loadQuiz()
  }, [])

  const loadQuiz = async () => {
    try {
      const data = await api.getQuiz()
      setQuestions(data.questions)
    } catch {
      // If quiz fails, redirect to home
      router.push("/home")
    } finally {
      setLoading(false)
    }
  }

  const currentQuestion = questions[currentIndex]
  const progress = ((currentIndex + 1) / questions.length) * 100

  const handleSliderChange = (value: number) => {
    setAnswers((prev) => ({ ...prev, [currentQuestion.id]: value }))
  }

  const handleMultipleChoice = (optionValue: string) => {
    const current = (answers[currentQuestion.id] as string[]) || []
    const updated = current.includes(optionValue) ? current.filter((o) => o !== optionValue) : [...current, optionValue]
    setAnswers((prev) => ({ ...prev, [currentQuestion.id]: updated }))
  }

  const handleSingleChoice = (optionValue: string) => {
    setAnswers((prev) => ({ ...prev, [currentQuestion.id]: optionValue }))
  }

  const handleSwipe = (direction: string) => {
    setAnswers((prev) => ({ ...prev, [currentQuestion.id]: direction }))
    // Auto-advance to next question after swipe
    setTimeout(() => {
      if (currentIndex < questions.length - 1) {
        setCurrentIndex((prev) => prev + 1)
      }
    }, 300)
  }

  const canProceed = () => {
    const answer = answers[currentQuestion?.id]
    if (!answer) return false
    if (currentQuestion.type === "multiple_choice" || currentQuestion.type === "multiselect") {
      const arr = answer as string[]
      return arr.length >= 1
    }
    if (currentQuestion.type === "swipe") {
      return typeof answer === "string" && (answer === "left" || answer === "right")
    }
    if (currentQuestion.type === "choice") {
      return typeof answer === "string" && answer.length > 0
    }
    return true
  }

  const handleNext = () => {
    if (currentIndex < questions.length - 1) {
      setCurrentIndex((prev) => prev + 1)
    }
  }

  const handlePrev = () => {
    if (currentIndex > 0) {
      setCurrentIndex((prev) => prev - 1)
    }
  }

  const handleSubmit = async () => {
    setSubmitting(true)
    try {
      const quizAnswers: QuizAnswer[] = Object.entries(answers).map(([id, answer]) => {
        const question = questions.find(q => q.id === id)
        if (!question) return null

        // Format answer based on question type
        if (question.type === "slider") {
          return {
            question_id: id,
            answer_type: "slider_value",
            value: answer as number,
          }
        } else if (question.type === "swipe") {
          return {
            question_id: id,
            answer_type: answer === "right" ? "swipe_right" : "swipe_left",
            choice: answer as string,
          }
        } else if (question.type === "choice") {
          return {
            question_id: id,
            answer_type: "choice",
            choice: answer as string,
          }
        } else if (question.type === "multiselect" || question.type === "multiple_choice") {
          return {
            question_id: id,
            answer_type: "choice",
            choice: (answer as string[]).join(","),
          }
        }
        return null
      }).filter(a => a !== null) as QuizAnswer[]

      await api.submitQuiz(quizAnswers)
      await refreshUser()
      router.push("/home")
    } catch (error) {
      console.error("Failed to submit quiz:", error)
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <Loader2 className="w-8 h-8 text-[#FF6B6B] animate-spin" />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-white p-4">
      <div className="max-w-md mx-auto pt-8">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-2 bg-[#FF6B6B]/10 text-[#FF6B6B] px-4 py-2 rounded-full text-sm font-medium mb-4">
            <Sparkles className="w-4 h-4" />
            Building Your Taste DNA
          </div>
          <h1 className="text-2xl font-bold text-[#2C3E50]">Tell us about your taste</h1>
        </div>

        {/* Progress Bar */}
        <div className="mb-8">
          <div className="flex justify-between text-sm text-[#6C757D] mb-2">
            <span>
              Question {currentIndex + 1} of {questions.length}
            </span>
            <span>{Math.round(progress)}%</span>
          </div>
          <div className="h-2 bg-[#E9ECEF] rounded-full overflow-hidden">
            <div
              className="h-full bg-[#FF6B6B] transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        {/* Question Card */}
        <div className="bg-white rounded-2xl shadow-lg p-6 mb-6">
          <h2 className="text-lg font-semibold text-[#2C3E50] mb-6">{currentQuestion?.question}</h2>

          {currentQuestion?.type === "slider" && (
            <div className="space-y-4">
              <input
                type="range"
                min={currentQuestion.min_value || currentQuestion.min || 0}
                max={currentQuestion.max_value || currentQuestion.max || 1}
                step="0.01"
                value={(answers[currentQuestion.id] as number) ?? (currentQuestion.min_value || currentQuestion.min || 0) + ((currentQuestion.max_value || currentQuestion.max || 1) - (currentQuestion.min_value || currentQuestion.min || 0)) / 2}
                onChange={(e) => handleSliderChange(Number.parseFloat(e.target.value))}
                className="w-full h-2 bg-[#E9ECEF] rounded-full appearance-none cursor-pointer accent-[#FF6B6B]"
              />
              <div className="flex justify-between text-sm text-[#6C757D]">
                {currentQuestion.labels ? (
                  currentQuestion.labels.map((label, i) => <span key={i}>{label}</span>)
                ) : (
                  <>
                    <span>{(currentQuestion as any).min_label || "Min"}</span>
                    <span>{(currentQuestion as any).max_label || "Max"}</span>
                  </>
                )}
              </div>
              <div className="text-center">
                <span className="text-3xl font-bold text-[#FF6B6B]">
                  {Math.round(((answers[currentQuestion.id] as number) ?? 0.5) * 100)}%
                </span>
              </div>
            </div>
          )}

          {(currentQuestion?.type === "multiple_choice" || currentQuestion?.type === "multiselect") && (
            <div className="space-y-3">
              <p className="text-sm text-[#6C757D] mb-4">Select one or more options</p>
              <div className="grid grid-cols-2 gap-3">
                {currentQuestion.options?.map((opt) => {
                  const option = typeof opt === "string" ? opt : opt.value
                  const label = typeof opt === "string" ? opt : opt.label
                  const selected = ((answers[currentQuestion.id] as string[]) || []).includes(option)
                  return (
                    <button
                      key={option}
                      onClick={() => handleMultipleChoice(option)}
                      className={`px-4 py-3 rounded-xl font-medium transition-all ${
                        selected ? "bg-[#FF6B6B] text-white" : "bg-[#F8F9FA] text-[#2C3E50] hover:bg-[#E9ECEF]"
                      }`}
                    >
                      {label}
                    </button>
                  )
                })}
              </div>
            </div>
          )}

          {currentQuestion?.type === "choice" && (
            <div className="space-y-3">
              <div className="grid grid-cols-1 gap-3">
                {currentQuestion.options?.map((opt) => {
                  const option = typeof opt === "string" ? opt : opt.value
                  const label = typeof opt === "string" ? opt : opt.label
                  const selected = answers[currentQuestion.id] === option
                  return (
                    <button
                      key={option}
                      onClick={() => handleSingleChoice(option)}
                      className={`px-4 py-3 rounded-xl font-medium transition-all ${
                        selected ? "bg-[#FF6B6B] text-white" : "bg-[#F8F9FA] text-[#2C3E50] hover:bg-[#E9ECEF]"
                      }`}
                    >
                      {label}
                    </button>
                  )
                })}
              </div>
            </div>
          )}

          {currentQuestion?.type === "swipe" && (
            <div className="space-y-6">
              {/* Restaurant Image */}
              <div className="relative rounded-xl overflow-hidden aspect-[4/3] bg-[#FF6B6B]/10 flex items-center justify-center">
                {currentQuestion.image_url && !currentQuestion.image_url.includes("example.com") ? (
                  <img
                    src={currentQuestion.image_url}
                    alt="Restaurant"
                    className="w-full h-full object-cover"
                    onError={(e) => {
                      e.currentTarget.style.display = "none"
                    }}
                  />
                ) : (
                  <div className="text-center p-8">
                    <div className="text-6xl mb-4">🍽️</div>
                    <p className="text-[#6C757D] font-medium">Restaurant {currentIndex + 1}</p>
                  </div>
                )}
              </div>

              {/* Swipe Buttons */}
              <div className="grid grid-cols-2 gap-4">
                <button
                  onClick={() => handleSwipe("left")}
                  className={`h-16 rounded-xl font-semibold text-lg transition-all flex items-center justify-center gap-2 ${
                    answers[currentQuestion.id] === "left"
                      ? "bg-[#FF6B6B] text-white scale-105"
                      : "bg-[#F8F9FA] text-[#6C757D] hover:bg-[#E9ECEF]"
                  }`}
                >
                  <span className="text-2xl">👎</span>
                  Pass
                </button>
                <button
                  onClick={() => handleSwipe("right")}
                  className={`h-16 rounded-xl font-semibold text-lg transition-all flex items-center justify-center gap-2 ${
                    answers[currentQuestion.id] === "right"
                      ? "bg-[#51CF66] text-white scale-105"
                      : "bg-[#F8F9FA] text-[#6C757D] hover:bg-[#E9ECEF]"
                  }`}
                >
                  <span className="text-2xl">👍</span>
                  Yes!
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Navigation */}
        <div className="flex gap-3">
          {currentIndex > 0 && (
            <button
              onClick={handlePrev}
              className="flex-1 h-12 rounded-xl border-2 border-[#DEE2E6] text-[#6C757D] font-medium hover:bg-[#F8F9FA] transition-colors flex items-center justify-center gap-2"
            >
              <ChevronLeft className="w-5 h-5" />
              Back
            </button>
          )}

          {currentIndex < questions.length - 1 ? (
            <button
              onClick={handleNext}
              disabled={!canProceed()}
              className="flex-1 h-12 rounded-xl bg-[#FF6B6B] text-white font-semibold hover:bg-[#FF5252] disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2"
            >
              Next
              <ChevronRight className="w-5 h-5" />
            </button>
          ) : (
            <button
              onClick={handleSubmit}
              disabled={!canProceed() || submitting}
              className="flex-1 h-12 rounded-xl bg-[#FF6B6B] text-white font-semibold hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2"
            >
              {submitting ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <>
                  <Sparkles className="w-5 h-5" />
                  Complete
                </>
              )}
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
