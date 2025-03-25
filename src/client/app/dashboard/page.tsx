'use client'
import { useEffect } from 'react'
import { setMetadata } from '@utils'
import DashboardPage from '@/components/dashboard/DashboardPage'

export default function Dashboard() {
    useEffect(() => {
        setMetadata({
            title: 'Dashboard | Shiftiatrics',
            description: 'Control and generate shift schedules for your registered pediatricians'
        })
    }, [])
    return <DashboardPage/>
}