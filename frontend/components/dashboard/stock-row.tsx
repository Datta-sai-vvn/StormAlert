import React from "react"
import { Sparkline } from "@/components/dashboard/sparkline"

interface StockData {
    symbol: string
    token: number
    price: number
    change: number
    history: number[]
}

interface StockRowProps {
    stock: StockData
}

export const StockRow = React.memo(function StockRow({ stock }: StockRowProps) {
    return (
        <tr className="border-b hover:bg-gray-50">
            <td className="px-4 py-3 font-medium">{stock.symbol}</td>
            <td className="px-4 py-3 font-mono">₹{stock.price.toFixed(2)}</td>
            <td className="px-4 py-3">
                <Sparkline data={stock.history} width={100} height={30} />
            </td>
            <td className={`px-4 py-3 font-bold ${stock.change > 0 ? "text-green-600" : "text-red-600"}`}>
                {stock.change > 0 ? "+" : ""}{stock.change}%
            </td>
        </tr>
    )
})
