"use client"

import { useState, useEffect, useCallback } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Package, TrendingDown, RefreshCw, Loader2 } from "lucide-react"

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

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

export function TrackedItems({ refreshKey }: { refreshKey?: number }) {
  const [items, setItems] = useState<TrackedItem[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchItems = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    try {
      const response = await fetch(`${API_URL}/api/products/tracked`)
      if (!response.ok) throw new Error("Failed to fetch tracked items")
      const data = await response.json()
      setItems(data.tracked_items || [])
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred")
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchItems()
  }, [fetchItems, refreshKey])

  if (isLoading) {
    return (
      <Card className="border-zinc-800/50 bg-zinc-900/50 backdrop-blur-sm">
        <CardContent className="flex items-center justify-center py-12">
          <Loader2 className="size-8 animate-spin text-zinc-500" />
        </CardContent>
      </Card>
    )
  }

  if (error) {
    return (
      <Card className="border-zinc-800/50 bg-zinc-900/50 backdrop-blur-sm">
        <CardContent className="flex flex-col items-center justify-center py-12 text-center">
          <p className="text-sm text-red-400">{error}</p>
          <Button
            variant="ghost"
            size="sm"
            onClick={fetchItems}
            className="mt-4 text-zinc-400 hover:text-white"
          >
            <RefreshCw className="mr-2 size-4" />
            Try Again
          </Button>
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
          <div className="flex items-center gap-2">
            <span className="rounded-full bg-zinc-800 px-2.5 py-0.5 text-xs font-medium text-zinc-400">
              {items.length} {items.length === 1 ? "item" : "items"}
            </span>
            <Button
              variant="ghost"
              size="icon"
              onClick={fetchItems}
              className="size-8 text-zinc-400 hover:text-white"
            >
              <RefreshCw className="size-4" />
            </Button>
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
            <p className="mt-1 text-xs text-zinc-600">
              Start chatting to track a product!
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
