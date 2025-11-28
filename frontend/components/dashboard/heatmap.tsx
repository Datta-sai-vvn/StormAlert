import React from "react"

interface HeatmapItem {
    token: number
    symbol: string
    change: number
}

interface HeatmapProps {
    data: HeatmapItem[]
}

export const Heatmap = React.memo(function Heatmap({ data }: HeatmapProps) {
    const getColor = (change: number) => {
        if (change > 2) return "bg-green-600"
        if (change > 1) return "bg-green-500"
        if (change > 0) return "bg-green-400"
        if (change === 0) return "bg-gray-400"
        if (change > -1) return "bg-red-400"
        if (change > -2) return "bg-red-500"
        return "bg-red-600"
    }

    return (
        <div className="grid grid-cols-4 sm:grid-cols-6 md:grid-cols-8 gap-1">
            {data.map((item) => (
                <div
                    key={item.token}
                    className={`${getColor(item.change)} h-16 flex flex-col items-center justify-center text-white rounded p-1 transition-colors duration-300`}
                    title={`${item.symbol}: ${item.change}%`}
                >
                    <span className="text-xs font-bold truncate w-full text-center">{item.symbol}</span>
                    <span className="text-xs">{item.change > 0 ? "+" : ""}{item.change}%</span>
                </div>
            ))}
            {data.length === 0 && (
                <div className="col-span-full text-center text-gray-400 py-4 text-sm">
                    No data available for heatmap
                </div>
            )}
        </div>
    )
})
