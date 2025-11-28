import React from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Info } from "lucide-react"

interface ImpactPreviewProps {
    dipThreshold: number
    timeframe: number
    cooldown: number
}

export function ImpactPreview({ dipThreshold, timeframe, cooldown }: ImpactPreviewProps) {
    const examplePrice = 752.00
    const dropAmount = (examplePrice * dipThreshold) / 100
    const triggerPrice = examplePrice - dropAmount

    let sensitivity = "Medium"
    let color = "text-yellow-600"

    if (dipThreshold < 1.5) {
        sensitivity = "High"
        color = "text-red-600"
    } else if (dipThreshold > 4) {
        sensitivity = "Low"
        color = "text-green-600"
    }

    return (
        <Card className="bg-slate-50 border-slate-200">
            <CardHeader>
                <CardTitle className="text-sm font-medium text-slate-500 uppercase tracking-wider">
                    Real-Time Impact Preview
                </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
                <div className="text-sm text-slate-700">
                    With a dip threshold of <span className="font-bold">{dipThreshold}%</span> and a <span className="font-bold">{timeframe}-minute</span> rolling window:
                </div>

                <Alert className="bg-white border-blue-100">
                    <Info className="h-4 w-4 text-blue-500" />
                    <AlertTitle className="text-blue-700">Simulation</AlertTitle>
                    <AlertDescription className="text-slate-600 mt-1">
                        If a stock is at <span className="font-mono font-bold">₹{examplePrice.toFixed(2)}</span>, an alert will trigger if it drops <span className="font-bold text-red-500">₹{dropAmount.toFixed(2)}</span> to <span className="font-mono font-bold">₹{triggerPrice.toFixed(2)}</span>.
                    </AlertDescription>
                </Alert>

                <div className="grid grid-cols-2 gap-4 pt-2">
                    <div>
                        <div className="text-xs text-slate-500 uppercase">Est. Sensitivity</div>
                        <div className={`text-lg font-bold ${color}`}>{sensitivity}</div>
                    </div>
                    <div>
                        <div className="text-xs text-slate-500 uppercase">Cooldown Period</div>
                        <div className="text-lg font-bold text-slate-700">{cooldown} mins</div>
                    </div>
                </div>
            </CardContent>
        </Card>
    )
}
