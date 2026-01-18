"use client"

import { useState, useEffect, useCallback } from "react"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Bell, TrendingDown, CheckCircle2, XCircle } from "lucide-react"
import { Skeleton } from "@/components/ui/skeleton"

interface Alert {
  id: string
  product_name: string
  old_price: number
  new_price: number
  email_sent: boolean
  created_at: string | null
}

const getApiUrl = () => {
  if (process.env.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL
  }
  if (typeof window !== "undefined") {
    return `http://${window.location.hostname}:8000`
  }
  return "http://localhost:8000"
}

interface PriceAlertsProps {
  refreshKey?: number
  emailInput?: React.ReactNode
}

export function PriceAlerts({ refreshKey, emailInput }: PriceAlertsProps) {
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [isLoading, setIsLoading] = useState(true)

  const fetchAlerts = useCallback(async () => {
    setIsLoading(true)
    try {
      const response = await fetch(`${getApiUrl()}/api/alerts`)
      if (response.ok) {
        const data = await response.json()
        setAlerts(data.alerts || [])
      }
    } catch (err) {
      console.error("Failed to fetch alerts:", err)
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchAlerts()
  }, [fetchAlerts, refreshKey])

  // Loading state
  if (isLoading) {
    return (
      <Card className="border-zinc-800/50 bg-zinc-900/50 backdrop-blur-sm">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="flex size-10 items-center justify-center rounded-lg bg-gradient-to-br from-rose-500 to-pink-600">
                <Bell className="size-5 text-white" />
              </div>
              <div>
                <CardTitle className="text-white">Price Alerts</CardTitle>
                <CardDescription>Loading alerts...</CardDescription>
              </div>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-3">
          <Skeleton className="h-16 w-full rounded-lg" />
          <Skeleton className="h-16 w-full rounded-lg" />
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="border-zinc-800/50 bg-zinc-900/50 backdrop-blur-sm">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex size-10 items-center justify-center rounded-lg bg-gradient-to-br from-rose-500 to-pink-600">
              <Bell className="size-5 text-white" />
            </div>
            <div>
              <CardTitle className="text-white">Price Alerts</CardTitle>
              <CardDescription>Get notified when prices drop</CardDescription>
            </div>
          </div>
          <span className="rounded-full bg-zinc-800 px-2.5 py-0.5 text-xs font-medium text-zinc-400">
            {alerts.length} {alerts.length === 1 ? "alert" : "alerts"}
          </span>
        </div>
        {/* Email input slot */}
        {emailInput && (
          <div className="mt-4">
            <label className="mb-2 block text-sm text-zinc-400">
              Send alerts to:
            </label>
            {emailInput}
          </div>
        )}
      </CardHeader>
      <CardContent>
        {alerts.length === 0 ? (
          <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-zinc-800 py-12 text-center">
            <div className="mb-4 flex size-12 items-center justify-center rounded-full bg-zinc-800/50">
              <Bell className="size-6 text-zinc-600" />
            </div>
            <p className="text-sm font-medium text-zinc-400">No alerts yet</p>
            <p className="mt-1 text-xs text-zinc-600">
              Alerts will appear here when prices drop
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {alerts.map((alert) => {
              const savings = alert.old_price - alert.new_price
              return (
                <div
                  key={alert.id}
                  className="relative overflow-hidden rounded-xl border border-zinc-800/50 bg-zinc-800/30 p-4"
                >
                  <div className="absolute left-0 top-0 h-full w-1 bg-gradient-to-b from-emerald-400 to-emerald-600" />
                  <div className="flex items-center justify-between pl-3">
                    <div className="min-w-0 flex-1">
                      <h4 className="truncate font-medium text-white">
                        {alert.product_name}
                      </h4>
                      <div className="mt-1 flex items-center gap-2 text-sm">
                        <span className="text-zinc-500 line-through">
                          ${alert.old_price.toFixed(2)}
                        </span>
                        <TrendingDown className="size-3 text-emerald-400" />
                        <span className="font-medium text-emerald-400">
                          ${alert.new_price.toFixed(2)}
                        </span>
                        <span className="text-zinc-500">
                          (Save ${savings.toFixed(2)})
                        </span>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      {alert.email_sent ? (
                        <span className="flex items-center gap-1 text-xs text-emerald-400">
                          <CheckCircle2 className="size-3" />
                          Sent
                        </span>
                      ) : (
                        <span className="flex items-center gap-1 text-xs text-zinc-500">
                          <XCircle className="size-3" />
                          Not sent
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
