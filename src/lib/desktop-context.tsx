"use client"

import { createContext, useContext, useEffect, useState } from "react"

const DesktopContext = createContext<{ isDesktop: boolean }>({ isDesktop: false })

export function useDesktop() {
  return useContext(DesktopContext)
}

export function DesktopProvider({ children }: { children: React.ReactNode }) {
  const [isDesktop, setIsDesktop] = useState(false)

  useEffect(() => {
    const checkDesktop = () => {
      setIsDesktop(window.innerWidth >= 768)
    }

    checkDesktop()
    window.addEventListener("resize", checkDesktop)
    return () => window.removeEventListener("resize", checkDesktop)
  }, [])

  return <DesktopContext.Provider value={{ isDesktop }}>{children}</DesktopContext.Provider>
}
