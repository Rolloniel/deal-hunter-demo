import Link from "next/link"
import { Target, MessageSquare, TrendingDown, Bell, BarChart3, ArrowRight, Zap } from "lucide-react"
import { Button } from "@/components/ui/button"

const features = [
  {
    icon: MessageSquare,
    title: "AI Chat Assistant",
    description: "Tell our AI what you want to track. It finds products, compares prices, and sets up alerts — all through natural conversation.",
    gradient: "from-violet-500 to-purple-600",
  },
  {
    icon: TrendingDown,
    title: "Price Tracking",
    description: "Monitor prices across retailers in real-time. See historical trends and get notified the moment prices drop.",
    gradient: "from-emerald-500 to-teal-600",
  },
  {
    icon: Bell,
    title: "Smart Alerts",
    description: "Set custom price thresholds and get instant notifications. Never miss a deal on products you care about.",
    gradient: "from-amber-500 to-orange-600",
  },
  {
    icon: BarChart3,
    title: "Analytics Dashboard",
    description: "See your savings at a glance. Track price history, compare deals, and understand buying patterns.",
    gradient: "from-sky-500 to-blue-600",
  },
]

export default function LandingPage() {
  return (
    <div className="flex min-h-screen flex-col bg-zinc-950">
      {/* Ambient background effects */}
      <div className="pointer-events-none fixed inset-0 overflow-hidden">
        <div className="absolute -left-40 -top-40 size-96 rounded-full bg-emerald-500/10 blur-[120px]" />
        <div className="absolute -bottom-40 -right-40 size-96 rounded-full bg-teal-500/10 blur-[120px]" />
        <div className="absolute left-1/2 top-1/3 size-64 -translate-x-1/2 rounded-full bg-violet-500/5 blur-[100px]" />
      </div>

      {/* Nav */}
      <header className="relative border-b border-zinc-800/50 bg-zinc-950/80 backdrop-blur-xl">
        <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-emerald-500/50 to-transparent" />
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
          <div className="flex items-center gap-3">
            <div className="relative flex size-10 items-center justify-center rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600 shadow-lg shadow-emerald-500/20">
              <Target className="size-5 text-white" strokeWidth={2.5} />
              <div className="absolute inset-0 rounded-xl bg-emerald-500/20 blur-md" />
            </div>
            <div className="flex flex-col">
              <h1 className="text-lg font-bold tracking-tight text-white">
                DealHunter
                <span className="ml-1 bg-gradient-to-r from-emerald-400 to-teal-400 bg-clip-text text-transparent">
                  AI
                </span>
              </h1>
              <span className="text-[10px] font-medium uppercase tracking-widest text-zinc-500">
                Price Intelligence
              </span>
            </div>
          </div>
          <Button asChild variant="outline" size="sm" className="border-zinc-700 text-zinc-300 hover:border-emerald-500/50 hover:text-white">
            <Link href="/app">
              Launch App
              <ArrowRight className="size-3.5" />
            </Link>
          </Button>
        </div>
      </header>

      {/* Hero */}
      <section className="relative flex flex-1 flex-col items-center justify-center px-4 py-20 sm:py-32">
        <div className="mx-auto max-w-4xl text-center">
          <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-zinc-800 bg-zinc-900/50 px-4 py-1.5">
            <div className="relative flex size-2">
              <span className="absolute inline-flex size-full animate-ping rounded-full bg-emerald-400 opacity-75" />
              <span className="relative inline-flex size-2 rounded-full bg-emerald-500" />
            </div>
            <span className="text-xs font-medium text-zinc-400">
              <Zap className="mr-1 inline size-3 text-emerald-500" />
              AI-Powered Price Intelligence
            </span>
          </div>

          <h2 className="mb-6 text-4xl font-bold tracking-tight text-white sm:text-5xl lg:text-6xl">
            Stop overpaying.
            <br />
            <span className="bg-gradient-to-r from-emerald-400 via-teal-400 to-cyan-400 bg-clip-text text-transparent">
              Start deal hunting.
            </span>
          </h2>

          <p className="mx-auto mb-10 max-w-2xl text-lg text-zinc-400 sm:text-xl">
            Track prices, get alerts, and find the best deals — all powered by AI
            that understands what you&apos;re looking for.
          </p>

          <div className="flex flex-col items-center gap-4 sm:flex-row sm:justify-center">
            <Button asChild size="lg" className="bg-gradient-to-r from-emerald-500 to-teal-600 text-white shadow-lg shadow-emerald-500/25 hover:from-emerald-600 hover:to-teal-700">
              <Link href="/app">
                Try the Demo
                <ArrowRight className="size-4" />
              </Link>
            </Button>
          </div>
        </div>

        {/* App mockup / preview */}
        <div className="relative mx-auto mt-16 w-full max-w-5xl px-4 sm:mt-20">
          <div className="overflow-hidden rounded-xl border border-zinc-800/50 bg-zinc-900/50 shadow-2xl shadow-black/50 backdrop-blur-sm">
            {/* Browser chrome */}
            <div className="flex items-center gap-2 border-b border-zinc-800/50 bg-zinc-900/80 px-4 py-3">
              <div className="flex gap-1.5">
                <div className="size-3 rounded-full bg-zinc-700" />
                <div className="size-3 rounded-full bg-zinc-700" />
                <div className="size-3 rounded-full bg-zinc-700" />
              </div>
              <div className="mx-auto flex items-center gap-2 rounded-md bg-zinc-800/50 px-3 py-1">
                <span className="text-xs text-zinc-500">dealhunter.ai/app</span>
              </div>
            </div>
            {/* Mock app content */}
            <div className="grid gap-4 p-6 sm:grid-cols-2">
              {/* Chat preview */}
              <div className="rounded-lg border border-zinc-800/50 bg-zinc-950/50 p-4">
                <div className="mb-3 flex items-center gap-2">
                  <div className="flex size-7 items-center justify-center rounded-md bg-gradient-to-br from-violet-500 to-purple-600">
                    <MessageSquare className="size-3.5 text-white" />
                  </div>
                  <span className="text-sm font-medium text-zinc-300">AI Assistant</span>
                </div>
                <div className="space-y-2">
                  <div className="w-3/4 rounded-lg bg-zinc-800/50 px-3 py-2">
                    <p className="text-xs text-zinc-400">Track the price of AirPods Pro</p>
                  </div>
                  <div className="ml-auto w-4/5 rounded-lg bg-emerald-500/10 px-3 py-2">
                    <p className="text-xs text-emerald-400">Found AirPods Pro 2 at $189. I&apos;ll track it and alert you when it drops below $170.</p>
                  </div>
                </div>
              </div>
              {/* Dashboard preview */}
              <div className="rounded-lg border border-zinc-800/50 bg-zinc-950/50 p-4">
                <div className="mb-3 flex items-center gap-2">
                  <div className="flex size-7 items-center justify-center rounded-md bg-gradient-to-br from-emerald-500 to-teal-600">
                    <TrendingDown className="size-3.5 text-white" />
                  </div>
                  <span className="text-sm font-medium text-zinc-300">Price Tracking</span>
                </div>
                <div className="space-y-2">
                  <div className="flex items-center justify-between rounded-md bg-zinc-800/30 px-3 py-2">
                    <span className="text-xs text-zinc-400">AirPods Pro 2</span>
                    <span className="text-xs font-medium text-emerald-400">$189</span>
                  </div>
                  <div className="flex items-center justify-between rounded-md bg-zinc-800/30 px-3 py-2">
                    <span className="text-xs text-zinc-400">Sony WH-1000XM5</span>
                    <span className="text-xs font-medium text-amber-400">$278</span>
                  </div>
                  <div className="flex items-center justify-between rounded-md bg-zinc-800/30 px-3 py-2">
                    <span className="text-xs text-zinc-400">iPad Air M2</span>
                    <span className="text-xs font-medium text-emerald-400">$549</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          {/* Glow effect under mockup */}
          <div className="absolute -bottom-8 left-1/2 h-16 w-3/4 -translate-x-1/2 rounded-full bg-emerald-500/10 blur-3xl" />
        </div>
      </section>

      {/* Features */}
      <section className="relative border-t border-zinc-800/50 px-4 py-20 sm:py-28">
        <div className="mx-auto max-w-7xl">
          <div className="mb-14 text-center">
            <h3 className="mb-3 text-3xl font-bold tracking-tight text-white sm:text-4xl">
              Everything you need to
              <span className="bg-gradient-to-r from-emerald-400 to-teal-400 bg-clip-text text-transparent"> save money</span>
            </h3>
            <p className="mx-auto max-w-xl text-zinc-400">
              Powered by AI that does the hard work so you don&apos;t have to.
            </p>
          </div>

          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {features.map((feature) => (
              <div
                key={feature.title}
                className="group rounded-xl border border-zinc-800/50 bg-zinc-900/30 p-6 transition-colors hover:border-zinc-700/50 hover:bg-zinc-900/50"
              >
                <div className={`mb-4 flex size-11 items-center justify-center rounded-lg bg-gradient-to-br ${feature.gradient} shadow-lg`}>
                  <feature.icon className="size-5 text-white" />
                </div>
                <h4 className="mb-2 text-base font-semibold text-white">{feature.title}</h4>
                <p className="text-sm leading-relaxed text-zinc-400">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Bottom CTA */}
      <section className="relative border-t border-zinc-800/50 px-4 py-20">
        <div className="mx-auto max-w-2xl text-center">
          <h3 className="mb-4 text-2xl font-bold text-white sm:text-3xl">
            Ready to find better deals?
          </h3>
          <p className="mb-8 text-zinc-400">
            Try the demo and see how DealHunter AI can save you money.
          </p>
          <Button asChild size="lg" className="bg-gradient-to-r from-emerald-500 to-teal-600 text-white shadow-lg shadow-emerald-500/25 hover:from-emerald-600 hover:to-teal-700">
            <Link href="/app">
              Try the Demo
              <ArrowRight className="size-4" />
            </Link>
          </Button>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-zinc-800/50 px-4 py-8">
        <div className="mx-auto flex max-w-7xl items-center justify-between">
          <div className="flex items-center gap-2">
            <Target className="size-4 text-emerald-500" />
            <span className="text-sm text-zinc-500">DealHunter AI</span>
          </div>
          <span className="text-xs text-zinc-600">AI-powered price intelligence</span>
        </div>
      </footer>
    </div>
  )
}
