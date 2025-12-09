"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/lib/auth-context"
import { Utensils, Mail, Lock, User, Sparkles, ArrowRight } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card } from "@/components/ui/card"

export default function LoginPage() {
  const router = useRouter()
  const { login, register } = useAuth()
  const [mode, setMode] = useState<"login" | "register">("login")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [name, setName] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")
  const [focusedField, setFocusedField] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError("")

    try {
      if (mode === "login") {
        await login(email, password)
      } else {
        await register(email, name, password)
      }

      // Check if quiz is completed
      const user = JSON.parse(localStorage.getItem("user") || "{}")
      if (user.quiz_completed) {
        router.push("/home")
      } else {
        router.push("/quiz")
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-[#FF6B6B] flex items-center justify-center p-4">
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 left-10 w-72 h-72 bg-white/10 rounded-full blur-3xl animate-pulse" />
        <div className="absolute bottom-20 right-10 w-96 h-96 bg-white/10 rounded-full blur-3xl animate-pulse delay-1000" />
      </div>

      <div className="w-full max-w-md relative z-10">
        {/* Logo and Brand */}
        <div className="text-center mb-8 animate-[slideUp_0.5s_ease-out]">
          <div className="relative inline-block mb-6">
            <div className="absolute inset-0 bg-white/20 rounded-3xl blur-xl" />
            <div className="relative w-24 h-24 bg-white rounded-3xl mx-auto flex items-center justify-center shadow-2xl">
              <Utensils className="w-12 h-12 text-[#FF6B6B]" aria-hidden="true" />
            </div>
          </div>

          <h1 className="text-4xl font-extrabold text-white mb-3 tracking-tight">
            TasteBuds
          </h1>
          <p className="text-white/90 text-lg font-medium">
            Find your food friends
          </p>
        </div>

        {/* Main Form Card */}
        <Card
          variant="elevated"
          padding="lg"
          className="backdrop-blur-sm bg-white/95 animate-[scaleIn_0.5s_ease-out_0.2s_both]"
        >
          {/* Mode Toggle */}
          <div className="flex gap-2 p-1 bg-gray-100 rounded-xl mb-6">
            <button
              type="button"
              onClick={() => {setMode("login"); setError("")}}
              className={`
                flex-1 py-3 px-4 rounded-lg font-semibold transition-all duration-200
                ${mode === "login"
                  ? "bg-white text-[#FF6B6B] shadow-md"
                  : "text-gray-600 hover:text-gray-900"
                }
              `}
              aria-pressed={mode === "login"}
            >
              Log In
            </button>
            <button
              type="button"
              onClick={() => {setMode("register"); setError("")}}
              className={`
                flex-1 py-3 px-4 rounded-lg font-semibold transition-all duration-200
                ${mode === "register"
                  ? "bg-white text-[#FF6B6B] shadow-md"
                  : "text-gray-600 hover:text-gray-900"
                }
              `}
              aria-pressed={mode === "register"}
            >
              Sign Up
            </button>
          </div>

          {/* Welcome Message */}
          <div className="mb-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-1">
              {mode === "login" ? "Welcome back!" : "Join TasteSync"}
            </h2>
            <p className="text-gray-600">
              {mode === "login"
                ? "Continue your culinary journey"
                : "Start discovering restaurants tailored to your taste"
              }
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            {mode === "register" && (
              <Input
                type="text"
                placeholder="Full Name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                leftIcon={<User className="w-5 h-5" />}
                required={mode === "register"}
                inputSize="lg"
                onFocus={() => setFocusedField("name")}
                onBlur={() => setFocusedField(null)}
                aria-label="Full name"
              />
            )}

            <Input
              type="email"
              placeholder="Email address"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              leftIcon={<Mail className="w-5 h-5" />}
              required
              inputSize="lg"
              onFocus={() => setFocusedField("email")}
              onBlur={() => setFocusedField(null)}
              aria-label="Email address"
            />

            <Input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              leftIcon={<Lock className="w-5 h-5" />}
              required
              inputSize="lg"
              error={error}
              helperText={mode === "register" ? "At least 6 characters" : undefined}
              onFocus={() => setFocusedField("password")}
              onBlur={() => setFocusedField(null)}
              aria-label="Password"
            />

            <Button
              type="submit"
              variant="gradient"
              size="lg"
              fullWidth
              loading={loading}
              rightIcon={<ArrowRight className="w-5 h-5" />}
              className="mt-6"
            >
              {mode === "login" ? "Log In" : "Create Account"}
            </Button>
          </form>

          {mode === "login" && (
            <div className="mt-4 text-center">
              <button
                type="button"
                className="text-sm text-gray-600 hover:text-[#FF6B6B] transition-colors"
                onClick={() => {/* Implement forgot password */}}
              >
                Forgot password?
              </button>
            </div>
          )}
        </Card>

        {/* Privacy Note */}
        <p className="mt-6 text-center text-white/60 text-xs">
          By continuing, you agree to our{" "}
          <button className="underline hover:text-white/80">Terms</button> and{" "}
          <button className="underline hover:text-white/80">Privacy Policy</button>
        </p>
      </div>
    </div>
  )
}
