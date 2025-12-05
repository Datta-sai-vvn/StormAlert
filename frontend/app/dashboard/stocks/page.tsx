"use client"

import { useEffect, useState, useRef } from "react"
import api from "@/lib/api"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Trash2, Plus, Search, ArrowUpDown, TrendingUp, TrendingDown, MoreHorizontal, Filter } from "lucide-react"
import { Modal } from "@/components/ui/modal"
import { ToastContainer, ToastMessage } from "@/components/ui/toast"

interface Stock {
    symbol: string
    exchange: string
    active: boolean
    instrument_token: number
    last_price?: number
    change?: number
    last_alert?: string
}

export default function StocksPage() {
    const [stocks, setStocks] = useState<Stock[]>([])
    const [loading, setLoading] = useState(false)
    const [newSymbol, setNewSymbol] = useState("")
    const [searchResults, setSearchResults] = useState<any[]>([])
    const [showResults, setShowResults] = useState(false)
    const [toasts, setToasts] = useState<ToastMessage[]>([])

    // Bulk Add State
    const [isBulkModalOpen, setIsBulkModalOpen] = useState(false)
    const [bulkText, setBulkText] = useState("")

    // Delete Modal State
    const [deleteStock, setDeleteStock] = useState<Stock | null>(null)

    // WebSocket
    const ws = useRef<WebSocket | null>(null)

    const addToast = (type: "success" | "error" | "warning" | "info", message: string) => {
        const id = Math.random().toString(36).substring(7)
        setToasts((prev) => [...prev, { id, type, message }])
    }

    const removeToast = (id: string) => {
        setToasts((prev) => prev.filter((t) => t.id !== id))
    }

    const fetchStocks = async () => {
        try {
            const res = await api.get("/stocks/")
            setStocks(res.data)
        } catch (error) {
            console.error("Failed to fetch stocks", error)
            addToast("error", "Failed to load stocks")
        }
    }

    useEffect(() => {
        fetchStocks()

        // Connect WebSocket
        const socket = new WebSocket(`${process.env.NEXT_PUBLIC_WS_URL}/stocks`)

        socket.onopen = () => {
            console.log("WebSocket Connected")
        }

        socket.onmessage = (event) => {
            try {
                const message = JSON.parse(event.data)
                if (message.type === "TICK_UPDATE") {
                    updatePrices(message.data)
                }
            } catch (e) {
                console.error("WS Error", e)
            }
        }

        socket.onerror = (error) => {
            console.error("WebSocket Error:", error)
        }

        socket.onclose = (event) => {
            console.log("WebSocket Closed:", event.code, event.reason)
        }

        ws.current = socket

        return () => {
            socket.close()
        }
    }, [])

    const updatePrices = (ticks: any[]) => {
        setStocks((prevStocks) => {
            return prevStocks.map((stock) => {
                const tick = ticks.find((t: any) => t.instrument_token === stock.instrument_token)
                if (tick) {
                    return {
                        ...stock,
                        last_price: tick.last_price,
                        change: tick.change
                    }
                }
                return stock
            })
        })
    }

    // Search Logic
    useEffect(() => {
        const delayDebounceFn = setTimeout(async () => {
            if (newSymbol.length > 1) {
                try {
                    const res = await api.get(`/stocks/search?query=${newSymbol}`)
                    setSearchResults(res.data)
                    setShowResults(true)
                } catch (error) {
                    console.error("Search failed", error)
                }
            } else {
                setSearchResults([])
                setShowResults(false)
            }
        }, 300)

        return () => clearTimeout(delayDebounceFn)
    }, [newSymbol])

    const selectStock = (stock: any) => {
        setNewSymbol(stock.tradingsymbol)
        setShowResults(false)
    }

    const handleAddStock = async (e: React.FormEvent) => {
        e.preventDefault()
        if (!newSymbol) return
        setLoading(true)
        try {
            await api.post("/stocks/add", { symbol: newSymbol.toUpperCase(), exchange: "NSE" })
            setNewSymbol("")
            setSearchResults([])
            addToast("success", `Stock ${newSymbol.toUpperCase()} added successfully`)
            fetchStocks()
        } catch (error: any) {
            console.error("Failed to add stock", error)
            addToast("error", error.response?.data?.detail || "Failed to add stock.")
        } finally {
            setLoading(false)
        }
    }

    const handleBulkAdd = async () => {
        if (!bulkText) return
        setLoading(true)
        const symbols = bulkText.split(/[\n,]+/).map(s => s.trim()).filter(s => s)
        try {
            const res = await api.post("/stocks/bulk-add", { symbols })
            const { added, failed } = res.data

            if (added.length > 0) {
                addToast("success", `Added ${added.length} stocks: ${added.join(", ")}`)
            }
            if (failed.length > 0) {
                addToast("warning", `Failed to add ${failed.length} stocks. Check console.`)
                console.warn("Failed stocks:", failed)
            }

            setBulkText("")
            setIsBulkModalOpen(false)
            fetchStocks()
        } catch (error) {
            addToast("error", "Bulk add failed")
        } finally {
            setLoading(false)
        }
    }

    const confirmDelete = async () => {
        if (!deleteStock) return
        try {
            await api.delete(`/stocks/${deleteStock.symbol}`)
            addToast("success", `Removed ${deleteStock.symbol}`)
            fetchStocks()
        } catch (error) {
            addToast("error", "Failed to remove stock")
        } finally {
            setDeleteStock(null)
        }
    }

    const quickAdd = (symbols: string[]) => {
        setBulkText(symbols.join("\n"))
        setIsBulkModalOpen(true)
    }

    return (
        <div className="space-y-6 relative">
            <ToastContainer toasts={toasts} removeToast={removeToast} />

            <div className="flex items-center justify-between">
                <h1 className="text-3xl font-bold text-gray-900">Stock Manager</h1>
                <div className="flex gap-2">
                    <Button variant="outline" onClick={() => setIsBulkModalOpen(true)}>Bulk Add</Button>
                </div>
            </div>

            {/* Quick Categories */}
            <div className="flex gap-2 overflow-x-auto pb-2">
                <Button variant="secondary" size="sm" onClick={() => quickAdd(["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK"])}>Top 5 Nifty</Button>
                <Button variant="secondary" size="sm" onClick={() => quickAdd(["SBIN", "HDFCBANK", "ICICIBANK", "KOTAKBANK", "AXISBANK"])}>Bank Nifty</Button>
                <Button variant="secondary" size="sm" onClick={() => quickAdd(["TATAMOTORS", "M&M", "MARUTI", "EICHERMOT"])}>Auto</Button>
                <Button variant="secondary" size="sm" onClick={() => quickAdd(["TCS", "INFY", "WIPRO", "HCLTECH", "TECHM"])}>IT Sector</Button>
            </div>

            <Card className="overflow-visible">
                <CardHeader>
                    <CardTitle>Add New Stock</CardTitle>
                </CardHeader>
                <CardContent>
                    <form onSubmit={handleAddStock} className="flex gap-4 relative">
                        <div className="flex-1 relative">
                            <Input
                                placeholder="Search Stock (e.g., RELIANCE, INFY)"
                                value={newSymbol}
                                onChange={(e) => {
                                    setNewSymbol(e.target.value)
                                    setShowResults(true)
                                }}
                                onFocus={() => setShowResults(true)}
                                onBlur={() => setTimeout(() => setShowResults(false), 200)}
                            />
                            {showResults && searchResults.length > 0 && (
                                <div className="absolute z-10 w-full mt-1 bg-white border rounded-md shadow-lg max-h-60 overflow-auto">
                                    {searchResults.map((stock) => (
                                        <div
                                            key={stock.instrument_token}
                                            className="px-4 py-2 hover:bg-gray-100 cursor-pointer text-sm flex justify-between"
                                            onClick={() => selectStock(stock)}
                                        >
                                            <div>
                                                <span className="font-bold">{stock.tradingsymbol}</span>
                                                <span className="text-gray-500 ml-2 text-xs">{stock.name}</span>
                                            </div>
                                            <span className="text-xs bg-gray-100 px-2 py-1 rounded">{stock.exchange}</span>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                        <Button type="submit" disabled={loading}>
                            <Plus className="mr-2 h-4 w-4" />
                            Add
                        </Button>
                    </form>
                </CardContent>
            </Card>

            <Card>
                <CardHeader className="flex flex-row items-center justify-between">
                    <CardTitle>Watchlist ({stocks.length})</CardTitle>
                    <div className="flex gap-2">
                        <Button variant="ghost" size="sm"><Filter className="h-4 w-4 mr-1" /> Filter</Button>
                    </div>
                </CardHeader>
                <CardContent>
                    <div className="relative overflow-x-auto">
                        <table className="w-full text-left text-sm text-gray-500">
                            <thead className="bg-gray-50 text-xs uppercase text-gray-700">
                                <tr>
                                    <th className="px-6 py-3 cursor-pointer hover:bg-gray-100">Symbol <ArrowUpDown className="inline h-3 w-3" /></th>
                                    <th className="px-6 py-3">Price</th>
                                    <th className="px-6 py-3">Change</th>
                                    <th className="px-6 py-3">Status</th>
                                    <th className="px-6 py-3 text-right">Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {stocks.map((stock) => (
                                    <tr key={stock.symbol} className="border-b bg-white hover:bg-gray-50">
                                        <td className="px-6 py-4">
                                            <div className="font-medium text-gray-900">{stock.symbol}</div>
                                            <div className="text-xs text-gray-400">{stock.exchange}</div>
                                        </td>
                                        <td className="px-6 py-4 font-mono">
                                            {stock.last_price ? `₹${stock.last_price.toFixed(2)}` : '-'}
                                        </td>
                                        <td className={`px-6 py-4 font-mono ${stock.change && stock.change > 0 ? 'text-green-600' : stock.change && stock.change < 0 ? 'text-red-600' : ''}`}>
                                            {stock.change ? (
                                                <span className="flex items-center">
                                                    {stock.change > 0 ? <TrendingUp className="h-3 w-3 mr-1" /> : <TrendingDown className="h-3 w-3 mr-1" />}
                                                    {stock.change}%
                                                </span>
                                            ) : '-'}
                                        </td>
                                        <td className="px-6 py-4">
                                            <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${stock.active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>
                                                {stock.active ? 'Active' : 'Inactive'}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 text-right">
                                            <Button variant="destructive" size="sm" onClick={() => setDeleteStock(stock)}>
                                                <Trash2 className="h-4 w-4" />
                                            </Button>
                                        </td>
                                    </tr>
                                ))}
                                {stocks.length === 0 && (
                                    <tr>
                                        <td colSpan={5} className="px-6 py-8 text-center text-gray-500">
                                            No stocks in watchlist. Use the search or bulk add to get started.
                                        </td>
                                    </tr>
                                )}
                            </tbody>
                        </table>
                    </div>
                </CardContent>
            </Card>

            {/* Bulk Add Modal */}
            <Modal
                isOpen={isBulkModalOpen}
                onClose={() => setIsBulkModalOpen(false)}
                title="Bulk Add Stocks"
                footer={
                    <>
                        <Button variant="outline" onClick={() => setIsBulkModalOpen(false)}>Cancel</Button>
                        <Button onClick={handleBulkAdd} disabled={loading}>Add Stocks</Button>
                    </>
                }
            >
                <div className="space-y-4">
                    <p className="text-sm text-gray-500">Enter stock symbols separated by commas or new lines (e.g., INFY, TCS, RELIANCE).</p>
                    <textarea
                        className="w-full h-32 p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="INFY&#10;TCS&#10;RELIANCE"
                        value={bulkText}
                        onChange={(e) => setBulkText(e.target.value)}
                    />
                </div>
            </Modal>

            {/* Delete Confirmation Modal */}
            <Modal
                isOpen={!!deleteStock}
                onClose={() => setDeleteStock(null)}
                title="Remove Stock"
                footer={
                    <>
                        <Button variant="outline" onClick={() => setDeleteStock(null)}>Cancel</Button>
                        <Button variant="destructive" onClick={confirmDelete}>Remove</Button>
                    </>
                }
            >
                <p>Are you sure you want to remove <strong>{deleteStock?.symbol}</strong> from your watchlist?</p>
            </Modal>
        </div>
    )
}
