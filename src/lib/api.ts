// Use environment variable or default to localhost
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"

class API {
  private getHeaders(): HeadersInit {
    const token = typeof window !== "undefined" ? localStorage.getItem("token") : null
    return {
      "Content-Type": "application/json",
      ...(token && { Authorization: `Bearer ${token}` }),
    }
  }

  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      let errorMessage = `HTTP ${response.status}: ${response.statusText}`

      try {
        const error = await response.json()
        if (error.detail) {
          errorMessage = typeof error.detail === 'string'
            ? error.detail
            : JSON.stringify(error.detail)
        } else if (error.message) {
          errorMessage = error.message
        }
      } catch (e) {
        // Failed to parse JSON error, use status text
        errorMessage = `${response.status} ${response.statusText || 'Error'}`
      }

      console.error('API Error:', {
        status: response.status,
        url: response.url,
        error: errorMessage
      })

      // Include status code in error message for better handling
      throw new Error(`${response.status === 404 ? '404: ' : ''}${errorMessage}`)
    }
    return response.json()
  }

  // Auth
  async login(email: string, password: string) {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    })
    return this.handleResponse<AuthResponse>(response)
  }

  async register(email: string, name: string, password: string) {
    const response = await fetch(`${API_BASE_URL}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, name, password }),
    })
    return this.handleResponse<AuthResponse>(response)
  }

  async getCurrentUser() {
    const response = await fetch(`${API_BASE_URL}/auth/me`, {
      headers: this.getHeaders(),
    })
    return this.handleResponse<User>(response)
  }

  // Taste DNA
  async getQuiz() {
    const response = await fetch(`${API_BASE_URL}/taste-dna/quiz`, {
      headers: this.getHeaders(),
    })
    return this.handleResponse<QuizResponse>(response)
  }

  async submitQuiz(answers: QuizAnswer[]) {
    const response = await fetch(`${API_BASE_URL}/taste-dna/quiz/submit`, {
      method: "POST",
      headers: this.getHeaders(),
      body: JSON.stringify({ answers }),
    })
    return this.handleResponse<QuizSubmitResponse>(response)
  }

  async getTasteDNA() {
    const response = await fetch(`${API_BASE_URL}/taste-dna/profile`, {
      headers: this.getHeaders(),
    })
    return this.handleResponse<TasteDNA>(response)
  }

  async getTasteDNACard() {
    const response = await fetch(`${API_BASE_URL}/taste-dna/card`, {
      headers: this.getHeaders(),
    })
    return this.handleResponse<TasteDNACard>(response)
  }

  // Twins
  async getTwins() {
    const response = await fetch(`${API_BASE_URL}/twins`, {
      headers: this.getHeaders(),
    })
    return this.handleResponse<TwinsResponse>(response)
  }

  async getTwinsCount() {
    const response = await fetch(`${API_BASE_URL}/twins/count`, {
      headers: this.getHeaders(),
    })
    return this.handleResponse<{ count: number }>(response)
  }

  // Discovery
  async getFeelingLucky(location: string) {
    const response = await fetch(`${API_BASE_URL}/discovery/lucky?location=${encodeURIComponent(location)}`, {
      headers: this.getHeaders(),
    })
    return this.handleResponse<FeelingLuckyResponse>(response)
  }

  async getCompare(location: string, limit = 3) {
    const response = await fetch(
      `${API_BASE_URL}/discovery/compare?location=${encodeURIComponent(location)}&limit=${limit}`,
      { headers: this.getHeaders() },
    )
    return this.handleResponse<CompareResponse>(response)
  }

  async getTrending(location: string) {
    const response = await fetch(`${API_BASE_URL}/discovery/trending?location=${encodeURIComponent(location)}`, {
      headers: this.getHeaders(),
    })
    return this.handleResponse<TrendingResponse>(response)
  }

  // Restaurants
  async searchRestaurants(params: SearchParams) {
    const searchParams = new URLSearchParams()
    searchParams.append("location", params.location)
    if (params.term) searchParams.append("term", params.term)
    if (params.limit) searchParams.append("limit", params.limit.toString())
    if (params.offset) searchParams.append("offset", params.offset.toString())
    if (params.price) searchParams.append("price", params.price)
    if (params.categories) searchParams.append("categories", params.categories)
    if (params.open_now) searchParams.append("open_now", "true")

    const response = await fetch(`${API_BASE_URL}/restaurants/search?${searchParams}`, { headers: this.getHeaders() })
    return this.handleResponse<SearchResponse>(response)
  }

  async getRestaurant(restaurantId: string) {
    const url = `${API_BASE_URL}/restaurants/${restaurantId}`
    console.log('Fetching restaurant from:', url, 'ID:', restaurantId)
    const response = await fetch(url, { headers: this.getHeaders() })
    console.log('Restaurant response status:', response.status)
    return this.handleResponse<RestaurantDetail>(response)
  }

  async getRestaurantReviews(restaurantId: string) {
    const response = await fetch(`${API_BASE_URL}/restaurants/${restaurantId}/reviews`, { headers: this.getHeaders() })
    return this.handleResponse<ReviewsResponse>(response)
  }

  async saveRestaurant(restaurantId: string, notes?: string) {
    const response = await fetch(`${API_BASE_URL}/restaurants/${restaurantId}/save`, {
      method: "POST",
      headers: this.getHeaders(),
      body: JSON.stringify({ notes }),
    })
    return this.handleResponse<{ message: string; saved_at: string }>(response)
  }

  async getSavedRestaurants() {
    const response = await fetch(`${API_BASE_URL}/restaurants/saved/list`, {
      headers: this.getHeaders(),
    })
    return this.handleResponse<SavedRestaurant[]>(response)
  }

  async logInteraction(restaurantId: string, data: { action_type: string; context?: string }) {
    const response = await fetch(`${API_BASE_URL}/restaurants/${restaurantId}/log`, {
      method: "POST",
      headers: this.getHeaders(),
      body: JSON.stringify(data),
    })
    return this.handleResponse<{ message: string }>(response)
  }

  // Date Night
  async getCompatibility(partnerId: string) {
    const response = await fetch(`${API_BASE_URL}/date-night/compatibility?partner_id=${partnerId}`, {
      headers: this.getHeaders(),
    })
    return this.handleResponse<CompatibilityResponse>(response)
  }

  async getDateNightSuggestions(partnerId: string, location: string) {
    const response = await fetch(
      `${API_BASE_URL}/date-night/suggestions?partner_id=${partnerId}&location=${encodeURIComponent(location)}`,
      { headers: this.getHeaders() },
    )
    return this.handleResponse<DateNightSuggestions>(response)
  }

  // Gamification
  async getChallenges() {
    const response = await fetch(`${API_BASE_URL}/gamification/challenges`, {
      headers: this.getHeaders(),
    })
    return this.handleResponse<ChallengesResponse>(response)
  }

  async joinChallenge(challengeId: string) {
    const response = await fetch(`${API_BASE_URL}/gamification/challenges/${challengeId}/join`, {
      method: "POST",
      headers: this.getHeaders(),
    })
    return this.handleResponse<{ message: string; progress: number }>(response)
  }

  async getLeaderboard(boardType: "adventure" | "discovery" | "social" = "adventure") {
    const response = await fetch(`${API_BASE_URL}/gamification/leaderboard?board_type=${boardType}`, {
      headers: this.getHeaders(),
    })
    return this.handleResponse<LeaderboardResponse>(response)
  }

  async getAchievements() {
    const response = await fetch(`${API_BASE_URL}/gamification/achievements`, {
      headers: this.getHeaders(),
    })
    return this.handleResponse<AchievementsResponse>(response)
  }

  // AI Chat
  async aiChat(query: string, chatId?: string, latitude?: number, longitude?: number, useTasteDNA: boolean = true) {
    const response = await fetch(`${API_BASE_URL}/ai-chat/chat`, {
      method: "POST",
      headers: this.getHeaders(),
      body: JSON.stringify({
        query,
        chat_id: chatId,
        latitude,
        longitude,
        use_taste_dna: useTasteDNA,
      }),
    })
    return this.handleResponse<AIChatResponse>(response)
  }

  async aiSmartSearch(query: string, latitude?: number, longitude?: number) {
    const params = new URLSearchParams({ query })
    if (latitude) params.append("latitude", latitude.toString())
    if (longitude) params.append("longitude", longitude.toString())

    const response = await fetch(`${API_BASE_URL}/ai-chat/smart-search?${params}`, {
      headers: this.getHeaders(),
    })
    return this.handleResponse<AIChatResponse>(response)
  }

  async aiCompareRestaurants(restaurantIds: string[], criteria: string = "overall experience", latitude?: number, longitude?: number) {
    const response = await fetch(`${API_BASE_URL}/ai-chat/compare`, {
      method: "POST",
      headers: this.getHeaders(),
      body: JSON.stringify({
        restaurant_ids: restaurantIds,
        criteria,
        latitude,
        longitude,
      }),
    })
    return this.handleResponse<AIChatResponse>(response)
  }

  async aiRecommend(occasion: string, partySize?: number, dateTime?: string, latitude?: number, longitude?: number) {
    const response = await fetch(`${API_BASE_URL}/ai-chat/recommend`, {
      method: "POST",
      headers: this.getHeaders(),
      body: JSON.stringify({
        occasion,
        party_size: partySize,
        date_time: dateTime,
        latitude,
        longitude,
      }),
    })
    return this.handleResponse<AIChatResponse>(response)
  }

  async aiAskAboutRestaurant(restaurantId: string, question: string, latitude?: number, longitude?: number) {
    const response = await fetch(`${API_BASE_URL}/ai-chat/ask`, {
      method: "POST",
      headers: this.getHeaders(),
      body: JSON.stringify({
        restaurant_id: restaurantId,
        question,
        latitude,
        longitude,
      }),
    })
    return this.handleResponse<AIChatResponse>(response)
  }
}

export const api = new API()

// Types
export interface User {
  id: string
  email: string
  name: string
  quiz_completed: boolean
  avatar_url: string | null
  created_at: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
  user: User
}

export interface QuizQuestion {
  id: string
  type: "slider" | "multiple_choice" | "swipe" | "choice" | "multiselect"
  question: string
  min?: number
  max?: number
  min_value?: number
  max_value?: number
  min_label?: string
  max_label?: string
  labels?: string[]
  options?: Array<{ value: string; label: string }> | string[]
  image_url?: string
}

export interface QuizResponse {
  questions: QuizQuestion[]
}

export interface QuizAnswer {
  question_id: string
  answer_type?: string
  value?: number
  choice?: string
}

export interface QuizSubmitResponse {
  message: string
  taste_dna: TasteDNA
}

export interface TasteDNA {
  user_id?: string
  adventure_score: number
  spice_tolerance: number
  ambiance_preference?: string
  price_sensitivity: number
  cuisine_diversity?: number
  preferred_cuisines: string[]
  dietary_restrictions?: string[]
  created_at?: string
  updated_at?: string
}

export interface TasteDNACard {
  user_name: string
  adventure_score: number
  spice_tolerance: number
  top_cuisines: string[]
  card_image_url: string
  share_text: string
}

export interface TasteTwin {
  twin_id: string
  name: string
  email: string
  avatar_url: string
  similarity_score: number
  shared_cuisines: string[]
  adventure_score: number
  spice_tolerance: number
}

export interface TwinsResponse {
  twins: TasteTwin[]
  total_count: number
}

export interface Restaurant {
  id: string
  restaurant_id?: string
  name: string
  image_url: string
  rating: number
  review_count?: number
  price: string
  category?: string
  categories?: { alias: string; title: string }[]
  location: {
    address?: string
    address1?: string
    city: string
    state: string
    zip_code: string
    display_address?: string[]
  }
  distance: number
  match_score: number
  why_match?: string
  url?: string
}

export interface FeelingLuckyResponse extends Restaurant {
  explanation: string
  twin_recommendations: {
    twin_name: string
    similarity: number
    comment: string
  }[]
}

export interface CompareResponse {
  restaurants: Restaurant[]
}

export interface TrendingResponse {
  trending: (Restaurant & { twin_visits: number; trending_score: number })[]
}

export interface SearchParams {
  location: string
  term?: string
  limit?: number
  offset?: number
  price?: string
  categories?: string
  open_now?: boolean
}

export interface SearchResponse {
  businesses: Restaurant[]
  total: number
}

export interface RestaurantDetail extends Restaurant {
  photos: string[]
  phone: string
  hours: { day: number; start: string; end: string; is_overnight: boolean }[]
  is_closed: boolean
  url: string
}

export interface Review {
  id: string
  rating: number
  text: string
  time_created: string
  user: {
    name: string
    image_url: string
  }
}

export interface ReviewsResponse {
  reviews: Review[]
  total: number
}

export interface SavedRestaurant {
  restaurant_id: string
  restaurant_name: string
  yelp_id: string
  notes: string
  saved_at: string
  restaurant_data: {
    name: string
    image_url: string
    rating: number
    price: string
  }
}

export interface CompatibilityResponse {
  compatibility_score: number
  shared_cuisines: string[]
  compromise_cuisines: string[]
  you_prefer: string[]
  they_prefer: string[]
  analysis: string
}

export interface DateNightSuggestions {
  perfect_matches: Restaurant[]
  you_will_love: Restaurant[]
  they_will_love: Restaurant[]
}

export interface Challenge {
  id: string
  title: string
  description: string
  target_count: number
  user_progress: number
  reward_xp: number
  active: boolean
  start_date: string
  end_date: string
}

export interface ChallengesResponse {
  challenges: Challenge[]
}

export interface LeaderboardEntry {
  rank: number
  user_id: string
  name: string
  score: number
  avatar_url: string
}

export interface LeaderboardResponse {
  leaderboard: LeaderboardEntry[]
  your_rank: number
  your_score: number
}

export interface Achievement {
  id: string
  title: string
  description: string
  icon_url: string
  earned_at: string
}

export interface AchievementsResponse {
  achievements: Achievement[]
}

export interface AIChatResponse {
  chat_id?: string
  text?: string
  businesses?: any[]
  entities?: any[]
  types?: string[]
  tags?: string[]
}
