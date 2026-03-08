"use client"

import { useState, useEffect, useCallback } from "react"
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts"
import { X, TrendingDown } from "lucide-react"

interface PricePoint {
  price: number
  created_at: string
}

interface ChartDataPoint {
  date: string
  price: number
  timestamp: number
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

function formatDate(dateStr: string): string {
  const d = new Date(dateStr)
  return d.toLocaleDateString("en-US", { month: "short", day: "numeric" })
}

function CustomTooltip({
  active,
  payload,
  label,
}: {
  active?: boolean
  payload?: Array<{ value: number }>
  label?: string
}) {
  if (!active || !payload?.length) return null
  return (
    <div className="rounded-lg border border-zinc-700 bg-zinc-900 px-3 py-2 shadow-xl">
      <p className="text-xs text-zinc-400">{label}</p>
      <p className="text-sm font-bold text-white">
        ${payload[0].value.toFixed(2)}
      </p>
    </div>
  )
}

/** Mini sparkline for the tracked item card */
export function PriceSparkline({
  productId,
  targetPrice,
  onClick,
}: {
  productId: string
  targetPrice: number
  onClick: () => void
}) {
  const [data, setData] = useState<ChartDataPoint[]>([])

  useEffect(() => {
    const controller = new AbortController()
    fetch(`${getApiUrl()}/api/products/${productId}/price-history`, {
      signal: controller.signal,
    })
      .then((r) => r.json())
      .then((json) => {
        const points: ChartDataPoint[] = (json.price_history || []).map(
          (p: PricePoint) => ({
            date: formatDate(p.created_at),
            price: p.price,
            timestamp: new Date(p.created_at).getTime(),
          })
        )
        setData(points)
      })
      .catch(() => {})
    return () => controller.abort()
  }, [productId])

  if (data.length < 2) return null

  const minPrice = Math.min(...data.map((d) => d.price))
  const maxPrice = Math.max(...data.map((d) => d.price))
  const lastPrice = data[data.length - 1].price
  const isBelow = lastPrice <= targetPrice

  return (
    <button
      onClick={onClick}
      className="group/spark flex h-10 w-24 cursor-pointer items-center rounded-md border border-zinc-800/50 bg-zinc-900/50 px-1 transition-all hover:border-zinc-600 hover:bg-zinc-800/50"
      title="Click to expand price history"
    >
      <ResponsiveContainer width="100%" height={32}>
        <AreaChart data={data} margin={{ top: 2, right: 2, bottom: 2, left: 2 }}>
          <defs>
            <linearGradient id={`spark-${productId}`} x1="0" y1="0" x2="0" y2="1">
              <stop
                offset="0%"
                stopColor={isBelow ? "#10b981" : "#f59e0b"}
                stopOpacity={0.3}
              />
              <stop
                offset="100%"
                stopColor={isBelow ? "#10b981" : "#f59e0b"}
                stopOpacity={0}
              />
            </linearGradient>
          </defs>
          <Area
            type="monotone"
            dataKey="price"
            stroke={isBelow ? "#10b981" : "#f59e0b"}
            strokeWidth={1.5}
            fill={`url(#spark-${productId})`}
            dot={false}
            isAnimationActive={false}
          />
          <YAxis domain={[minPrice * 0.95, maxPrice * 1.05]} hide />
        </AreaChart>
      </ResponsiveContainer>
    </button>
  )
}

/** Expanded price history chart overlay */
export function PriceHistoryExpanded({
  productId,
  productName,
  targetPrice,
  currentPrice,
  onClose,
}: {
  productId: string
  productName: string
  targetPrice: number
  currentPrice: number
  onClose: () => void
}) {
  const [data, setData] = useState<ChartDataPoint[]>([])
  const [isLoading, setIsLoading] = useState(true)

  const fetchHistory = useCallback(async () => {
    setIsLoading(true)
    try {
      const res = await fetch(
        `${getApiUrl()}/api/products/${productId}/price-history`
      )
      const json = await res.json()
      const points: ChartDataPoint[] = (json.price_history || []).map(
        (p: PricePoint) => ({
          date: formatDate(p.created_at),
          price: p.price,
          timestamp: new Date(p.created_at).getTime(),
        })
      )
      setData(points)
    } catch {
      // silently fail
    } finally {
      setIsLoading(false)
    }
  }, [productId])

  useEffect(() => {
    fetchHistory()
  }, [fetchHistory])

  useEffect(() => {
    const handleKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose()
    }
    window.addEventListener("keydown", handleKey)
    return () => window.removeEventListener("keydown", handleKey)
  }, [onClose])

  const allPrices = data.map((d) => d.price)
  const minPrice = allPrices.length
    ? Math.min(...allPrices, targetPrice) * 0.9
    : 0
  const maxPrice = allPrices.length
    ? Math.max(...allPrices, targetPrice) * 1.1
    : 100

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
      onClick={onClose}
    >
      <div
        className="mx-4 w-full max-w-2xl rounded-2xl border border-zinc-700/50 bg-zinc-900 p-6 shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-white">{productName}</h3>
            <div className="mt-1 flex items-center gap-3 text-sm">
              <span className="text-zinc-400">
                Current:{" "}
                <span className="font-medium text-white">
                  ${currentPrice.toFixed(2)}
                </span>
              </span>
              <span className="flex items-center gap-1 text-zinc-400">
                <TrendingDown className="size-3 text-emerald-400" />
                Alert below{" "}
                <span className="font-medium text-emerald-400">
                  ${targetPrice.toFixed(2)}
                </span>
              </span>
            </div>
          </div>
          <button
            onClick={onClose}
            className="flex size-8 items-center justify-center rounded-lg text-zinc-400 transition-colors hover:bg-zinc-800 hover:text-white"
          >
            <X className="size-5" />
          </button>
        </div>

        {/* Chart */}
        <div className="h-64">
          {isLoading ? (
            <div className="flex h-full items-center justify-center">
              <div className="size-6 animate-spin rounded-full border-2 border-zinc-600 border-t-emerald-400" />
            </div>
          ) : data.length < 2 ? (
            <div className="flex h-full flex-col items-center justify-center text-center">
              <TrendingDown className="mb-2 size-8 text-zinc-600" />
              <p className="text-sm text-zinc-400">
                Not enough price data yet
              </p>
              <p className="mt-1 text-xs text-zinc-600">
                Price history builds as prices change
              </p>
            </div>
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart
                data={data}
                margin={{ top: 10, right: 10, bottom: 0, left: 10 }}
              >
                <defs>
                  <linearGradient id="expandedGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#10b981" stopOpacity={0.2} />
                    <stop offset="100%" stopColor="#10b981" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <XAxis
                  dataKey="date"
                  stroke="#52525b"
                  tick={{ fill: "#71717a", fontSize: 12 }}
                  tickLine={false}
                  axisLine={false}
                />
                <YAxis
                  domain={[minPrice, maxPrice]}
                  stroke="#52525b"
                  tick={{ fill: "#71717a", fontSize: 12 }}
                  tickLine={false}
                  axisLine={false}
                  tickFormatter={(v: number) => `$${v.toFixed(0)}`}
                  width={50}
                />
                <Tooltip content={<CustomTooltip />} />
                <ReferenceLine
                  y={targetPrice}
                  stroke="#10b981"
                  strokeDasharray="6 4"
                  strokeOpacity={0.6}
                  label={{
                    value: `Target $${targetPrice.toFixed(0)}`,
                    fill: "#10b981",
                    fontSize: 11,
                    position: "right",
                  }}
                />
                <Area
                  type="monotone"
                  dataKey="price"
                  stroke="#10b981"
                  strokeWidth={2}
                  fill="url(#expandedGrad)"
                  dot={{ r: 3, fill: "#10b981", strokeWidth: 0 }}
                  activeDot={{
                    r: 5,
                    fill: "#10b981",
                    stroke: "#064e3b",
                    strokeWidth: 2,
                  }}
                />
              </AreaChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>
    </div>
  )
}
