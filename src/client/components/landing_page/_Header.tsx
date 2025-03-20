'use client'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { ReactNode, useEffect, useState } from 'react'
import { Icon } from '@utils'
import menuIcon from '@icons/menu.png'

const HeaderBtn = ({ name, href }: { name: string, href: string }) => {
    const pathname = usePathname()
    const urlName = name?.toLowerCase().replace(' ', '')
    return (
        <Link
            href={href}
            id={urlName}
            className={`header-btn ${urlName && pathname?.includes(urlName) ? 'active-navlink' : ''}`}
        >
            {name}
        </Link>
    )
}

const HeaderBtns = ({ isMenuScrollable }: { isMenuScrollable: boolean }) => (
    <section id='header-btns' style={isMenuScrollable ? { flexDirection: 'column-reverse' } : {}}>
        <HeaderBtn name='Log In' href='/login'/>
        <HeaderBtn name='Sign Up' href='/signup'/>
    </section>
)

const NavLink = ({ href, children }: { href: string, children: ReactNode }) => {
    const pathname = usePathname()
    return <Link href={href} className={pathname?.includes(href) ? 'active-navlink' : ''}>{children}</Link>
}

const NavLinks = ({ isHeaderBtnsShown, isMenuScrollable }: { isHeaderBtnsShown: boolean, isMenuScrollable: boolean }) => (
    <section id='header-links' onClick={e => e.stopPropagation()} style={isMenuScrollable ? { height: '70%' } : {} }>
        <NavLink href='/about'>About</NavLink>
        <NavLink href='/pricing'>Pricing</NavLink>
        <NavLink href='/support'>Support</NavLink>
        <NavLink href='/legal'>Legal</NavLink>
        {isHeaderBtnsShown && <HeaderBtns isMenuScrollable={isMenuScrollable}/>}
    </section>
)

export default function Header({ transparentHeader=false }: { transparentHeader?: boolean }) {
    const [isScrolled, setIsScrolled] = useState(false)
    const [isMenuAvailable, setIsMenuAvailable] = useState(false)
    const [isMenuShown, setIsMenuShown] = useState(false)
    const [isMenuScrollable, setIsMenuScrollable] = useState(false)
    const [isHeaderBtnsShown, setIsHeaderBtnShown] = useState(true)

    useEffect(() => {
        const handleScroll = () => setIsScrolled(window.scrollY > 0)
        const handleResize = () => {
            setIsMenuAvailable(window.innerWidth <= 855)
            setIsHeaderBtnShown(window.innerWidth > 855)
            setIsMenuScrollable(window.innerHeight < 950)
        }

        window.addEventListener('scroll', handleScroll)
        window.addEventListener('resize', handleResize)
        handleResize() // initial check

        return () => {
            window.removeEventListener('scroll', handleScroll)
            window.removeEventListener('resize', handleResize)
        }
    }, [])

    return <>
        <header id='lp-header' className={`${isScrolled || !transparentHeader ? 'bg-visible' : ''}`}>
            <h1><Link href='/'>Shiftiatrics</Link></h1>
            {!isMenuAvailable && <NavLinks isHeaderBtnsShown={false} isMenuScrollable={isMenuScrollable}/>}
            {isHeaderBtnsShown && <HeaderBtns isMenuScrollable={isMenuScrollable}/>}
            {isMenuAvailable &&
                <button id='header-menu-btn' onClick={() => setIsMenuShown(prev => !prev)}>
                    <Icon src={menuIcon} alt='Menu' size={30}/>
                </button>
            }
        </header>

        <div
            className={`backdrop ${isMenuShown ? 'open' : 'closed'}`}
            onClick={() => setIsMenuShown(false)}
            style={isMenuScrollable ? { overflowY: 'scroll' } : {}}
        >
            <NavLinks isHeaderBtnsShown={true} isMenuScrollable={isMenuScrollable}/>
        </div>
    </>
}