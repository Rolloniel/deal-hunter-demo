"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Zap, Loader2 } from "lucide-react"
import { toast } from "sonner"

const getApiUrl = () => {
  if (process.env.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL
  }
  if (typeof window !== "undefined") {
    return `http://${window.location.hostname}:8000`
  }
  return "http://localhost:8000"
}

interface SimulateButtonProps {
  email?: string
  onSimulate?: () => void
  disabled?: boolean
  accessToken?: string
}

export function SimulateButton({ email, onSimulate, disabled, accessToken }: SimulateButtonProps) {
  const [isLoading, setIsLoading] = useState(false)

  const handleSimulate = async () => {
    setIsLoading(true)
    try {
      const headers: Record<string, string> = { "Content-Type": "application/json" }
      if (accessToken) {
        headers["Authorization"] = `Bearer ${accessToken}`
      }
      const response = await fetch(`${getApiUrl()}/api/alerts/simulate`, {
        method: "POST",
        headers,
        body: JSON.stringify({ email: email || undefined }),
      })

      if (!response.ok) {
        let errorMessage = "Failed to simulate price drop"
        try {
          const error = await response.json()
          errorMessage = error.detail || errorMessage
        } catch {
          // Response wasn't JSON (e.g., HTML error page)
        }
        throw new Error(errorMessage)
      }

      const data = await response.json()

      toast.success("Price Drop Simulated!", {
        description: `${data.message} Alert sent to ${data.email_recipient}`,
        duration: 5000,
      })

      // Trigger refresh
      onSimulate?.()
    } catch (error) {
      toast.error("Simulation Failed", {
        description: error instanceof Error ? error.message : "Please try again",
      })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Button
      onClick={handleSimulate}
      disabled={isLoading || disabled}
      className="bg-gradient-to-r from-amber-500 to-orange-600 text-white shadow-lg shadow-amber-500/20 transition-all hover:from-amber-600 hover:to-orange-700 hover:shadow-amber-500/30 disabled:opacity-50"
    >
      {isLoading ? (
        <>
          <Loader2 className="mr-2 size-4 animate-spin" />
          Simulating...
        </>
      ) : (
        <>
          <Zap className="mr-2 size-4" />
          Simulate Price Drop
        </>
      )}
    </Button>
  )
}
