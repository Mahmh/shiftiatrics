'use client'
import { useContext, useEffect } from 'react'
import { dashboardContext } from '@context'
import { isLoggedIn } from '@utils'
import LandingPage from '@/components/landing_page/LandingPage'
import DashboardPage from '@/components/dashboard/DashboardPage'

export default function Home() {
    const { account } = useContext(dashboardContext)
    useEffect(() => { window.scrollTo(0, 0) }, [])
    return isLoggedIn(account) ? <DashboardPage/> : <LandingPage/>
}