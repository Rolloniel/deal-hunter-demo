import { Header } from "@/components/layout/Header"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"
import {
  MessageSquare,
  Package,
  TrendingDown,
  Bell,
  Send,
  Sparkles,
} from "lucide-react"

export default function Home() {
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
              {/* Chat messages area */}
              <ScrollArea className="flex-1 p-6">
                <div className="space-y-4">
                  {/* Welcome message */}
                  <div className="flex gap-3">
                    <div className="flex size-8 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-emerald-500 to-teal-600">
                      <Sparkles className="size-4 text-white" />
                    </div>
                    <div className="rounded-2xl rounded-tl-sm bg-zinc-800/50 px-4 py-3">
                      <p className="text-sm text-zinc-300">
                        Hey! I&apos;m your DealHunter AI assistant. I can help
                        you:
                      </p>
                      <ul className="mt-2 space-y-1 text-sm text-zinc-400">
                        <li className="flex items-center gap-2">
                          <TrendingDown className="size-3 text-emerald-500" />
                          Track product prices across stores
                        </li>
                        <li className="flex items-center gap-2">
                          <Bell className="size-3 text-emerald-500" />
                          Set up price drop alerts
                        </li>
                        <li className="flex items-center gap-2">
                          <Package className="size-3 text-emerald-500" />
                          Find the best deals on items you want
                        </li>
                      </ul>
                      <p className="mt-3 text-sm text-zinc-300">
                        Just paste a product URL or tell me what you&apos;re
                        looking for!
                      </p>
                    </div>
                  </div>
                </div>
              </ScrollArea>

              {/* Chat input */}
              <div className="border-t border-zinc-800/50 p-4">
                <div className="flex gap-2">
                  <Input
                    placeholder="Paste a product URL or describe what you're looking for..."
                    className="flex-1 border-zinc-700 bg-zinc-800/50 text-white placeholder:text-zinc-500"
                  />
                  <Button className="bg-gradient-to-r from-emerald-500 to-teal-600 text-white hover:from-emerald-600 hover:to-teal-700">
                    <Send className="size-4" />
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Dashboard Section */}
          <div className="flex flex-col gap-6">
            {/* Tracked Items Card */}
            <Card className="border-zinc-800/50 bg-zinc-900/50 backdrop-blur-sm">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="flex size-10 items-center justify-center rounded-lg bg-gradient-to-br from-amber-500 to-orange-600">
                      <Package className="size-5 text-white" />
                    </div>
                    <div>
                      <CardTitle className="text-white">
                        Tracked Items
                      </CardTitle>
                      <CardDescription>
                        Products you&apos;re monitoring
                      </CardDescription>
                    </div>
                  </div>
                  <span className="rounded-full bg-zinc-800 px-2.5 py-0.5 text-xs font-medium text-zinc-400">
                    0 items
                  </span>
                </div>
              </CardHeader>
              <CardContent>
                <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-zinc-800 py-12 text-center">
                  <div className="mb-4 flex size-12 items-center justify-center rounded-full bg-zinc-800/50">
                    <Package className="size-6 text-zinc-600" />
                  </div>
                  <p className="text-sm font-medium text-zinc-400">
                    No items tracked yet
                  </p>
                  <p className="mt-1 text-xs text-zinc-600">
                    Start by pasting a product URL in the chat
                  </p>
                </div>
              </CardContent>
            </Card>

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
