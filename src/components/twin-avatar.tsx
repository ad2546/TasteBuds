"use client"

import type { TasteTwin } from "@/lib/api"
import { getAvatarUrl } from "@/lib/avatar-utils"

interface TwinAvatarProps {
  twin: TasteTwin
  size?: "sm" | "md" | "lg"
  onClick?: () => void
}

export function TwinAvatar({ twin, size = "md", onClick }: TwinAvatarProps) {
  const sizeClasses = {
    sm: "w-12 h-12",
    md: "w-16 h-16",
    lg: "w-20 h-20",
  }

  const badgeSize = {
    sm: "text-[10px] px-1.5 py-0.5",
    md: "text-xs px-2 py-0.5",
    lg: "text-sm px-2.5 py-1",
  }

  return (
    <div className="relative inline-block cursor-pointer" onClick={onClick}>
      <img
        src={getAvatarUrl(twin.avatar_url, twin.twin_id)}
        alt={twin.name}
        className={`${sizeClasses[size]} rounded-full ring-2 ring-white object-cover bg-white`}
      />
      <div className={`absolute -bottom-1 -right-1 bg-[#4ECDC4] text-white font-bold rounded-full ${badgeSize[size]}`}>
        {Math.round(twin.similarity_score * 100)}%
      </div>
    </div>
  )
}
