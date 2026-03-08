"use client"

import { createContext, useContext, useEffect, useState } from "react"

interface AppUser {
  id: string
  email: string
}

interface AuthContextType {
  user: AppUser | null
  loading: boolean
  signOut: () => Promise<void>
  refreshAuth: () => Promise<void>
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  loading: true,
  signOut: async () => {},
  refreshAuth: async () => {},
})

const getApiUrl = () => {
  if (process.env.NEXT_PUBLIC_API_URL) return process.env.NEXT_PUBLIC_API_URL
  if (typeof window !== "undefined") return `http://${window.location.hostname}:8000`
  return "http://localhost:8000"
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<AppUser | null>(null)
  const [loading, setLoading] = useState(true)

  const checkAuth = async () => {
    try {
      const res = await fetch(`${getApiUrl()}/auth/me`, { credentials: "include" })
      const data = await res.json()
      setUser(data.user || null)
    } catch {
      setUser(null)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    checkAuth()
  }, [])

  const signOut = async () => {
    try {
      await fetch(`${getApiUrl()}/auth/logout`, {
        method: "POST",
        credentials: "include",
      })
    } catch {
      // Ignore errors
    }
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, loading, signOut, refreshAuth: checkAuth }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)
