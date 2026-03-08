"use client"

import { useState, useEffect, useCallback } from "react"
import { useRouter } from "next/navigation"
import { toast } from "sonner"
import { Header } from "@/components/layout/Header"
import { ChatInterface } from "@/components/chat/ChatInterface"
import { TrackedItems } from "@/components/dashboard/TrackedItems"
import { PriceAlerts } from "@/components/dashboard/PriceAlerts"
import { AnalyticsSummary } from "@/components/dashboard/AnalyticsSummary"
import { EmailInput } from "@/components/dashboard/EmailInput"
import { DemoTour } from "@/components/tour/DemoTour"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { MessageSquare } from "lucide-react"
import { useAuth } from "@/components/providers/AuthProvider"

const getApiUrl = () => {
  if (process.env.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL
  }
  if (typeof window !== "undefined") {
    return `http://${window.location.hostname}:8000`
  }
  return "http://localhost:8000"
}

export default function Home() {
  const { user, session, loading } = useAuth()
  const router = useRouter()
  const [refreshKey, setRefreshKey] = useState(0)
  const [chatResetKey, setChatResetKey] = useState(0)
  const [email, setEmail] = useState("")
  const [tourTrigger, setTourTrigger] = useState(false)

  const handleStartTour = () => {
    setTourTrigger(false)
    // Use a microtask to reset then set, so the DemoTour sees a fresh true
    setTimeout(() => setTourTrigger(true), 0)
  }

  const handleTourEnd = () => {
    setTourTrigger(false)
  }

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!loading && !user) {
      router.replace("/login")
    }
  }, [user, loading, router])

  // Load email from localStorage on mount
  useEffect(() => {
    const saved = localStorage.getItem("dealhunter_alert_email")
    if (saved) setEmail(saved)
  }, [])

  // Email change handler with localStorage persistence
  const handleEmailChange = (newEmail: string) => {
    setEmail(newEmail)
    localStorage.setItem("dealhunter_alert_email", newEmail)
  }

  const getAuthHeaders = useCallback((): Record<string, string> => {
    const token = session?.access_token
    if (token) {
      return { Authorization: `Bearer ${token}` }
    }
    return {}
  }, [session])

  // Reset demo handler
  const handleReset = async () => {
    try {
      const response = await fetch(`${getApiUrl()}/api/demo/reset`, {
        method: "POST",
        headers: getAuthHeaders(),
      })
      if (response.ok) {
        toast.success("Demo reset complete")
        setRefreshKey(prev => prev + 1)
        setChatResetKey(prev => prev + 1)
      } else {
        toast.error("Reset failed")
      }
    } catch {
      toast.error("Reset failed", { description: "Could not connect to server" })
    }
  }

  const handleChatComplete = () => {
    // Trigger refresh of tracked items after chat interaction
    setRefreshKey((prev) => prev + 1)
  }

  // Show loading while checking auth
  if (loading || !user) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-zinc-950">
        <div className="size-8 animate-spin rounded-full border-2 border-zinc-700 border-t-emerald-500" />
      </div>
    )
  }

  return (
    <div className="flex min-h-screen flex-col bg-zinc-950">
      {/* Ambient background effects */}
      <div className="pointer-events-none fixed inset-0 overflow-hidden">
        <div className="absolute -left-40 -top-40 size-80 rounded-full bg-emerald-500/10 blur-[100px]" />
        <div className="absolute -bottom-40 -right-40 size-80 rounded-full bg-teal-500/10 blur-[100px]" />
      </div>

      <Header onStartTour={handleStartTour} />
      <DemoTour startTour={tourTrigger} onTourEnd={handleTourEnd} />

      <main className="relative flex-1 p-4 sm:p-6 lg:p-8">
        <div className="mx-auto max-w-7xl space-y-6">
          {/* Analytics Summary Cards */}
          <AnalyticsSummary refreshKey={refreshKey} accessToken={session?.access_token} />

          <div className="grid gap-6 lg:grid-cols-2">
          {/* Chat Section */}
          <Card className="flex flex-col border-zinc-800/50 bg-zinc-900/50 backdrop-blur-sm">
            <CardHeader className="border-b border-zinc-800/50 pb-4">
              <div className="flex items-center gap-3">
                <div className="flex size-10 items-center justify-center rounded-lg bg-gradient-to-br from-violet-500 to-purple-600">
                  <MessageSquare className="size-5 text-white" />
                </div>
                <div>
                  <CardTitle className="text-white">AI Assistant</CardTitle>
                  <CardDescription>
                    Ask me to track prices, find deals, or set alerts
                  </CardDescription>
                </div>
              </div>
            </CardHeader>

            <CardContent className="flex flex-1 flex-col p-0">
              <ChatInterface
                onMessageComplete={handleChatComplete}
                resetKey={chatResetKey}
                accessToken={session?.access_token}
              />
            </CardContent>
          </Card>

          {/* Dashboard Section */}
          <div className="flex flex-col gap-6">
            {/* Tracked Items Card - Dynamic */}
            <TrackedItems
              refreshKey={refreshKey}
              email={email}
              onSimulate={handleChatComplete}
              onReset={handleReset}
              accessToken={session?.access_token}
            />

{/* Price Alerts Card - Dynamic */}
            <PriceAlerts
              refreshKey={refreshKey}
              emailInput={
                <EmailInput
                  value={email}
                  onChange={handleEmailChange}
                />
              }
              accessToken={session?.access_token}
            />
          </div>
        </div>
        </div>
      </main>
    </div>
  )
}
