import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { ReactNode, useEffect, useState } from 'react'
import { Icon } from '@utils'
import menuIcon from '@icons/menu.png'

const HeaderBtn = () => {
    const pathname = usePathname()
    return (
        <Link
            href='/signup'
            id='header-btn'
            className={pathname?.includes('signup') || pathname?.includes('login') ? 'active-navlink' : ''}
        >
            Sign Up
        </Link>
    )
}

const NavLink = ({ href, children }: { href: string, children: ReactNode }) => {
    const pathname = usePathname()
    return <Link href={href} className={pathname?.includes(href) ? 'active-navlink' : ''}>{children}</Link>
}

const NavLinks = ({ isHeaderBtnShown }: { isHeaderBtnShown: boolean }) => (
    <section id='header-links' onClick={e => e.stopPropagation()}>
        <NavLink href='/about'>About</NavLink>
        <NavLink href='/pricing'>Pricing</NavLink>
        <NavLink href='/support'>Support</NavLink>
        <NavLink href='/legal'>Legal</NavLink>
        {isHeaderBtnShown && <HeaderBtn/>}
    </section>
)

export default function Header({ transparentHeader=false }: { transparentHeader?: boolean }) {
    const [isScrolled, setIsScrolled] = useState(false)
    const [isMenuAvailable, setIsMenuAvailable] = useState(false)
    const [isMenuShown, setIsMenuShown] = useState(false)
    const [isHeaderBtnShown, setIsHeaderBtnShown] = useState(true)

    useEffect(() => {
        const handleScroll = () => setIsScrolled(window.scrollY > 0)
        const handleResize = () => {
            setIsMenuAvailable(window.innerWidth <= 855)
            setIsHeaderBtnShown(window.innerWidth > 855)
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
            {!isMenuAvailable && <NavLinks isHeaderBtnShown={false}/>}
            {isHeaderBtnShown && <HeaderBtn/>}
            {isMenuAvailable &&
                <button id='header-menu-btn' onClick={() => setIsMenuShown(prev => !prev)}>
                    <Icon src={menuIcon} alt='Menu' size={30}/>
                </button>
            }
        </header>

        <div className={`backdrop ${isMenuShown ? 'open' : 'closed'}`} onClick={() => setIsMenuShown(false)}>
            <NavLinks isHeaderBtnShown={true}/>
        </div>
    </>
}