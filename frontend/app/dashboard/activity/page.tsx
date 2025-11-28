"use client"
// Force rebuild


import { useEffect, useState } from "react"
import api from "@/lib/api"
import { ActivityFilters } from "@/components/activity/activity-filters"
import { ActivityTable } from "@/components/activity/activity-table"
import { ActivityStats } from "@/components/activity/activity-stats"
import { AlertDrawer } from "@/components/activity/alert-drawer"
import { Button } from "@/components/ui/button"
import { Download, RefreshCw } from "lucide-react"
import { useToast } from "@/components/ui/use-toast"

export default function ActivityPage() {
    const { toast } = useToast()
    const [logs, setLogs] = useState<any[]>([])
    const [stats, setStats] = useState(null)
    const [loading, setLoading] = useState(true)
    const [filters, setFilters] = useState({})
    const [selectedLog, setSelectedLog] = useState(null)
    const [drawerOpen, setDrawerOpen] = useState(false)
    useEffect(() => {
        // WebSocket for Real-Time Logs
        const socket = new WebSocket("ws://localhost:8002/ws/stocks")

        socket.onopen = () => {
            console.log("Activity WS Connected")
        }

        socket.onmessage = (event) => {
            try {
                const message = JSON.parse(event.data)
                if (message.type === "ALERT_NEW") {
                    const newLog = message.data
                    // Prepend new log to state
                    setLogs(prev => [newLog, ...prev])
                    // Optional: Show toast
                    toast({
                        title: "New Alert",
                        description: `${newLog.stock_symbol}: ${newLog.change_percent.toFixed(2)}% ${newLog.alert_type}`,
                    })
                }
            } catch (e) {
                console.error("WS Error", e)
            }
        }

        return () => socket.close()
    }, [])

    const fetchData = async () => {
        setLoading(true)
        try {
            // Build query string
            const params = new URLSearchParams()
            if ((filters as any).search) params.append("symbol", (filters as any).search)
            if ((filters as any).type && (filters as any).type !== "all") params.append("alert_type", (filters as any).type)

            const [logsRes, statsRes] = await Promise.all([
                api.get(`/activity/list?${params.toString()}`),
                api.get("/activity/stats")
            ])

            setLogs(logsRes.data)
            setStats(statsRes.data)
        } catch (error) {
            console.error("Failed to fetch activity", error)
            toast({ title: "Error", description: "Failed to load activity logs" })
        } finally {
            setLoading(false)
        }
    }

    const handleDelete = async (id: string) => {
        try {
            await api.delete(`/activity/${id}`)
            setLogs(logs.filter((l: any) => l._id !== id))
            toast({ title: "Deleted", description: "Log entry deleted" })
        } catch (error) {
            toast({ title: "Error", description: "Failed to delete log" })
        }
    }

    const handleExport = async () => {
        try {
            const response = await api.get("/activity/export", { responseType: "blob" })
            const url = window.URL.createObjectURL(new Blob([response.data]))
            const link = document.createElement("a")
            link.href = url
            link.setAttribute("download", "activity_logs.csv")
            document.body.appendChild(link)
            link.click()
            link.remove()
        } catch (error) {
            toast({ title: "Error", description: "Failed to export logs" })
        }
    }

    return (
        <div className="space-y-6 pb-10">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900">Activity Logs</h1>
                    <p className="text-muted-foreground">Real-time history of all system alerts and events.</p>
                </div>
                <div className="flex gap-2">
                    <Button variant="outline" onClick={fetchData}>
                        <RefreshCw className={`mr-2 h-4 w-4 ${loading ? "animate-spin" : ""}`} />
                        Refresh
                    </Button>
                    <Button variant="outline" onClick={handleExport}>
                        <Download className="mr-2 h-4 w-4" />
                        Export CSV
                    </Button>
                </div>
            </div>

            <ActivityStats stats={stats} />

            <ActivityFilters onFilterChange={setFilters} />

            <ActivityTable
                logs={logs}
                onDelete={handleDelete}
                onView={(log) => {
                    setSelectedLog(log)
                    setDrawerOpen(true)
                }}
            />

            <AlertDrawer
                log={selectedLog}
                open={drawerOpen}
                onClose={() => setDrawerOpen(false)}
            />
        </div>
    )
}
