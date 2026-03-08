"use client"

import { useEffect, useCallback, useRef } from "react"
import { driver, type DriveStep } from "driver.js"
import "driver.js/dist/driver.css"

const TOUR_COMPLETED_KEY = "tourCompleted"

const tourSteps: DriveStep[] = [
  {
    element: "#chat-input",
    popover: {
      title: "Chat with AI",
      description:
        "Type a message to track a product, like 'Track Samsung TV under $900'",
      side: "top",
      align: "center",
    },
  },
  {
    element: "#tracked-items",
    popover: {
      title: "Tracked Items",
      description:
        "Products you track appear here with current prices",
      side: "left",
      align: "start",
    },
  },
  {
    element: "#simulate-button",
    popover: {
      title: "Simulate Price Drop",
      description:
        "Click here to simulate a price drop",
      side: "bottom",
      align: "center",
    },
  },
  {
    element: "#price-alerts",
    popover: {
      title: "Price Alerts",
      description:
        "When prices drop, alerts show up here with savings info",
      side: "left",
      align: "start",
    },
  },
  {
    element: "#analytics-summary",
    popover: {
      title: "Analytics Summary",
      description:
        "See your tracking stats at a glance",
      side: "bottom",
      align: "center",
    },
  },
]

interface DemoTourProps {
  startTour?: boolean
  onTourStart?: () => void
  onTourEnd?: () => void
}

export function DemoTour({ startTour, onTourStart, onTourEnd }: DemoTourProps) {
  const driverRef = useRef<ReturnType<typeof driver> | null>(null)
  const hasAutoStarted = useRef(false)

  const markTourCompleted = useCallback(() => {
    localStorage.setItem(TOUR_COMPLETED_KEY, "true")
    onTourEnd?.()
  }, [onTourEnd])

  const initAndStart = useCallback(() => {
    // Destroy any previous instance
    if (driverRef.current) {
      driverRef.current.destroy()
    }

    const driverInstance = driver({
      showProgress: true,
      animate: true,
      overlayColor: "rgba(0, 0, 0, 0.75)",
      stagePadding: 8,
      stageRadius: 12,
      popoverClass: "dealhunter-tour-popover",
      nextBtnText: "Next",
      prevBtnText: "Back",
      doneBtnText: "Done",
      steps: tourSteps,
      onDestroyStarted: () => {
        markTourCompleted()
        driverInstance.destroy()
      },
      onDestroyed: () => {
        markTourCompleted()
      },
    })

    driverRef.current = driverInstance
    onTourStart?.()
    driverInstance.drive()
  }, [markTourCompleted, onTourStart])

  // Auto-start for first-time visitors
  useEffect(() => {
    if (hasAutoStarted.current) return
    hasAutoStarted.current = true

    const tourCompleted = localStorage.getItem(TOUR_COMPLETED_KEY)
    if (!tourCompleted) {
      // Small delay to let page elements render
      const timeout = setTimeout(() => {
        initAndStart()
      }, 1000)
      return () => clearTimeout(timeout)
    }
  }, [initAndStart])

  // Manual start via prop
  useEffect(() => {
    if (startTour) {
      initAndStart()
    }
  }, [startTour, initAndStart])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (driverRef.current) {
        driverRef.current.destroy()
      }
    }
  }, [])

  return null
}
