'use client'
import { useContext, useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { isLoggedIn } from '@auth'
import { dashboardContext } from '@context'
import DashboardPage from '@/components/dashboard/DashboardPage'

export default function Dashboard() {
    const { setAccount } = useContext(dashboardContext)
    const router = useRouter()
    const [authChecked, setAuthChecked] = useState(false)

    useEffect(() => {
        const checkLoginStatus = async () => {
            const account = await isLoggedIn()
            if (!account) {
                router.push('/')
            } else {
                setAccount(account)
                setAuthChecked(true) // Ensure rendering only happens after auth check
            }
        }
        checkLoginStatus()
    }, [router, setAccount])

    if (!authChecked) return null // Prevent rendering before auth check completes
    return <DashboardPage />
}