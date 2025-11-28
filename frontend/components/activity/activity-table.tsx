"use client"

import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Trash2, Eye, ArrowDown, ArrowUp } from "lucide-react"
import { format } from "date-fns"

interface ActivityTableProps {
    logs: any[]
    onDelete: (id: string) => void
    onView: (log: any) => void
}

export function ActivityTable({ logs, onDelete, onView }: ActivityTableProps) {
    if (logs.length === 0) {
        return (
            <div className="text-center py-10 text-muted-foreground bg-white rounded-lg border border-dashed">
                No activity logs found matching your criteria.
            </div>
        )
    }

    return (
        <div className="rounded-md border bg-white shadow-sm overflow-hidden">
            <Table>
                <TableHeader>
                    <TableRow>
                        <TableHead>Timestamp</TableHead>
                        <TableHead>Symbol</TableHead>
                        <TableHead>Type</TableHead>
                        <TableHead>Price</TableHead>
                        <TableHead>Change</TableHead>
                        <TableHead>Message</TableHead>
                        <TableHead className="text-right">Actions</TableHead>
                    </TableRow>
                </TableHeader>
                <TableBody>
                    {logs.map((log) => (
                        <TableRow key={log._id} className="group hover:bg-muted/50">
                            <TableCell className="font-mono text-xs text-muted-foreground">
                                {format(new Date(log.timestamp), "MMM dd, HH:mm:ss")}
                            </TableCell>
                            <TableCell className="font-bold">{log.stock_symbol}</TableCell>
                            <TableCell>
                                <Badge variant={log.alert_type === "DIP" ? "destructive" : log.alert_type === "SPIKE" ? "default" : "secondary"}>
                                    {log.alert_type}
                                </Badge>
                            </TableCell>
                            <TableCell>₹{log.price.toFixed(2)}</TableCell>
                            <TableCell className={log.change_percent < 0 ? "text-red-500 font-medium" : "text-green-500 font-medium"}>
                                <div className="flex items-center gap-1">
                                    {log.change_percent < 0 ? <ArrowDown className="h-3 w-3" /> : <ArrowUp className="h-3 w-3" />}
                                    {Math.abs(log.change_percent).toFixed(2)}%
                                </div>
                            </TableCell>
                            <TableCell className="max-w-[300px] truncate text-sm text-muted-foreground">
                                {log.message}
                            </TableCell>
                            <TableCell className="text-right">
                                <div className="flex justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                    <Button variant="ghost" size="icon" onClick={() => onView(log)}>
                                        <Eye className="h-4 w-4" />
                                    </Button>
                                    <Button variant="ghost" size="icon" className="text-destructive hover:text-destructive" onClick={() => onDelete(log._id)}>
                                        <Trash2 className="h-4 w-4" />
                                    </Button>
                                </div>
                            </TableCell>
                        </TableRow>
                    ))}
                </TableBody>
            </Table>
        </div>
    )
}
