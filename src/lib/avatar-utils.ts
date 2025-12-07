// Food-themed emojis for profile pictures
const AVATAR_EMOJIS = [
  "🍕", "🍔", "🍟", "🌭", "🍿", "🧂", "🥓", "🥚", "🍳", "🧇",
  "🥞", "🧈", "🍞", "🥐", "🥨", "🥯", "🥖", "🧀", "🥗", "🥙",
  "🥪", "🌮", "🌯", "🥫", "🍝", "🍜", "🍲", "🍛", "🍣", "🍱",
  "🥟", "🍤", "🍙", "🍚", "🍘", "🍥", "🥠", "🥮", "🍢", "🍡",
  "🍧", "🍨", "🍦", "🥧", "🧁", "🍰", "🎂", "🍮", "🍭", "🍬",
  "🍫", "🍿", "🍩", "🍪", "🌰", "🥜", "🍯", "🥛", "🍼", "☕",
  "🍵", "🧃", "🥤", "🧋", "🍶", "🍺", "🍻", "🥂", "🍷", "🥃",
  "🍸", "🍹", "🧉", "🍾", "🍴", "🥄", "🔪", "🏺", "🥝", "🥥",
  "🥑", "🍆", "🥔", "🥕", "🌽", "🌶️", "🥒", "🥬", "🥦", "🧄",
  "🧅", "🍄", "🥨", "🥖", "🌭", "🥩", "🍗", "🍖"
]

/**
 * Generate a random emoji avatar URL from a user ID
 * Uses the user ID as a seed to ensure consistency
 */
export function getEmojiAvatar(userId?: string): string {
  // Use user ID to generate consistent emoji for same user
  const seed = userId ? hashCode(userId) : Math.floor(Math.random() * AVATAR_EMOJIS.length)
  const index = Math.abs(seed) % AVATAR_EMOJIS.length
  const emoji = AVATAR_EMOJIS[index]

  // Return SVG data URL with emoji
  return `data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='100' height='100'><text x='50%' y='50%' font-size='60' text-anchor='middle' dominant-baseline='central'>${emoji}</text></svg>`
}

/**
 * Simple hash function to convert string to number
 */
function hashCode(str: string): number {
  let hash = 0
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i)
    hash = ((hash << 5) - hash) + char
    hash = hash & hash // Convert to 32-bit integer
  }
  return hash
}

/**
 * Get avatar URL with emoji fallback
 */
export function getAvatarUrl(avatarUrl: string | null | undefined, userId?: string): string {
  return avatarUrl || getEmojiAvatar(userId)
}
