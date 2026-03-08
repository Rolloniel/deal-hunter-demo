"use client"

import { Target, Zap, LogOut, HelpCircle } from "lucide-react"
import { Button } from "@/components/ui/button"
import { useAuth } from "@/components/providers/AuthProvider"

interface HeaderProps {
  onStartTour?: () => void
}

export function Header({ onStartTour }: HeaderProps) {
  const { user, signOut } = useAuth()

  const displayName = user?.email?.split("@")[0] || "User"

  return (
    <header className="relative border-b border-zinc-800/50 bg-zinc-950/80 backdrop-blur-xl">
      {/* Subtle gradient accent line at top */}
      <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-emerald-500/50 to-transparent" />

      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        {/* Logo & Brand */}
        <div className="flex items-center gap-3">
          <div className="relative flex size-10 items-center justify-center rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600 shadow-lg shadow-emerald-500/20">
            <Target className="size-5 text-white" strokeWidth={2.5} />
            {/* Glow effect */}
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

        {/* User info & sign out */}
        <div className="flex items-center gap-3">
          {onStartTour && (
            <Button
              id="tour-button"
              variant="ghost"
              onClick={onStartTour}
              className="flex items-center gap-1.5 rounded-full border border-zinc-800 bg-zinc-900/50 px-3 py-1.5 text-xs font-medium text-zinc-400 hover:border-emerald-500/50 hover:text-emerald-400"
            >
              <HelpCircle className="size-3.5" />
              <span className="hidden sm:inline">Take a Tour</span>
            </Button>
          )}

          <div className="flex items-center gap-2 rounded-full border border-zinc-800 bg-zinc-900/50 px-3 py-1.5">
            <div className="relative flex size-2">
              <span className="absolute inline-flex size-full animate-ping rounded-full bg-emerald-400 opacity-75" />
              <span className="relative inline-flex size-2 rounded-full bg-emerald-500" />
            </div>
            <span className="text-xs font-medium text-zinc-400">
              <Zap className="mr-1 inline size-3 text-emerald-500" />
              Tracking Active
            </span>
          </div>

          {user && (
            <div className="flex items-center gap-2">
              <div className="flex items-center gap-2 rounded-full border border-zinc-800 bg-zinc-900/50 px-3 py-1.5">
                <div className="flex size-5 items-center justify-center rounded-full bg-gradient-to-br from-violet-500 to-purple-600 text-[10px] font-bold text-white">
                  {displayName.charAt(0).toUpperCase()}
                </div>
                <span className="hidden text-xs font-medium text-zinc-300 sm:inline">
                  {displayName}
                </span>
              </div>
              <Button
                variant="ghost"
                size="icon"
                onClick={signOut}
                className="size-8 text-zinc-400 hover:text-white"
                title="Sign out"
              >
                <LogOut className="size-4" />
              </Button>
            </div>
          )}
        </div>
      </div>
    </header>
  )
}
