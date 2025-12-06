'use client'

import React from 'react'
import { usePathname, useRouter } from 'next/navigation'
import { Home, Search, Users, Heart, User, LucideIcon } from 'lucide-react'
import { colors } from '@/lib/design-tokens'

interface NavItem {
  label: string
  icon: LucideIcon
  href: string
  activePattern: RegExp
}

const navItems: NavItem[] = [
  {
    label: 'Home',
    icon: Home,
    href: '/home',
    activePattern: /^\/home$/,
  },
  {
    label: 'Search',
    icon: Search,
    href: '/search',
    activePattern: /^\/search/,
  },
  {
    label: 'Twins',
    icon: Users,
    href: '/twins',
    activePattern: /^\/twins/,
  },
  {
    label: 'Date',
    icon: Heart,
    href: '/date-night',
    activePattern: /^\/date-night/,
  },
  {
    label: 'Profile',
    icon: User,
    href: '/profile',
    activePattern: /^\/profile/,
  },
]

export const BottomNav: React.FC = () => {
  const pathname = usePathname()
  const router = useRouter()

  // Don't show bottom nav on auth pages
  if (pathname === '/login' || pathname === '/register' || pathname === '/') {
    return null
  }

  return (
    <nav
      className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 shadow-lg z-50"
      role="navigation"
      aria-label="Main navigation"
    >
      <div className="max-w-md mx-auto h-[72px] flex items-center justify-around px-2">
        {navItems.map(({ label, icon: Icon, href, activePattern }) => {
          const isActive = activePattern.test(pathname)

          return (
            <button
              key={href}
              onClick={() => router.push(href)}
              className={`
                flex flex-col items-center justify-center
                min-w-[64px] h-16 rounded-xl
                transition-all duration-200
                ${isActive
                  ? 'text-[#D32323]'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                }
              `}
              aria-label={label}
              aria-current={isActive ? 'page' : undefined}
            >
              <div
                className={`
                  relative transition-all duration-200
                  ${isActive ? 'scale-110' : ''}
                `}
              >
                <Icon
                  className={`w-6 h-6 ${isActive ? 'stroke-[2.5]' : 'stroke-2'}`}
                  aria-hidden="true"
                />
                {isActive && (
                  <div
                    className="absolute -bottom-1 left-1/2 -translate-x-1/2 w-1 h-1 rounded-full bg-[#D32323]"
                    aria-hidden="true"
                  />
                )}
              </div>
              <span
                className={`
                  text-xs mt-1 font-medium transition-all duration-200
                  ${isActive ? 'font-semibold' : ''}
                `}
              >
                {label}
              </span>
            </button>
          )
        })}
      </div>
    </nav>
  )
}
