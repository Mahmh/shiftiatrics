import { useState, useEffect, useContext } from 'react'
import { DashboardContext } from '@context'

export default function LoadingScreen() {
    const { account, employees, shifts, schedules, settings } = useContext(DashboardContext)
    const [isShown, setIsShown] = useState(true)

    useEffect(() => {
        setTimeout(() => setIsShown(!(account && employees && shifts && schedules && settings)), 0)
    }, [account, employees, shifts, schedules, settings])

    return (
        <div className={`loading-screen ${isShown ? 'open' : 'closed'}`}>
            <div className='dot'></div>
            <div className='dot'></div>
            <div className='dot'></div>
        </div>
    )
}