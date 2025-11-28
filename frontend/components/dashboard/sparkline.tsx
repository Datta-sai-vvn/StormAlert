import React from "react"

interface SparklineProps {
    data: number[]
    color?: string
    width?: number
    height?: number
}

export const Sparkline = React.memo(function Sparkline({ data, color = "green", width = 100, height = 30 }: SparklineProps) {
    if (!data || data.length < 2) return null

    const min = Math.min(...data)
    const max = Math.max(...data)
    const range = max - min || 1

    const points = data.map((val, i) => {
        const x = (i / (data.length - 1)) * width
        const y = height - ((val - min) / range) * height
        return `${x},${y}`
    }).join(" ")

    const isUp = data[data.length - 1] >= data[0]
    const strokeColor = isUp ? "#16a34a" : "#dc2626" // green-600 : red-600

    return (
        <svg width={width} height={height} className="overflow-visible">
            <polyline
                points={points}
                fill="none"
                stroke={strokeColor}
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
            />
            {/* Last point dot */}
            <circle
                cx={(data.length - 1) / (data.length - 1) * width}
                cy={height - ((data[data.length - 1] - min) / range) * height}
                r="2"
                fill={strokeColor}
            />
        </svg>
    )
})
