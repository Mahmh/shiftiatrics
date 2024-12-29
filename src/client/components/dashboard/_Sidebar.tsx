import { useContext } from 'react'
import { StaticImageData } from 'next/image'
import { DashboardContext } from '@context'
import { Icon } from '@utils'
import scheduleIcon from '@icons/schedule.png'
import employeeIcon from '@icons/employee.png'
import shiftIcon from '@icons/shift.png'
import settingsIcon from '@icons/settings.png'
// import supportIcon from '@icons/support.png'
import { ContentName } from '@/app/types'

export default function Sidebar() {
    const { content, setContent } = useContext(DashboardContext)

    const SidebarButton = ({ name, src, contentName=name }: { name: string, src: StaticImageData, contentName?: string }) => (
        <button onClick={() => setContent(contentName.toLowerCase() as ContentName)} className={content === contentName.toLowerCase() ? 'active-content-btn' : ''}>
            <Icon src={src} alt={`${name.toLowerCase()}-icon`}/>{name}
        </button>
    )

    return (
        <nav id='sidebar'>
            <section id='sidebar-upper'>
                <SidebarButton name='Schedules' src={scheduleIcon}/>
                <SidebarButton name='Employees' src={employeeIcon}/>
                <SidebarButton name='Shifts per Day' contentName='Shifts' src={shiftIcon}/>
            </section>
            <section id='sidebar-lower'>
                <SidebarButton name='Settings' src={settingsIcon}/>
                {/* <SidebarButton name='Support' src={supportIcon}/> */}
            </section>
        </nav>
    )
}