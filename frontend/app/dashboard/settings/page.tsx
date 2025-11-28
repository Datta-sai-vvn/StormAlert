"use client"

import { useEffect, useState } from "react"
import api from "@/lib/api"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { useToast } from "@/components/ui/use-toast"
import { AlgorithmSelector } from "@/components/settings/algorithm-selector"
import { ImpactPreview } from "@/components/settings/impact-preview"
import { NotificationSettings } from "@/components/settings/notification-settings"
import { SystemSettings } from "@/components/settings/system-settings"
import { Save, RotateCcw, Zap } from "lucide-react"

export default function SettingsPage() {
    const { toast } = useToast()
    const [loading, setLoading] = useState(true)
    const [settings, setSettings] = useState<any>({
        timeframe_minutes: 10,
        dip_threshold: 1.0,
        rise_threshold: 1.0,
        cooldown_minutes: 15,
        algo_mode: "both",
        alert_frequency: "once",
        market_hours_only: true,
        auto_refresh_token: true,
        auto_reconnect_ws: true,
        data_source: "zerodha",
        email_enabled: false,
        whatsapp_enabled: false,
        telegram_enabled: false
    })

    useEffect(() => {
        fetchSettings()
    }, [])

    const fetchSettings = async () => {
        try {
            const res = await api.get("/settings/")
            setSettings(res.data)
        } catch (error) {
            console.error("Failed to fetch settings", error)
            toast({ title: "Error", description: "Failed to load settings" })
        } finally {
            setLoading(false)
        }
    }

    const handleChange = (key: string, value: any) => {
        setSettings((prev: any) => ({ ...prev, [key]: value }))
    }

    const handleSave = async () => {
        try {
            await api.put("/settings/update", settings)
            toast({ title: "Success", description: "Settings saved successfully ✔" })
        } catch (error) {
            toast({ title: "Error", description: "Failed to save settings" })
        }
    }

    const handlePreset = async (name: string) => {
        try {
            const res = await api.post(`/settings/preset?preset_name=${name}`)
            setSettings(res.data)
            toast({ title: "Preset Applied", description: `Applied ${name} mode settings.` })
        } catch (error) {
            toast({ title: "Error", description: "Failed to apply preset" })
        }
    }

    const handleTestNotification = async (channel: string) => {
        try {
            await api.post(`/settings/test-notification?channel=${channel}`)
            toast({ title: "Test Sent", description: `Test alert sent to ${channel}` })
        } catch (error) {
            toast({ title: "Error", description: "Failed to send test alert" })
        }
    }

    if (loading) return <div>Loading settings...</div>

    return (
        <div className="space-y-6 pb-10">
            <div className="flex items-center justify-between">
                <h1 className="text-3xl font-bold text-gray-900">Settings & Configuration</h1>
                <div className="space-x-2">
                    <Button variant="outline" onClick={() => fetchSettings()}>
                        <RotateCcw className="mr-2 h-4 w-4" /> Reset
                    </Button>
                    <Button onClick={handleSave}>
                        <Save className="mr-2 h-4 w-4" /> Save Changes
                    </Button>
                </div>
            </div>

            <div className="grid gap-6 lg:grid-cols-3">
                {/* Left Column: Main Controls */}
                <div className="lg:col-span-2 space-y-6">
                    {/* Presets */}
                    <Card>
                        <CardHeader>
                            <CardTitle className="text-lg">Quick Presets</CardTitle>
                        </CardHeader>
                        <CardContent className="flex gap-2 flex-wrap">
                            <Button variant="outline" onClick={() => handlePreset("safe")}>Safe Mode</Button>
                            <Button variant="outline" onClick={() => handlePreset("standard")}>Standard</Button>
                            <Button variant="outline" onClick={() => handlePreset("scalping")}>Scalping (High Sens)</Button>
                            <Button variant="outline" onClick={() => handlePreset("extreme")}>Extreme</Button>
                        </CardContent>
                    </Card>

                    {/* Thresholds */}
                    <Card>
                        <CardHeader>
                            <CardTitle className="text-lg">Thresholds & Sensitivity</CardTitle>
                        </CardHeader>
                        <CardContent className="grid gap-6 md:grid-cols-2">
                            <div className="space-y-2">
                                <Label>Dip Threshold (%)</Label>
                                <Input
                                    type="number"
                                    step="0.1"
                                    value={settings.dip_threshold}
                                    onChange={(e) => handleChange("dip_threshold", parseFloat(e.target.value))}
                                />
                            </div>
                            <div className="space-y-2">
                                <Label>Rise Threshold (%)</Label>
                                <Input
                                    type="number"
                                    step="0.1"
                                    value={settings.rise_threshold}
                                    onChange={(e) => handleChange("rise_threshold", parseFloat(e.target.value))}
                                />
                            </div>
                            <div className="space-y-2">
                                <Label>Timeframe (Minutes)</Label>
                                <Input
                                    type="number"
                                    value={settings.timeframe_minutes}
                                    onChange={(e) => handleChange("timeframe_minutes", parseInt(e.target.value))}
                                />
                            </div>
                            <div className="space-y-2">
                                <Label>Cooldown (Minutes)</Label>
                                <Input
                                    type="number"
                                    value={settings.cooldown_minutes}
                                    onChange={(e) => handleChange("cooldown_minutes", parseInt(e.target.value))}
                                />
                            </div>
                        </CardContent>
                    </Card>

                    <AlgorithmSelector value={settings.algo_mode} onChange={(v) => handleChange("algo_mode", v)} />

                    <NotificationSettings
                        settings={settings}
                        onChange={handleChange}
                        onTest={handleTestNotification}
                    />
                </div>

                {/* Right Column: Preview & System */}
                <div className="space-y-6">
                    <ImpactPreview
                        dipThreshold={settings.dip_threshold}
                        timeframe={settings.timeframe_minutes}
                        cooldown={settings.cooldown_minutes}
                    />

                    <SystemSettings settings={settings} onChange={handleChange} />
                </div>
            </div>
        </div>
    )
}
