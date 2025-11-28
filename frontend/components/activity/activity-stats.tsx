"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from "recharts"
import { useEffect, useState } from "react"

interface ActivityStatsProps {
    stats: any
}

export function ActivityStats({ stats }: ActivityStatsProps) {
    const [mounted, setMounted] = useState(false)

    useEffect(() => {
        setMounted(true)
    }, [])

    if (!stats) return null
    if (!mounted) return null

    return (
        <div className="grid gap-4 md:grid-cols-3 mb-6">
            <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Total Alerts</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="text-2xl font-bold">{stats.total_alerts}</div>
                    <p className="text-xs text-muted-foreground">All time alerts generated</p>
                </CardContent>
            </Card>

            <Card className="col-span-2">
                <CardHeader>
                    <CardTitle className="text-sm font-medium">Top Alerted Stocks</CardTitle>
                </CardHeader>
                <CardContent className="h-[150px]">
                    <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={stats.top_stocks}>
                            <XAxis dataKey="symbol" fontSize={12} tickLine={false} axisLine={false} />
                            <YAxis fontSize={12} tickLine={false} axisLine={false} />
                            <Tooltip
                                contentStyle={{ background: "#fff", border: "1px solid #eee", borderRadius: "8px" }}
                                cursor={{ fill: "transparent" }}
                            />
                            <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                                {stats.top_stocks.map((entry: any, index: number) => (
                                    <Cell key={`cell-${index}`} fill={index % 2 === 0 ? "#2563eb" : "#64748b"} />
                                ))}
                            </Bar>
                        </BarChart>
                    </ResponsiveContainer>
                </CardContent>
            </Card>
        </div>
    )
}
