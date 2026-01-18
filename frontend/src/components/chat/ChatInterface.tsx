"use client"

import { useState, useRef, useEffect, FormEvent } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Send, Sparkles, User, Loader2, Wifi, WifiOff, RefreshCw } from "lucide-react"
import { cn } from "@/lib/utils"
import { toast } from "sonner"

interface Message {
  id: string
  role: "user" | "assistant"
  content: string
  isError?: boolean
}

type ConnectionStatus = "idle" | "connecting" | "connected" | "error" | "reconnecting"

const EXAMPLE_PROMPTS = [
  'Track Samsung 65" TV under $900',
  "Show me laptop deals under $1500",
  "What am I tracking?",
]

const getApiUrl = () => {
  if (process.env.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL
  }
  if (typeof window !== "undefined") {
    return `http://${window.location.hostname}:8000`
  }
  return "http://localhost:8000"
}

interface ChatInterfaceProps {
  onMessageComplete?: () => void
}

// Connection status indicator component
function ConnectionIndicator({ status }: { status: ConnectionStatus }) {
  if (status === "idle" || status === "connected") return null

  const config = {
    connecting: {
      icon: <Loader2 className="size-3 animate-spin" />,
      text: "Connecting to server...",
      className: "bg-amber-500/20 text-amber-400 border-amber-500/30",
    },
    reconnecting: {
      icon: <RefreshCw className="size-3 animate-spin" />,
      text: "Reconnecting...",
      className: "bg-amber-500/20 text-amber-400 border-amber-500/30",
    },
    error: {
      icon: <WifiOff className="size-3" />,
      text: "Connection issue",
      className: "bg-red-500/20 text-red-400 border-red-500/30",
    },
  }[status]

  if (!config) return null

  return (
    <div
      className={cn(
        "flex items-center gap-2 rounded-full border px-3 py-1.5 text-xs font-medium transition-all animate-in fade-in slide-in-from-top-2",
        config.className
      )}
    >
      {config.icon}
      <span>{config.text}</span>
    </div>
  )
}

export function ChatInterface({ onMessageComplete }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>("idle")
  const scrollRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)
  const retryTimeoutRef = useRef<NodeJS.Timeout | null>(null)

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [messages])

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (retryTimeoutRef.current) {
        clearTimeout(retryTimeoutRef.current)
      }
    }
  }, [])

  const handleSubmit = async (e: FormEvent, retryMessage?: string) => {
    e?.preventDefault?.()
    const messageContent = retryMessage || input.trim()
    if (!messageContent || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: messageContent,
    }

    // Only add user message if not a retry
    if (!retryMessage) {
      setMessages((prev) => [...prev, userMessage])
      setInput("")
    }

    setIsLoading(true)
    setConnectionStatus(messages.length === 0 ? "connecting" : "connected")

    // Create placeholder for assistant message
    const assistantId = (Date.now() + 1).toString()
    setMessages((prev) => [
      ...prev,
      { id: assistantId, role: "assistant", content: "" },
    ])

    try {
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), 30000) // 30s timeout for Railway cold start

      const response = await fetch(`${getApiUrl()}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: userMessage.content,
          session_id: "demo-session",
        }),
        signal: controller.signal,
      })

      clearTimeout(timeoutId)

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`)
      }

      setConnectionStatus("connected")

      const reader = response.body?.getReader()
      const decoder = new TextDecoder()

      if (!reader) throw new Error("No response body")

      let fullContent = ""

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value)
        const lines = chunk.split("\n")

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            try {
              const data = JSON.parse(line.slice(6))

              if (data.type === "text") {
                fullContent += data.content
                setMessages((prev) =>
                  prev.map((msg) =>
                    msg.id === assistantId
                      ? { ...msg, content: fullContent }
                      : msg
                  )
                )
              } else if (data.type === "done") {
                // Stream complete
              } else if (data.type === "error") {
                fullContent = data.message || "An error occurred"
                setMessages((prev) =>
                  prev.map((msg) =>
                    msg.id === assistantId
                      ? { ...msg, content: fullContent, isError: true }
                      : msg
                  )
                )
              }
            } catch {
              // Ignore parse errors for incomplete chunks
            }
          }
        }
      }
      onMessageComplete?.()
    } catch (error) {
      console.error("Chat error:", error)
      const isAbort = error instanceof Error && error.name === "AbortError"
      const isNetworkError = error instanceof TypeError && error.message.includes("fetch")

      let errorMessage: string
      let shouldRetry = false

      if (isAbort) {
        errorMessage = "The server is taking a while to respond. It might be waking up from sleep."
        shouldRetry = true
        setConnectionStatus("reconnecting")
      } else if (isNetworkError) {
        errorMessage = "Unable to reach the server. Please check your connection."
        setConnectionStatus("error")
      } else {
        errorMessage = "Something went wrong. Please try again."
        setConnectionStatus("error")
      }

      // Update the assistant message with error
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === assistantId
            ? {
                ...msg,
                content: errorMessage,
                isError: true,
              }
            : msg
        )
      )

      // Show toast for errors
      toast.error("Message failed", {
        description: shouldRetry
          ? "The server may be starting up. Try again in a moment."
          : "Check your connection and try again.",
      })

      // Auto-retry once for timeout errors
      if (shouldRetry) {
        retryTimeoutRef.current = setTimeout(() => {
          setConnectionStatus("idle")
        }, 5000)
      }
    } finally {
      setIsLoading(false)
      // Reset connection status after a delay if connected
      setTimeout(() => {
        setConnectionStatus((prev) => (prev === "connected" ? "idle" : prev))
      }, 2000)
    }
  }

  const handleExampleClick = (prompt: string) => {
    setInput(prompt)
    inputRef.current?.focus()
  }

  return (
    <div className="flex h-full flex-col">
      {/* Connection status indicator */}
      <div className="absolute right-4 top-4 z-10">
        <ConnectionIndicator status={connectionStatus} />
      </div>

      {/* Messages area */}
      <div className="flex-1 overflow-y-auto p-4" ref={scrollRef}>
        <div className="space-y-4">
          {/* Welcome message if no messages */}
          {messages.length === 0 && (
            <div className="flex gap-3">
              <div className="flex size-8 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-emerald-500 to-teal-600 shadow-lg shadow-emerald-500/20">
                <Sparkles className="size-4 text-white" />
              </div>
              <div className="rounded-2xl rounded-tl-sm bg-zinc-800/50 px-4 py-3 backdrop-blur-sm">
                <p className="text-sm text-zinc-300">
                  Hey! I&apos;m your DealHunter AI assistant. Try one of these:
                </p>
                <div className="mt-3 flex flex-wrap gap-2">
                  {EXAMPLE_PROMPTS.map((prompt) => (
                    <button
                      key={prompt}
                      onClick={() => handleExampleClick(prompt)}
                      className="rounded-full border border-zinc-700/50 bg-zinc-800/80 px-3 py-1.5 text-xs text-zinc-300 transition-all hover:border-emerald-500/50 hover:bg-zinc-700 hover:text-white hover:shadow-md hover:shadow-emerald-500/10"
                    >
                      {prompt}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Message list */}
          {messages.map((message, index) => (
            <div
              key={message.id}
              className={cn(
                "flex gap-3 animate-in fade-in slide-in-from-bottom-2 duration-300",
                message.role === "user" && "flex-row-reverse"
              )}
              style={{ animationDelay: `${index * 50}ms` }}
            >
              <div
                className={cn(
                  "flex size-8 shrink-0 items-center justify-center rounded-full shadow-lg",
                  message.role === "assistant"
                    ? message.isError
                      ? "bg-gradient-to-br from-red-500 to-rose-600 shadow-red-500/20"
                      : "bg-gradient-to-br from-emerald-500 to-teal-600 shadow-emerald-500/20"
                    : "bg-gradient-to-br from-violet-500 to-purple-600 shadow-violet-500/20"
                )}
              >
                {message.role === "assistant" ? (
                  message.isError ? (
                    <WifiOff className="size-4 text-white" />
                  ) : (
                    <Sparkles className="size-4 text-white" />
                  )
                ) : (
                  <User className="size-4 text-white" />
                )}
              </div>
              <div
                className={cn(
                  "max-w-[80%] rounded-2xl px-4 py-3 backdrop-blur-sm",
                  message.role === "assistant"
                    ? message.isError
                      ? "rounded-tl-sm border border-red-500/20 bg-red-500/10"
                      : "rounded-tl-sm bg-zinc-800/50"
                    : "rounded-tr-sm bg-gradient-to-r from-violet-500/20 to-purple-600/20 border border-violet-500/20"
                )}
              >
                <p
                  className={cn(
                    "whitespace-pre-wrap text-sm",
                    message.isError ? "text-red-300" : "text-zinc-300"
                  )}
                >
                  {message.content || (
                    <span className="flex items-center gap-2 text-zinc-500">
                      <Loader2 className="size-4 animate-spin" />
                      <span className="animate-pulse">Thinking...</span>
                    </span>
                  )}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Input area */}
      <div className="border-t border-zinc-800/50 bg-zinc-900/30 p-4 backdrop-blur-sm">
        <form onSubmit={handleSubmit} className="flex gap-2">
          <Input
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask me to track a product or find deals..."
            className="flex-1 border-zinc-700 bg-zinc-800/50 text-white placeholder:text-zinc-500 focus-visible:border-emerald-500/50 focus-visible:ring-emerald-500/20"
            disabled={isLoading}
          />
          <Button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="bg-gradient-to-r from-emerald-500 to-teal-600 text-white shadow-lg shadow-emerald-500/20 transition-all hover:from-emerald-600 hover:to-teal-700 hover:shadow-emerald-500/30 disabled:opacity-50 disabled:shadow-none"
          >
            {isLoading ? (
              <Loader2 className="size-4 animate-spin" />
            ) : (
              <Send className="size-4" />
            )}
          </Button>
        </form>
      </div>
    </div>
  )
}
