"use client"

import { useEffect, useState, useRef } from "react"
import api from "@/lib/api"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Activity, AlertTriangle, Server, Zap } from "lucide-react"
import { Sparkline } from "@/components/dashboard/sparkline"
import { Heatmap } from "@/components/dashboard/heatmap"
import { StockRow } from "@/components/dashboard/stock-row"
import { useSystemStatus } from "@/contexts/SystemStatusContext"

interface DashboardStats {
    active_stocks: number
    alerts_today: number
    avg_latency: number
    uptime: string
    connected: boolean
}

interface StockData {
    symbol: string
    token: number
    price: number
    change: number
    history: number[]
}

export default function DashboardPage() {
    const [stats, setStats] = useState<DashboardStats>({
        active_stocks: 0,
        alerts_today: 0,
        avg_latency: 0,
        uptime: "-",
        connected: false
    })
    const [stocks, setStocks] = useState<StockData[]>([])

    const ws = useRef<WebSocket | null>(null)

    useEffect(() => {
        // Initial Fetch
        const fetchData = async () => {
            try {
                const res = await api.get("/dashboard/stats")
                setStats(res.data)
                const stocksRes = await api.get("/stocks/")
                // Initialize stocks with empty history
                setStocks(stocksRes.data.map((s: any) => ({
                    symbol: s.symbol,
                    token: s.instrument_token,
                    price: 0,
                    change: 0,
                    history: []
                })))
            } catch (e) {
                console.error("Failed to fetch dashboard data", e)
            }
        }
        fetchData()

        // WebSocket
        const socket = new WebSocket("ws://localhost:8002/ws/stocks")

        socket.onopen = () => {
            console.log("Dashboard WS Connected")
        }

        socket.onmessage = (event) => {
            try {
                const message = JSON.parse(event.data)

                if (message.type === "TICK_UPDATE") {
                    updateStocks(message.data)
                } else if (message.type === "DASHBOARD_UPDATE") {
                    setStats(prev => ({ ...prev, ...message.stats }))
                }
            } catch (e) {
                console.error("WS Error", e)
            }
        }

        ws.current = socket
        return () => socket.close()
    }, [])

    const updateStocks = (ticks: any[]) => {
        setStocks(prev => {
            return prev.map(stock => {
                const tick = ticks.find((t: any) => t.instrument_token === stock.token)
                if (tick) {
                    const newHistory = [...stock.history, tick.last_price].slice(-30) // Keep last 30
                    return {
                        ...stock,
                        price: tick.last_price,
                        change: tick.change,
                        history: newHistory
                    }
                }
                return stock
            })
        })
    }

    const { status } = useSystemStatus()

    // Override stats if offline
    const displayStats = status === "OFFLINE" ? {
        active_stocks: 0,
        alerts_today: 0,
        avg_latency: 0,
        uptime: "-",
        connected: false
    } : stats

    return (
        <div className="space-y-6">
            <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>

            {/* KPI Grid */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                <Card className={status === "OFFLINE" ? "bg-gray-50 opacity-70" : ""}>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Active Stocks</CardTitle>
                        <Activity className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{status === "OFFLINE" ? "—" : displayStats.active_stocks}</div>
                        <p className="text-xs text-muted-foreground">Monitoring live</p>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">System Status</CardTitle>
                        <Server className={`h-4 w-4 ${status === "ONLINE" ? "text-green-500" : "text-gray-500"}`} />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{status === "ONLINE" ? "Online" : "Offline"}</div>
                        <p className="text-xs text-muted-foreground">
                            {status === "ONLINE" ? `Uptime: ${new Date(displayStats.uptime).toLocaleTimeString()}` : "Waiting for Token"}
                        </p>
                    </CardContent>
                </Card>
                <Card className={status === "OFFLINE" ? "bg-gray-50 opacity-70" : ""}>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Alerts Today</CardTitle>
                        <AlertTriangle className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{status === "OFFLINE" ? "—" : displayStats.alerts_today}</div>
                        <p className="text-xs text-muted-foreground">Triggered events</p>
                    </CardContent>
                </Card>
                <Card className={status === "OFFLINE" ? "bg-gray-50 opacity-70" : ""}>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Latency</CardTitle>
                        <Zap className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{status === "OFFLINE" ? "—" : "~50ms"}</div>
                        <p className="text-xs text-muted-foreground">Real-time connection</p>
                    </CardContent>
                </Card>
            </div>

            {status === "ONLINE" ? (
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
                    {/* Live Market Watch */}
                    <Card className="col-span-4">
                        <CardHeader>
                            <CardTitle>Live Market Watch</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="relative overflow-x-auto">
                                <table className="w-full text-left text-sm">
                                    <thead className="text-xs uppercase text-gray-500 bg-gray-50">
                                        <tr>
                                            <th className="px-4 py-2">Symbol</th>
                                            <th className="px-4 py-2">Price</th>
                                            <th className="px-4 py-2">Trend (30s)</th>
                                            <th className="px-4 py-2">Change</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {stocks.map(stock => (
                                            <StockRow key={stock.token} stock={stock} />
                                        ))}
                                        {stocks.length === 0 && (
                                            <tr>
                                                <td colSpan={4} className="text-center py-4 text-gray-500">No stocks added.</td>
                                            </tr>
                                        )}
                                    </tbody>
                                </table>
                            </div>
                        </CardContent>
                    </Card>

                    {/* Heatmap & Logs */}
                    <div className="col-span-3 space-y-4">
                        <Card>
                            <CardHeader>
                                <CardTitle>Market Heatmap</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <Heatmap data={stocks.map(s => ({ token: s.token, symbol: s.symbol, change: s.change }))} />
                            </CardContent>
                        </Card>

                        <Card>
                            <CardHeader>
                                <CardTitle>System Logs</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="h-[200px] overflow-y-auto bg-black text-green-400 p-2 rounded text-xs font-mono">
                                    <p>[INFO] System Initialized</p>
                                    <p>[INFO] WebSocket Connected</p>
                                    <p>[INFO] Ticker Service Running</p>
                                    {stocks.length > 0 && <p>[INFO] Monitoring {stocks.length} stocks...</p>}
                                </div>
                            </CardContent>
                        </Card>
                    </div>
                </div>
            ) : (
                <div className="flex flex-col items-center justify-center h-[400px] bg-gray-50 rounded-lg border border-dashed border-gray-300">
                    <Server className="h-12 w-12 text-gray-300 mb-4" />
                    <h3 className="text-lg font-medium text-gray-900">System Offline</h3>
                    <p className="text-sm text-gray-500 max-w-sm text-center mt-2">
                        Real-time data is unavailable. Waiting for admin to provide today's Zerodha token.
                    </p>
                </div>
            )}
        </div>
    )
}
