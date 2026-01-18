"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Zap, Loader2 } from "lucide-react"
import { toast } from "sonner"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

interface SimulateButtonProps {
  onSimulate?: () => void
  disabled?: boolean
}

export function SimulateButton({ onSimulate, disabled }: SimulateButtonProps) {
  const [isLoading, setIsLoading] = useState(false)

  const handleSimulate = async () => {
    setIsLoading(true)
    try {
      const response = await fetch(`${API_URL}/api/alerts/simulate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || "Failed to simulate price drop")
      }

      const data = await response.json()

      toast.success("Price Drop Simulated!", {
        description: `${data.message} Alert will be sent to alerts@kliuiev.com`,
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
