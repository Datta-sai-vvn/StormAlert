"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

interface Alert {
    _id: string
    type: 'DIP' | 'SPIKE'
    token: number
    percent: number
    price: number
    timestamp: number
    created_at: string
}

export function AlertList() {
    const [alerts, setAlerts] = useState<Alert[]>([])

    useEffect(() => {
        const fetchAlerts = async () => {
            try {
                const res = await fetch("/api/alerts?limit=10")
                if (res.ok) {
                    const data = await res.json()
                    setAlerts(data)
                }
            } catch (e) {
                console.error("Failed to fetch alerts", e)
            }
        }

        fetchAlerts()
        const interval = setInterval(fetchAlerts, 5000)
        return () => clearInterval(interval)
    }, [])

    return (
        <Card>
            <CardHeader>
                <CardTitle>Recent Alerts</CardTitle>
            </CardHeader>
            <CardContent>
                <div className="h-[300px] overflow-y-auto pr-2">
                    <div className="space-y-4">
                        {alerts.map((alert) => (
                            <div key={alert._id} className="flex items-center justify-between border-b pb-2 last:border-0">
                                <div>
                                    <div className="flex items-center gap-2">
                                        <Badge variant={alert.type === 'SPIKE' ? 'default' : 'destructive'}>
                                            {alert.type}
                                        </Badge>
                                        <span className="font-mono text-sm text-gray-500">
                                            {new Date(alert.timestamp).toLocaleTimeString()}
                                        </span>
                                    </div>
                                    <p className="text-xs text-muted-foreground mt-1">
                                        Token: {alert.token}
                                    </p>
                                </div>
                                <div className="text-right">
                                    <div className="font-bold">
                                        {alert.percent.toFixed(2)}%
                                    </div>
                                    <div className="text-xs text-gray-500">
                                        ₹{alert.price.toFixed(2)}
                                    </div>
                                </div>
                            </div>
                        ))}
                        {alerts.length === 0 && (
                            <p className="text-center text-sm text-gray-500 py-4">No alerts yet.</p>
                        )}
                    </div>
                </div>
            </CardContent>
        </Card>
    )
}
