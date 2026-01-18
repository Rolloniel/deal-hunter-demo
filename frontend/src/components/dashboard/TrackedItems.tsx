"use client"

import { useState, useEffect, useCallback, useRef } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Package, TrendingDown, RefreshCw, WifiOff, RotateCcw } from "lucide-react"
import { SimulateButton } from "./SimulateButton"
import { Skeleton } from "@/components/ui/skeleton"
import { toast } from "sonner"

interface TrackedItem {
  id: string
  product_id: string
  target_price: number
  email: string
  created_at: string
  products: {
    id: string
    name: string
    category: string
    current_price: number
    image_url: string | null
  }
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

// Skeleton card for loading state
function TrackedItemSkeleton() {
  return (
    <div className="relative overflow-hidden rounded-xl border border-zinc-800/50 bg-zinc-800/30 p-4">
      <div className="absolute left-0 top-0 h-full w-1 bg-gradient-to-b from-zinc-600 to-zinc-700" />
      <div className="flex items-center justify-between pl-3">
        <div className="flex items-center gap-4">
          <Skeleton className="size-14 rounded-lg" />
          <div className="space-y-2">
            <Skeleton className="h-5 w-32" />
            <Skeleton className="h-4 w-20" />
          </div>
        </div>
        <div className="space-y-2 text-right">
          <Skeleton className="ml-auto h-7 w-20" />
          <Skeleton className="ml-auto h-4 w-28" />
        </div>
      </div>
    </div>
  )
}

interface TrackedItemsProps {
  refreshKey?: number
  email?: string
  onSimulate?: () => void
  onReset?: () => void
}

export function TrackedItems({ refreshKey, email, onSimulate, onReset }: TrackedItemsProps) {
  const [items, setItems] = useState<TrackedItem[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [hasError, setHasError] = useState(false)
  const retryCount = useRef(0)
  const maxRetries = 3

  const fetchItems = useCallback(async (isManualRefresh = false) => {
    if (isManualRefresh) {
      setIsRefreshing(true)
    } else {
      setIsLoading(true)
    }
    setHasError(false)

    try {
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), 15000) // 15s timeout for Railway cold start

      const response = await fetch(`${getApiUrl()}/api/products/tracked`, {
        signal: controller.signal,
      })
      clearTimeout(timeoutId)

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`)
      }

      const data = await response.json()
      setItems(data.tracked_items || [])
      retryCount.current = 0 // Reset retry count on success
    } catch (err) {
      setHasError(true)
      const isAbort = err instanceof Error && err.name === "AbortError"
      const message = isAbort
        ? "Request timed out. The server may be starting up."
        : err instanceof Error
          ? err.message
          : "Failed to load tracked items"

      // Auto-retry for timeouts (Railway cold start)
      if (isAbort && retryCount.current < maxRetries) {
        retryCount.current++
        toast.loading(`Server starting up... Retry ${retryCount.current}/${maxRetries}`, {
          id: "tracked-items-retry",
          duration: 3000,
        })
        setTimeout(() => fetchItems(isManualRefresh), 2000)
        return
      }

      toast.error(message, {
        id: "tracked-items-error",
        description: "Check your connection and try again",
      })
    } finally {
      setIsLoading(false)
      setIsRefreshing(false)
    }
  }, [])

  useEffect(() => {
    fetchItems()
  }, [fetchItems, refreshKey])

  const handleRefresh = () => {
    retryCount.current = 0
    fetchItems(true)
  }

  // Loading state with skeletons
  if (isLoading) {
    return (
      <Card className="border-zinc-800/50 bg-zinc-900/50 backdrop-blur-sm">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="flex size-10 items-center justify-center rounded-lg bg-gradient-to-br from-amber-500 to-orange-600">
                <Package className="size-5 text-white" />
              </div>
              <div>
                <CardTitle className="text-white">Tracked Items</CardTitle>
                <p className="text-sm text-zinc-400">Loading your items...</p>
              </div>
            </div>
            <Skeleton className="h-6 w-16 rounded-full" />
          </div>
        </CardHeader>
        <CardContent className="space-y-3">
          <TrackedItemSkeleton />
          <TrackedItemSkeleton />
          <TrackedItemSkeleton />
        </CardContent>
      </Card>
    )
  }

  // Error state with empty card (toast handles the message)
  if (hasError && items.length === 0) {
    return (
      <Card className="border-zinc-800/50 bg-zinc-900/50 backdrop-blur-sm">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="flex size-10 items-center justify-center rounded-lg bg-gradient-to-br from-zinc-600 to-zinc-700">
                <WifiOff className="size-5 text-zinc-400" />
              </div>
              <div>
                <CardTitle className="text-white">Tracked Items</CardTitle>
                <p className="text-sm text-zinc-400">Unable to connect</p>
              </div>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-zinc-800 py-12 text-center">
            <div className="mb-4 flex size-12 items-center justify-center rounded-full bg-zinc-800/50">
              <WifiOff className="size-6 text-zinc-600" />
            </div>
            <p className="text-sm font-medium text-zinc-400">
              Couldn&apos;t load your items
            </p>
            <p className="mt-1 text-xs text-zinc-600">
              The server might be waking up. Try refreshing in a moment.
            </p>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="border-zinc-800/50 bg-zinc-900/50 backdrop-blur-sm">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex size-10 items-center justify-center rounded-lg bg-gradient-to-br from-amber-500 to-orange-600">
              <Package className="size-5 text-white" />
            </div>
            <div>
              <CardTitle className="text-white">Tracked Items</CardTitle>
              <p className="text-sm text-zinc-400">
                Products you&apos;re monitoring
              </p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <span className="rounded-full bg-zinc-800 px-2.5 py-0.5 text-xs font-medium text-zinc-400">
              {items.length} {items.length === 1 ? "item" : "items"}
            </span>
            <SimulateButton
              email={email}
              onSimulate={onSimulate}
              disabled={items.length === 0}
            />
            <Button
              variant="ghost"
              size="icon"
              onClick={handleRefresh}
              disabled={isRefreshing}
              className="size-8 text-zinc-400 hover:text-white disabled:opacity-50"
            >
              <RefreshCw className={`size-4 ${isRefreshing ? "animate-spin" : ""}`} />
            </Button>
            {onReset && (
              <Button
                variant="ghost"
                size="icon"
                onClick={onReset}
                className="size-8 text-zinc-400 hover:text-white"
                title="Reset Demo"
              >
                <RotateCcw className="size-4" />
              </Button>
            )}
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {items.length === 0 ? (
          <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-zinc-800 py-12 text-center">
            <div className="mb-4 flex size-12 items-center justify-center rounded-full bg-zinc-800/50">
              <Package className="size-6 text-zinc-600" />
            </div>
            <p className="text-sm font-medium text-zinc-400">
              No items tracked yet
            </p>
            <p className="mt-1 max-w-[200px] text-xs text-zinc-600">
              Start a conversation to track your first product and get price alerts!
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {items.map((item) => {
              const product = item.products
              const isAlertTriggered =
                product?.current_price <= item.target_price

              return (
                <div
                  key={item.id}
                  className="group relative overflow-hidden rounded-xl border border-zinc-800/50 bg-zinc-800/30 p-4 transition-all hover:border-zinc-700/50 hover:bg-zinc-800/50"
                >
                  {/* Status indicator bar */}
                  <div
                    className={`absolute left-0 top-0 h-full w-1 ${
                      isAlertTriggered
                        ? "bg-gradient-to-b from-emerald-400 to-emerald-600"
                        : "bg-gradient-to-b from-amber-400 to-orange-500"
                    }`}
                  />

                  <div className="flex items-center justify-between pl-3">
                    <div className="flex items-center gap-4">
                      {/* Product image placeholder */}
                      <div className="flex size-14 items-center justify-center rounded-lg bg-zinc-700/50 ring-1 ring-zinc-600/30">
                        {product?.image_url ? (
                          <img
                            src={product.image_url}
                            alt={product.name}
                            className="size-full rounded-lg object-cover"
                          />
                        ) : (
                          <Package className="size-6 text-zinc-500" />
                        )}
                      </div>

                      <div className="min-w-0">
                        <h4 className="truncate font-medium text-white">
                          {product?.name || "Unknown Product"}
                        </h4>
                        <div className="mt-1 flex items-center gap-2">
                          <span className="rounded-md bg-zinc-700/50 px-2 py-0.5 text-xs text-zinc-400">
                            {product?.category || "Unknown"}
                          </span>
                          {isAlertTriggered && (
                            <span className="flex items-center gap-1 rounded-md bg-emerald-500/20 px-2 py-0.5 text-xs font-medium text-emerald-400">
                              <TrendingDown className="size-3" />
                              Alert Triggered!
                            </span>
                          )}
                        </div>
                      </div>
                    </div>

                    <div className="text-right">
                      <p className="text-xl font-bold tabular-nums text-white">
                        ${product?.current_price?.toFixed(2) || "0.00"}
                      </p>
                      <p className="mt-0.5 flex items-center justify-end gap-1 text-sm text-zinc-400">
                        <TrendingDown className="size-3 text-emerald-400" />
                        <span>
                          Alert below{" "}
                          <span className="font-medium text-emerald-400">
                            ${item.target_price?.toFixed(2) || "0.00"}
                          </span>
                        </span>
                      </p>
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
