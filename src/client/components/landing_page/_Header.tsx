import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { ReactNode, useEffect, useState } from 'react'
import { Icon, isLoggedIn } from '@utils'
import menuIcon from '@icons/menu.png'

const HeaderBtn = ({ headerBtn }: { headerBtn: string }) => (
    <Link href={headerBtn === 'Sign Up' ? '/signup' : '/'} id='header-btn'>{headerBtn}</Link>
)

const NavLink = ({ href, children }: { href: string, children: ReactNode }) => {
    const pathname = usePathname()
    return <Link href={href} className={pathname?.includes(href) ? 'active-navlink' : ''}>{children}</Link>
}

const NavLinks = ({ headerBtn }: { headerBtn?: string }) => (
    <section id='header-links' onClick={e => e.stopPropagation()}>
        <NavLink href='/about'>About</NavLink>
        <NavLink href='/pricing'>Pricing</NavLink>
        <NavLink href='/support'>Support</NavLink>
        <NavLink href='/legal'>Legal</NavLink>
        {headerBtn && <HeaderBtn headerBtn={headerBtn}/>}
    </section>
)

export default function Header({ transparentHeader=false }: { transparentHeader?: boolean }) {
    const [isScrolled, setIsScrolled] = useState(false)
    const [headerBtn, setHeaderBtn] = useState<'Sign Up' | 'Dashboard'>('Sign Up')
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

    useEffect(() => {
        setHeaderBtn(isLoggedIn() ? 'Dashboard' : 'Sign Up')
    }, [])

    return <>
        <header id='lp-header' className={`${isScrolled || !transparentHeader ? 'bg-visible' : ''}`}>
            <h1><Link href='/'>Shiftiatrics</Link></h1>
            {!isMenuAvailable && <NavLinks/>}
            {isHeaderBtnShown && <HeaderBtn headerBtn={headerBtn}/>}
            {isMenuAvailable &&
                <button id='header-menu-btn' onClick={() => setIsMenuShown(prev => !prev)}>
                    <Icon src={menuIcon} alt='Menu' size={30}/>
                </button>
            }
        </header>

        <div className={`backdrop ${isMenuShown ? 'open' : 'closed'}`} onClick={() => setIsMenuShown(false)}>
            <NavLinks headerBtn={headerBtn}/>
        </div>
    </>
}