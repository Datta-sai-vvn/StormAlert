"use client"

import React, { createContext, useContext, useState, useEffect } from "react"

interface SystemStatusContextType {
    status: "ONLINE" | "OFFLINE"
    loading: boolean
    refreshStatus: () => void
}

const SystemStatusContext = createContext<SystemStatusContextType | undefined>(undefined)

export function SystemStatusProvider({ children }: { children: React.ReactNode }) {
    const [status, setStatus] = useState<"ONLINE" | "OFFLINE">("OFFLINE")
    const [loading, setLoading] = useState(true)

    const fetchStatus = async () => {
        try {
            const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8002/api'}/admin/system-status`)
            if (res.ok) {
                const data = await res.json()
                setStatus(data.status)
            }
        } catch (e) {
            console.error("Failed to fetch system status", e)
            setStatus("OFFLINE")
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        fetchStatus()
        const interval = setInterval(fetchStatus, 30000) // Poll every 30s
        return () => clearInterval(interval)
    }, [])

    return (
        <SystemStatusContext.Provider value={{ status, loading, refreshStatus: fetchStatus }}>
            {children}
        </SystemStatusContext.Provider>
    )
}

export const useSystemStatus = () => {
    const context = useContext(SystemStatusContext)
    if (context === undefined) {
        throw new Error("useSystemStatus must be used within a SystemStatusProvider")
    }
    return context
}
