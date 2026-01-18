"use client"

import { Input } from "@/components/ui/input"
import { cn } from "@/lib/utils"

interface EmailInputProps {
  value: string
  onChange: (email: string) => void
  className?: string
}

export function EmailInput({ value, onChange, className }: EmailInputProps) {
  return (
    <Input
      type="email"
      placeholder="your@email.com"
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className={cn("bg-zinc-800/50 border-zinc-700 text-white placeholder:text-zinc-500", className)}
    />
  )
}
