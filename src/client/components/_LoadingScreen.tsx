import { useState, useEffect, useContext } from 'react'
import { dashboardContext, nullAccount, nullSub } from '@context'

export default function LoadingScreen() {
    const { account, subscription, employees, shifts, schedules, settings } = useContext(dashboardContext)
    const [isShown, setIsShown] = useState(true)

    useEffect(() => {
        setTimeout(() => {
            setIsShown(
                !(employees && shifts && schedules && settings)
                || account === nullAccount
                || subscription === nullSub
            )
        }, 500)
    }, [account, employees, shifts, schedules, settings, subscription])

    return (
        <div className={`loading-screen ${isShown ? 'open' : 'closed'}`}>
            <div className='dot'></div>
            <div className='dot'></div>
            <div className='dot'></div>
        </div>
    )
}