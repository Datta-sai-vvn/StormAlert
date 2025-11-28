import React from "react"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

interface AlgorithmSelectorProps {
    value: string
    onChange: (value: string) => void
}

export function AlgorithmSelector({ value, onChange }: AlgorithmSelectorProps) {
    return (
        <Card>
            <CardHeader>
                <CardTitle className="text-lg">Algorithm Mode</CardTitle>
            </CardHeader>
            <CardContent>
                <RadioGroup value={value} onValueChange={onChange} className="grid gap-4">
                    <div className="flex items-start space-x-3 space-y-0">
                        <RadioGroupItem value="trailing" id="trailing" className="mt-1" />
                        <div className="grid gap-1.5">
                            <Label htmlFor="trailing" className="font-medium">
                                Trailing Mode
                            </Label>
                            <p className="text-sm text-gray-500">
                                Alerts based on the highest/lowest price seen so far. Best for catching strong swings and reversals.
                            </p>
                        </div>
                    </div>
                    <div className="flex items-start space-x-3 space-y-0">
                        <RadioGroupItem value="rolling" id="rolling" className="mt-1" />
                        <div className="grid gap-1.5">
                            <Label htmlFor="rolling" className="font-medium">
                                Rolling Window Mode
                            </Label>
                            <p className="text-sm text-gray-500">
                                Alerts based on price movement within a fixed timeframe (e.g., last 10 mins). Best for intraday volatility.
                            </p>
                        </div>
                    </div>
                    <div className="flex items-start space-x-3 space-y-0">
                        <RadioGroupItem value="both" id="both" className="mt-1" />
                        <div className="grid gap-1.5">
                            <Label htmlFor="both" className="font-medium">
                                Hybrid (Both)
                            </Label>
                            <p className="text-sm text-gray-500">
                                Uses both algorithms simultaneously. Alerts if EITHER condition is met. Maximum coverage.
                            </p>
                        </div>
                    </div>
                </RadioGroup>
            </CardContent>
        </Card>
    )
}
