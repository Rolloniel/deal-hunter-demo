"use client"

import { useState } from "react"
import { Header } from "@/components/layout/Header"
import { ChatInterface } from "@/components/chat/ChatInterface"
import { TrackedItems } from "@/components/dashboard/TrackedItems"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { MessageSquare, Bell } from "lucide-react"

export default function Home() {
  const [refreshKey, setRefreshKey] = useState(0)

  const handleChatComplete = () => {
    // Trigger refresh of tracked items after chat interaction
    setRefreshKey((prev) => prev + 1)
  }

  return (
    <div className="flex min-h-screen flex-col bg-zinc-950">
      {/* Ambient background effects */}
      <div className="pointer-events-none fixed inset-0 overflow-hidden">
        <div className="absolute -left-40 -top-40 size-80 rounded-full bg-emerald-500/10 blur-[100px]" />
        <div className="absolute -bottom-40 -right-40 size-80 rounded-full bg-teal-500/10 blur-[100px]" />
      </div>

      <Header />

      <main className="relative flex-1 p-4 sm:p-6 lg:p-8">
        <div className="mx-auto grid max-w-7xl gap-6 lg:grid-cols-2">
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
              <ChatInterface onMessageComplete={handleChatComplete} />
            </CardContent>
          </Card>

          {/* Dashboard Section */}
          <div className="flex flex-col gap-6">
            {/* Tracked Items Card - Dynamic */}
            <TrackedItems refreshKey={refreshKey} />

            {/* Price Alerts Card */}
            <Card className="border-zinc-800/50 bg-zinc-900/50 backdrop-blur-sm">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="flex size-10 items-center justify-center rounded-lg bg-gradient-to-br from-rose-500 to-pink-600">
                      <Bell className="size-5 text-white" />
                    </div>
                    <div>
                      <CardTitle className="text-white">Price Alerts</CardTitle>
                      <CardDescription>
                        Get notified when prices drop
                      </CardDescription>
                    </div>
                  </div>
                  <span className="rounded-full bg-zinc-800 px-2.5 py-0.5 text-xs font-medium text-zinc-400">
                    0 active
                  </span>
                </div>
              </CardHeader>
              <CardContent>
                <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-zinc-800 py-12 text-center">
                  <div className="mb-4 flex size-12 items-center justify-center rounded-full bg-zinc-800/50">
                    <Bell className="size-6 text-zinc-600" />
                  </div>
                  <p className="text-sm font-medium text-zinc-400">
                    No alerts configured
                  </p>
                  <p className="mt-1 text-xs text-zinc-600">
                    Ask me to alert you when a price drops
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
    </div>
  )
}
