"use client"

import { AuthProvider } from "@/contexts/AuthContext"
import { SystemStatusProvider } from "@/contexts/SystemStatusContext"
import { OfflineBanner } from "@/components/ui/OfflineBanner"
import { TokenSubmissionModal } from "@/components/admin/TokenSubmissionModal"
import { Toaster } from "@/components/ui/toaster"

export function Providers({ children }: { children: React.ReactNode }) {
    return (
        <AuthProvider>
            <SystemStatusProvider>
                <OfflineBanner />
                {children}
                <TokenSubmissionModal />
                <Toaster />
            </SystemStatusProvider>
        </AuthProvider>
    )
}
