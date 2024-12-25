import { useContext } from 'react'
import { StaticImageData } from 'next/image'
import { AppContext } from '@context'
import { Icon } from '@utils'
import scheduleIcon from '@icons/schedule.png'
import employeeIcon from '@icons/employee.png'
import shiftIcon from '@icons/shift.png'
import accountIcon from '@icons/account.png'
import settingsIcon from '@icons/settings.png'
import supportIcon from '@icons/support.png'
import { ContentName } from '@/app/types'

export default function Sidebar() {
    const { content, setContent } = useContext(AppContext)

    const ContentButton = ({ name, src }: { name: string, src: StaticImageData }) => (
        <button onClick={() => setContent(name.toLowerCase() as ContentName)} className={content === name.toLowerCase() ? 'active-content-btn' : ''}>
            <Icon src={src} alt={`${name.toLowerCase()}-icon`}/>{name}
        </button>
    )

    return (
        <nav id='sidebar'>
            <section id='sidebar-upper'>
                <ContentButton name='Schedules' src={scheduleIcon}/>
                <ContentButton name='Employees' src={employeeIcon}/>
                <ContentButton name='Shifts' src={shiftIcon}/>
            </section>
            <section id='sidebar-lower'>
                <ContentButton name='Account' src={accountIcon}/>
                <ContentButton name='Settings' src={settingsIcon}/>
                <ContentButton name='Support' src={supportIcon}/>
            </section>
        </nav>
    )
}