import React from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"
import { Switch } from "@/components/ui/switch"
import { Button } from "@/components/ui/button"
import { MessageCircle, Mail, Send } from "lucide-react"

interface NotificationSettingsProps {
    settings: any
    onChange: (key: string, value: any) => void
    onTest: (channel: string) => void
}

export function NotificationSettings({ settings, onChange, onTest }: NotificationSettingsProps) {
    return (
        <Card>
            <CardHeader>
                <CardTitle className="text-lg">Notification Channels</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
                {/* WhatsApp */}
                <div className="flex items-start space-x-4">
                    <div className="mt-1 bg-green-100 p-2 rounded-full">
                        <MessageCircle className="h-5 w-5 text-green-600" />
                    </div>
                    <div className="flex-1 space-y-2">
                        <div className="flex items-center justify-between">
                            <Label htmlFor="whatsapp-toggle" className="font-medium">WhatsApp Alerts</Label>
                            <Switch
                                id="whatsapp-toggle"
                                checked={settings.whatsapp_enabled}
                                onCheckedChange={(c) => onChange("whatsapp_enabled", c)}
                            />
                        </div>
                        {settings.whatsapp_enabled && (
                            <div className="flex gap-2">
                                <Input
                                    placeholder="+91 98765 43210"
                                    value={settings.whatsapp_number || ""}
                                    onChange={(e) => onChange("whatsapp_number", e.target.value)}
                                />
                                <Button variant="outline" size="sm" onClick={() => onTest("whatsapp")}>Test</Button>
                            </div>
                        )}
                    </div>
                </div>

                {/* Email */}
                <div className="flex items-start space-x-4">
                    <div className="mt-1 bg-blue-100 p-2 rounded-full">
                        <Mail className="h-5 w-5 text-blue-600" />
                    </div>
                    <div className="flex-1 space-y-2">
                        <div className="flex items-center justify-between">
                            <Label htmlFor="email-toggle" className="font-medium">Email Alerts</Label>
                            <Switch
                                id="email-toggle"
                                checked={settings.email_enabled}
                                onCheckedChange={(c) => onChange("email_enabled", c)}
                            />
                        </div>
                        {settings.email_enabled && (
                            <div className="flex gap-2">
                                <Input
                                    placeholder="you@example.com"
                                    value={settings.email_address || ""}
                                    onChange={(e) => onChange("email_address", e.target.value)}
                                />
                                <Button variant="outline" size="sm" onClick={() => onTest("email")}>Test</Button>
                            </div>
                        )}
                    </div>
                </div>

                {/* Telegram */}
                <div className="flex items-start space-x-4">
                    <div className="mt-1 bg-sky-100 p-2 rounded-full">
                        <Send className="h-5 w-5 text-sky-600" />
                    </div>
                    <div className="flex-1 space-y-2">
                        <div className="flex items-center justify-between">
                            <Label htmlFor="telegram-toggle" className="font-medium">Telegram Alerts</Label>
                            <Switch
                                id="telegram-toggle"
                                checked={settings.telegram_enabled}
                                onCheckedChange={(c) => onChange("telegram_enabled", c)}
                            />
                        </div>
                        {settings.telegram_enabled && (
                            <div className="flex gap-2">
                                <Input
                                    placeholder="Chat ID"
                                    value={settings.telegram_chat_id || ""}
                                    onChange={(e) => onChange("telegram_chat_id", e.target.value)}
                                />
                                <Button variant="outline" size="sm" onClick={() => onTest("telegram")}>Test</Button>
                            </div>
                        )}
                    </div>
                </div>
            </CardContent>
        </Card>
    )
}
