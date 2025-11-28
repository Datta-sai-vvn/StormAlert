"use client"

import React, { createContext, useContext, useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { jwtDecode } from "jwt-decode"

interface User {
    email: string
    role: string
}

interface AuthContextType {
    user: User | null
    loading: boolean
    login: (token: string) => void
    logout: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
    const [user, setUser] = useState<User | null>(null)
    const [loading, setLoading] = useState(true)
    const router = useRouter()

    useEffect(() => {
        const token = localStorage.getItem("token")
        if (token) {
            try {
                const decoded: any = jwtDecode(token)
                // Check expiry
                if (decoded.exp * 1000 < Date.now()) {
                    logout()
                } else {
                    setUser({
                        email: decoded.sub,
                        role: decoded.role || "user"
                    })
                }
            } catch (e) {
                logout()
            }
        }
        setLoading(false)
    }, [])

    const login = (token: string) => {
        localStorage.setItem("token", token)
        const decoded: any = jwtDecode(token)
        setUser({
            email: decoded.sub,
            role: decoded.role || "user"
        })
        router.push("/dashboard")
    }

    const logout = () => {
        localStorage.removeItem("token")
        setUser(null)
        router.push("/login")
    }

    return (
        <AuthContext.Provider value={{ user, loading, login, logout }}>
            {children}
        </AuthContext.Provider>
    )
}

export const useAuth = () => {
    const context = useContext(AuthContext)
    if (context === undefined) {
        throw new Error("useAuth must be used within an AuthProvider")
    }
    return context
}
