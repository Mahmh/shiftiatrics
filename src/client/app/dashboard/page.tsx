'use client'
import { useCallback, useContext, useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { getUIDate, setMetadata } from '@utils'
import { isLoggedIn } from '@auth'
import { dashboardContext } from '@context'
import type { Subscription } from '@types'
import DashboardPage from '@/components/dashboard/DashboardPage'

export default function Dashboard() {
    const router = useRouter()
    const { setAccount, setSubscription, openModal, setModalContent } = useContext(dashboardContext)
    const [authChecked, setAuthChecked] = useState(false)

    const checkIsSubExpiringSoon = useCallback((subscription: Subscription) => {
        const now = new Date()
        const expiryDate = new Date(subscription.expiresAt)
        const timeDiff = expiryDate.getTime() - now.getTime()
        const daysLeft = Math.floor(timeDiff / (1000 * 60 * 60 * 24))
        if (daysLeft === 3) {
            setModalContent(<>
                <h1>Subscription Expiring Soon</h1>
                <p>
                    Your current plan will expire in {daysLeft} day(s) on {getUIDate(expiryDate)}.
                    To avoid service interruptions, upgrade now and continue enjoying all features.
                </p>
                <button>Renew or Upgrade Now</button>
            </>)
            openModal()
        }
    }, [openModal, setModalContent])


    const checkLoginStatus = useCallback(async () => {
        const res = await isLoggedIn()
        if (res === false) { router.push('/'); return }

        setAccount(res.account)
        setSubscription(res.subscription)
        setAuthChecked(true) // Ensure rendering only happens after auth check

        if (res.subscription !== null) checkIsSubExpiringSoon(res.subscription)        
    }, [router, checkIsSubExpiringSoon, setAccount, setSubscription])


    useEffect(() => {
        checkLoginStatus()
    }, [router, checkLoginStatus])

    useEffect(() => {
        setMetadata({
            title: 'Dashboard | Shiftiatrics',
            description: 'Control and generate shift schedules for your registered pediatricians'
        })
    }, [])


    if (!authChecked) return null // Prevent rendering before auth check completes
    return <DashboardPage/>
}