import React from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

interface SystemSettingsProps {
    settings: any
    onChange: (key: string, value: any) => void
}

export function SystemSettings({ settings, onChange }: SystemSettingsProps) {
    return (
        <Card>
            <CardHeader>
                <CardTitle className="text-lg">Global System Settings</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
                <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                        <Label className="text-base">Market Hours Only</Label>
                        <p className="text-sm text-muted-foreground">
                            Only send alerts between 9:15 AM and 3:30 PM
                        </p>
                    </div>
                    <Switch
                        checked={settings.market_hours_only}
                        onCheckedChange={(c) => onChange("market_hours_only", c)}
                    />
                </div>
                <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                        <Label className="text-base">Auto-Refresh Token</Label>
                        <p className="text-sm text-muted-foreground">
                            Automatically refresh Zerodha access token daily
                        </p>
                    </div>
                    <Switch
                        checked={settings.auto_refresh_token}
                        onCheckedChange={(c) => onChange("auto_refresh_token", c)}
                    />
                </div>
                <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                        <Label className="text-base">Data Source</Label>
                        <p className="text-sm text-muted-foreground">
                            Primary source for real-time price data
                        </p>
                    </div>
                    <Select
                        value={settings.data_source}
                        onValueChange={(v) => onChange("data_source", v)}
                    >
                        <SelectTrigger className="w-[180px]">
                            <SelectValue placeholder="Select source" />
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value="zerodha">Zerodha WebSocket</SelectItem>
                            <SelectItem value="nse_polling">NSE Polling (Fallback)</SelectItem>
                        </SelectContent>
                    </Select>
                </div>
            </CardContent>
        </Card>
    )
}
