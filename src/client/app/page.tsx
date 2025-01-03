'use client'
import { useContext } from 'react'
import { DashboardContext } from '@context'
import { isLoggedIn } from '@utils'
import Dashboard from '@/components/dashboard/Dashboard'
import LandingPage from '@/components/landing_page/LandingPage'

export default function Home() {
    const { account } = useContext(DashboardContext)
    return isLoggedIn(account) ? <Dashboard/> : <LandingPage/>
}