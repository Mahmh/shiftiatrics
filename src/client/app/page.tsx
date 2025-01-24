'use client'
import { useContext, useEffect, useState } from 'react'
import { isLoggedIn } from '@utils'
import { dashboardContext } from '@context'
import type { Account } from '@types'
import LandingPage from '@/components/landing_page/LandingPage'
import DashboardPage from '@/components/dashboard/DashboardPage'

export default function Home() {
    const { account } = useContext(dashboardContext)
    const [isUserLoggedIn, setUserLoggedIn] = useState<false | Account>(false)

    useEffect(() => {
        window.scrollTo(0, 0)
        const checkLoginStatus = async () => {
            if (account.id === -Infinity) setUserLoggedIn(false)
            else setUserLoggedIn(await isLoggedIn())
        }
        checkLoginStatus()
    }, [account, setUserLoggedIn])

    return isUserLoggedIn ? <DashboardPage/> : <LandingPage/>
}