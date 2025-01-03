import { useContext } from 'react'
import type { StaticImageData } from 'next/image'
import type { ContentName } from '@types'
import { DashboardContext } from '@context'
import { Icon } from '@utils'
import scheduleIcon from '@icons/schedule.png'
import employeeIcon from '@icons/employee.png'
import shiftIcon from '@icons/shift.png'
import settingsIcon from '@icons/settings.png'
import menuIcon from '@icons/menu.png'
import closeIcon from '@icons/white_close.png'

export const MenuButton = () => {
    const { isMenuShown, setIsMenuShown } = useContext(DashboardContext)
    return (
        <button id='dashboard-menu-btn' onClick={() => setIsMenuShown(prev => !prev)}>
            {isMenuShown ? <Icon src={closeIcon} alt='Close menu' size={40}/> : <Icon src={menuIcon} alt='Menu' size={40}/>}
        </button>
    )
}

export default function Sidebar() {
    const { content, setContent, darkThemeClassName, screenWidth, isMenuShown, setIsMenuShown } = useContext(DashboardContext)

    const SidebarButton = ({ name, src, contentName=name }: { name: string, src: StaticImageData, contentName?: string }) => {
        const handleClick = () => {
            setContent(contentName.toLowerCase() as ContentName)
            if (screenWidth <= 950) setIsMenuShown(false)
        }
        return (
            <button onClick={handleClick} className={content === contentName.toLowerCase() ? 'active-content-btn' : ''}>
                <Icon src={src} alt={`${name.toLowerCase()}-icon`}/>{name}
            </button>
        )
    }

    return isMenuShown && (
        <nav id='sidebar' className={darkThemeClassName}>
            <section id='sidebar-upper'>
                <SidebarButton name='Schedules' src={scheduleIcon}/>
                <SidebarButton name='Employees' src={employeeIcon}/>
                <SidebarButton name='Shifts per Day' contentName='Shifts' src={shiftIcon}/>
            </section>
            <section id='sidebar-lower'>
                <SidebarButton name='Settings' src={settingsIcon}/>
            </section>
        </nav>
    )
}