"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"

export default function AuthCallback() {
  const router = useRouter()
  useEffect(() => { router.replace("/app") }, [router])
  return (
    <div className="flex min-h-screen items-center justify-center bg-zinc-950">
      <div className="size-8 animate-spin rounded-full border-2 border-zinc-700 border-t-emerald-500" />
    </div>
  )
}
