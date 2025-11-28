"use client"

import {
    Sheet,
    SheetContent,
    SheetDescription,
    SheetHeader,
    SheetTitle,
} from "@/components/ui/sheet"
import { Badge } from "@/components/ui/badge"
import { format } from "date-fns"
import { Separator } from "@/components/ui/separator"

interface AlertDrawerProps {
    log: any
    open: boolean
    onClose: () => void
}

export function AlertDrawer({ log, open, onClose }: AlertDrawerProps) {
    if (!log) return null

    return (
        <Sheet open={open} onOpenChange={onClose}>
            <SheetContent className="w-[400px] sm:w-[540px]">
                <SheetHeader>
                    <SheetTitle className="flex items-center gap-2">
                        {log.stock_symbol}
                        <Badge variant={log.alert_type === "DIP" ? "destructive" : "default"}>
                            {log.alert_type}
                        </Badge>
                    </SheetTitle>
                    <SheetDescription>
                        Alert Details & Context
                    </SheetDescription>
                </SheetHeader>

                <div className="mt-6 space-y-6">
                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <div className="text-sm font-medium text-muted-foreground">Price</div>
                            <div className="text-2xl font-bold">₹{log.price.toFixed(2)}</div>
                        </div>
                        <div>
                            <div className="text-sm font-medium text-muted-foreground">Change</div>
                            <div className={`text-2xl font-bold ${log.change_percent < 0 ? "text-red-500" : "text-green-500"}`}>
                                {log.change_percent.toFixed(2)}%
                            </div>
                        </div>
                    </div>

                    <Separator />

                    <div className="space-y-4">
                        <div>
                            <div className="text-sm font-medium text-muted-foreground mb-1">Timestamp</div>
                            <div className="font-mono">{format(new Date(log.timestamp), "PPP pp")}</div>
                        </div>

                        <div>
                            <div className="text-sm font-medium text-muted-foreground mb-1">Message</div>
                            <div className="p-3 bg-muted rounded-md text-sm">
                                {log.message}
                            </div>
                        </div>

                        {log.notes && (
                            <div>
                                <div className="text-sm font-medium text-muted-foreground mb-1">System Notes</div>
                                <div className="text-sm">{log.notes}</div>
                            </div>
                        )}

                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <div className="text-sm font-medium text-muted-foreground mb-1">Algorithm</div>
                                <Badge variant="outline">{log.algo_mode || "Standard"}</Badge>
                            </div>
                            <div>
                                <div className="text-sm font-medium text-muted-foreground mb-1">Exchange</div>
                                <Badge variant="outline">{log.exchange || "NSE"}</Badge>
                            </div>
                        </div>
                    </div>
                </div>
            </SheetContent>
        </Sheet>
    )
}
