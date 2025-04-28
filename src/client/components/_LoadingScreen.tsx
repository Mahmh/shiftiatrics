import { useState, useEffect, useContext } from 'react'
import { dashboardContext, nullSettings, nullAccount, nullSub } from '@context'

export default function LoadingScreen() {
    const { account, subscription, teams, employees, shifts, schedules, settings } = useContext(dashboardContext)
    const [isShown, setIsShown] = useState(true)

    useEffect(() => {
        setTimeout(() => {
            setIsShown(
                !(teams && employees && shifts && schedules)
                || settings === nullSettings
                || account === nullAccount
                || subscription === nullSub
            )
        }, 500)
    }, [account, teams, employees, shifts, schedules, settings, subscription])

    return (
        <div className={`loading-screen ${isShown ? 'open' : 'closed'}`}>
            <div className='dot'></div>
            <div className='dot'></div>
            <div className='dot'></div>
        </div>
    )
}