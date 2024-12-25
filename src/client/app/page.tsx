'use client'
import { useContext } from 'react'
import { AppContext } from '@context'
import { isLoggedIn } from '@utils'
import Dashboard from '@/components/dashboard/Dashboard'
import LandingPage from '@/components/landing_page/LandingPage'

export default function Home() {
    const { account } = useContext(AppContext)
    return isLoggedIn(account) ? <Dashboard/> : <LandingPage/>
}