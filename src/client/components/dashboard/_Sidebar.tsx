import { useContext, useEffect, useRef, useState } from 'react'
import type { StaticImageData } from 'next/image'
import type { ContentName } from '@types'
import { dashboardContext } from '@context'
import { Icon } from '@utils'
import scheduleIcon from '@icons/schedule.png'
import staffIcon from '@icons/staff.png'
import shiftIcon from '@icons/shift.png'
import holidayIcon from '@icons/holiday.png'
import settingsIcon from '@icons/settings.png'
import menuIcon from '@icons/menu.png'
import closeIcon from '@icons/white_close.png'
import SubscriptionIcon from '@icons/subscription.png'

export default function Sidebar() {
    const { subscription, content, setContent, darkThemeClassName, screenWidth, isMenuShown, setIsMenuShown } = useContext(dashboardContext)

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
                <SidebarButton name='Staff' src={staffIcon}/>
                <SidebarButton name='Shifts per Day' contentName='Shifts' src={shiftIcon}/>
                <SidebarButton name='Holidays' src={holidayIcon}/>
            </section>
            <section id='sidebar-lower'>
                {subscription !== null && <SidebarButton name='Subscription' src={SubscriptionIcon}/>}
                <SidebarButton name='Settings' src={settingsIcon}/>
            </section>
        </nav>
    )
}


export const MenuButton = () => {
    const { isMenuShown, setIsMenuShown, isModalOpen } = useContext(dashboardContext)
    const buttonRef = useRef<HTMLButtonElement>(null)
    const [position, setPosition] = useState({ x: 10, y: 0 })

    const isDragging = useRef(false)
    const touchOffset = useRef({ x: 0, y: 0 })

    useEffect(() => {
        const updateInitialPosition = () => {
            const button = buttonRef.current
            const buttonHeight = button?.offsetHeight || 60
            const bottomMargin = 20
            const y = window.innerHeight - buttonHeight - bottomMargin
            setPosition({ x: 20, y })
        }

        updateInitialPosition()
        window.addEventListener('resize', updateInitialPosition)
        return () => window.removeEventListener('resize', updateInitialPosition)
    }, [])

    const handleTouchStart = (e: React.TouchEvent) => {
        isDragging.current = true
        const touch = e.touches[0]
        const button = buttonRef.current
        if (button) {
            const rect = button.getBoundingClientRect()
            touchOffset.current = {
                x: touch.clientX - rect.left,
                y: touch.clientY - rect.top
            }
        }
    }

    const handleTouchMove = (e: React.TouchEvent) => {
        if (!isDragging.current) return
        const touch = e.touches[0]
        const button = buttonRef.current
        if (!button) return

        const screenWidth = window.innerWidth
        const screenHeight = window.innerHeight
        const buttonWidth = button.offsetWidth
        const buttonHeight = button.offsetHeight

        let newX = touch.clientX - touchOffset.current.x
        let newY = touch.clientY - touchOffset.current.y

        // Clamp values to prevent going out of bounds
        newX = Math.max(0, Math.min(screenWidth - buttonWidth, newX))
        newY = Math.max(0, Math.min(screenHeight - buttonHeight, newY))

        setPosition({ x: newX, y: newY })
    }

    const handleTouchEnd = () => {
        isDragging.current = false
    }

    const handleClick = () => {
        if (isDragging.current) return
        setIsMenuShown(prev => !prev)
    }

    return !isModalOpen && (
        <button
            id='dashboard-menu-btn'
            ref={buttonRef}
            onClick={handleClick}
            onTouchStart={handleTouchStart}
            onTouchMove={handleTouchMove}
            onTouchEnd={handleTouchEnd}
            style={{
                position: 'fixed',
                left: position.x,
                top: position.y,
                zIndex: 9999,
                touchAction: 'none'
            }}
        >
            {isMenuShown
                ? <Icon src={closeIcon} alt='Close menu' size={40}/>
                : <Icon src={menuIcon} alt='Menu' size={40}/>}
        </button>
    )
}