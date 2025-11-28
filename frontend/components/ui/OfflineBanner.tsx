"use client"

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { AlertCircle } from "lucide-react"
import { useSystemStatus } from "@/contexts/SystemStatusContext"

export function OfflineBanner() {
    const { status } = useSystemStatus()

    if (status === "ONLINE") return null

    return (
        <div className="w-full bg-destructive/15 p-4 border-b border-destructive/20">
            <div className="container mx-auto flex items-center gap-2 text-destructive">
                <AlertCircle className="h-5 w-5" />
                <span className="font-semibold">System Offline — Waiting for Admin Token</span>
                <span className="ml-auto text-sm opacity-80">Real-time data unavailable</span>
            </div>
        </div>
    )
}
