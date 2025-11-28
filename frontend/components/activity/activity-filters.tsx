"use client"

import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Calendar } from "@/components/ui/calendar"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { CalendarIcon, Search, Filter, X } from "lucide-react"
import { format } from "date-fns"
import { cn } from "@/lib/utils"
import { useState } from "react"

interface ActivityFiltersProps {
    onFilterChange: (filters: any) => void
}

export function ActivityFilters({ onFilterChange }: ActivityFiltersProps) {
    const [search, setSearch] = useState("")
    const [type, setType] = useState("all")
    const [date, setDate] = useState<Date>()

    const handleSearch = (val: string) => {
        setSearch(val)
        onFilterChange({ search: val, type, date })
    }

    const handleTypeChange = (val: string) => {
        setType(val)
        onFilterChange({ search, type: val, date })
    }

    const handleDateSelect = (val: Date | undefined) => {
        setDate(val)
        onFilterChange({ search, type, date: val })
    }

    const clearFilters = () => {
        setSearch("")
        setType("all")
        setDate(undefined)
        onFilterChange({ search: "", type: "all", date: undefined })
    }

    return (
        <div className="flex flex-col gap-4 md:flex-row md:items-center bg-white p-4 rounded-lg border shadow-sm">
            <div className="relative flex-1">
                <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                    placeholder="Search symbol, notes..."
                    className="pl-8"
                    value={search}
                    onChange={(e) => handleSearch(e.target.value)}
                />
            </div>

            <Select value={type} onValueChange={handleTypeChange}>
                <SelectTrigger className="w-[180px]">
                    <SelectValue placeholder="Alert Type" />
                </SelectTrigger>
                <SelectContent>
                    <SelectItem value="all">All Types</SelectItem>
                    <SelectItem value="DIP">Dip</SelectItem>
                    <SelectItem value="SPIKE">Spike</SelectItem>
                    <SelectItem value="COOLDOWN">Cooldown</SelectItem>
                </SelectContent>
            </Select>

            <Popover>
                <PopoverTrigger asChild>
                    <Button
                        variant={"outline"}
                        className={cn(
                            "w-[240px] justify-start text-left font-normal",
                            !date && "text-muted-foreground"
                        )}
                    >
                        <CalendarIcon className="mr-2 h-4 w-4" />
                        {date ? format(date, "PPP") : <span>Pick a date</span>}
                    </Button>
                </PopoverTrigger>
                <PopoverContent className="w-auto p-0" align="start">
                    <Calendar
                        mode="single"
                        selected={date}
                        onSelect={handleDateSelect}
                        initialFocus
                    />
                </PopoverContent>
            </Popover>

            {(search || type !== "all" || date) && (
                <Button variant="ghost" onClick={clearFilters} className="px-2 lg:px-3">
                    <X className="mr-2 h-4 w-4" />
                    Reset
                </Button>
            )}
        </div>
    )
}
