"use client"

import { useState } from "react"
import { Modal } from "@/components/ui/modal"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { useToast } from "@/components/ui/use-toast"
import { useAuth } from "@/contexts/AuthContext"
import { useSystemStatus } from "@/contexts/SystemStatusContext"
import { Toast, ToastClose, ToastDescription } from "@/components/ui/toast"

import { usePathname } from "next/navigation"

export function TokenSubmissionModal() {
    const { user } = useAuth()
    const { status, refreshStatus } = useSystemStatus()
    const { toast } = useToast()
    const pathname = usePathname()
    const [tokenUrl, setTokenUrl] = useState("")
    const [submitting, setSubmitting] = useState(false)
    const [success, setSuccess] = useState(false)

    // Only show if user is admin and system is offline
    // AND we are not on the login/register page
    const isAuthPage = pathname === "/login" || pathname === "/register"
    const isOpen = !isAuthPage && status === "OFFLINE" && user?.role === "admin"

    const handleSubmit = async () => {
        if (!tokenUrl) return

        setSubmitting(true)
        try {
            const res = await fetch("http://localhost:8002/api/admin/submit-request-token", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${localStorage.getItem("token")}`
                },
                body: JSON.stringify({ request_token_url: tokenUrl })
            })

            const data = await res.json()

            if (!res.ok) {
                throw new Error(data.detail || "Failed to submit token")
            }

            toast({
                title: "Success",
                description: "System is now ONLINE",
            })

            setTokenUrl("")
            refreshStatus()
            setSuccess(true)

        } catch (error: any) {
            toast({
                title: "Error",
                description: error.message,
            })
        } finally {
            setSubmitting(false)
        }
    }

    if (!isOpen) return null

    return (
        <Modal
            isOpen={isOpen}
            onClose={() => { }}
            title="System Offline"
            footer={
                success ? (
                    <Toast className="bg-green-100 border-green-500">
                        <div className="flex justify-between items-center">
                            <ToastDescription>Token submitted successfully!</ToastDescription>
                            <ToastClose onClick={() => setSuccess(false)} />
                        </div>
                    </Toast>
                ) : (
                    <>
                        <Button variant="outline" onClick={() => { }}>Cancel</Button>
                        <Button onClick={handleSubmit} disabled={submitting}>
                            {submitting ? "Activating..." : "Activate System"}
                        </Button>
                    </>
                )
            }
        >
            <div className="grid gap-4 py-4">
                <div className="grid grid-cols-4 items-center gap-4">
                    <Label htmlFor="tokenUrl" className="text-right">
                        Request Token URL
                    </Label>
                    <Input
                        id="tokenUrl"
                        value={tokenUrl}
                        onChange={(e) => setTokenUrl(e.target.value)}
                        className="col-span-3"
                        placeholder="e.g., https://kite.trade/..."
                    />
                </div>
            </div>
        </Modal>
    )
}
