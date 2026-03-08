"use client"

import { useState, useEffect, useCallback, useRef } from "react"
import { Package, Bell, DollarSign, TrendingDown } from "lucide-react"
import { Skeleton } from "@/components/ui/skeleton"

interface SummaryData {
  total_items: number
  total_alerts: number
  total_savings: number
  best_deal: {
    product_name: string
    old_price: number
    new_price: number
    pct_drop: number
  } | null
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

function AnimatedCounter({ value, prefix = "", suffix = "", decimals = 0 }: {
  value: number
  prefix?: string
  suffix?: string
  decimals?: number
}) {
  const [display, setDisplay] = useState(0)
  const animationRef = useRef<number | null>(null)
  const startTimeRef = useRef<number | null>(null)
  const prevValueRef = useRef(0)

  useEffect(() => {
    const from = prevValueRef.current
    const to = value
    const duration = 800

    if (animationRef.current) {
      cancelAnimationFrame(animationRef.current)
    }

    const animate = (timestamp: number) => {
      if (!startTimeRef.current) startTimeRef.current = timestamp
      const elapsed = timestamp - startTimeRef.current
      const progress = Math.min(elapsed / duration, 1)
      // Ease out cubic
      const eased = 1 - Math.pow(1 - progress, 3)
      const current = from + (to - from) * eased

      setDisplay(current)

      if (progress < 1) {
        animationRef.current = requestAnimationFrame(animate)
      } else {
        prevValueRef.current = to
      }
    }

    startTimeRef.current = null
    animationRef.current = requestAnimationFrame(animate)

    return () => {
      if (animationRef.current) cancelAnimationFrame(animationRef.current)
    }
  }, [value])

  const formatted = decimals > 0 ? display.toFixed(decimals) : Math.round(display).toString()

  return (
    <span className="tabular-nums">
      {prefix}{formatted}{suffix}
    </span>
  )
}

function SummaryCardSkeleton() {
  return (
    <div className="rounded-xl border border-zinc-800/50 bg-zinc-900/50 p-4 backdrop-blur-sm">
      <div className="flex items-center gap-3">
        <Skeleton className="size-9 rounded-lg" />
        <div className="flex-1 space-y-2">
          <Skeleton className="h-3 w-20" />
          <Skeleton className="h-6 w-16" />
        </div>
      </div>
    </div>
  )
}

interface AnalyticsSummaryProps {
  refreshKey?: number
  accessToken?: string
}

export function AnalyticsSummary({ refreshKey, accessToken }: AnalyticsSummaryProps) {
  const [data, setData] = useState<SummaryData | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  const fetchSummary = useCallback(async () => {
    try {
      const headers: Record<string, string> = {}
      if (accessToken) {
        headers["Authorization"] = `Bearer ${accessToken}`
      }
      const response = await fetch(`${getApiUrl()}/api/analytics/summary`, { headers })
      if (!response.ok) return
      const result = await response.json()
      setData(result)
    } catch {
      // Silently fail — cards just show zeros
    } finally {
      setIsLoading(false)
    }
  }, [accessToken])

  useEffect(() => {
    fetchSummary()
  }, [fetchSummary, refreshKey])

  if (isLoading) {
    return (
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <SummaryCardSkeleton />
        <SummaryCardSkeleton />
        <SummaryCardSkeleton />
        <SummaryCardSkeleton />
      </div>
    )
  }

  const cards = [
    {
      label: "Items Tracked",
      value: data?.total_items ?? 0,
      icon: Package,
      gradient: "from-amber-500 to-orange-600",
      color: "text-amber-400",
    },
    {
      label: "Alerts Triggered",
      value: data?.total_alerts ?? 0,
      icon: Bell,
      gradient: "from-rose-500 to-pink-600",
      color: "text-rose-400",
    },
    {
      label: "Total Savings",
      value: data?.total_savings ?? 0,
      icon: DollarSign,
      prefix: "$",
      decimals: 2,
      gradient: "from-emerald-500 to-teal-600",
      color: "text-emerald-400",
    },
    {
      label: "Best Deal",
      value: data?.best_deal?.pct_drop ?? 0,
      suffix: "%",
      subtitle: data?.best_deal?.product_name,
      icon: TrendingDown,
      gradient: "from-violet-500 to-purple-600",
      color: "text-violet-400",
    },
  ]

  return (
    <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
      {cards.map((card) => (
        <div
          key={card.label}
          className="group rounded-xl border border-zinc-800/50 bg-zinc-900/50 p-4 backdrop-blur-sm transition-all hover:border-zinc-700/50 hover:bg-zinc-800/50"
        >
          <div className="flex items-center gap-3">
            <div className={`flex size-9 shrink-0 items-center justify-center rounded-lg bg-gradient-to-br ${card.gradient}`}>
              <card.icon className="size-4 text-white" />
            </div>
            <div className="min-w-0">
              <p className="truncate text-xs text-zinc-500">{card.label}</p>
              <p className={`text-lg font-bold leading-tight ${card.color}`}>
                <AnimatedCounter
                  value={card.value}
                  prefix={card.prefix}
                  suffix={card.suffix}
                  decimals={card.decimals}
                />
              </p>
              {card.subtitle && (
                <p className="truncate text-[10px] text-zinc-600">{card.subtitle}</p>
              )}
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}
