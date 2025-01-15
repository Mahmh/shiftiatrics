import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useEffect, useState } from 'react'
import { isLoggedIn } from '@utils'

const NavLink = ({ href, children }: { href: string, children: React.ReactNode }) => {
    const pathname = usePathname()
    useEffect(() => { console.log(pathname) }, [pathname])
    return <Link href={href} className={pathname?.includes(href) ? 'active-navlink' : ''}>{children}</Link>
}

export default function Header({ transparentHeader=false }: { transparentHeader?: boolean }) {
    const [isScrolled, setIsScrolled] = useState(false)
    const [headerBtn, setHeaderBtn] = useState<'Sign Up' | 'Dashboard'>('Sign Up')

    useEffect(() => {
        const handleScroll = () => setIsScrolled(window.scrollY > 0)
        window.addEventListener('scroll', handleScroll)
        return () => window.removeEventListener('scroll', handleScroll)
    }, [])

    useEffect(() => {
        setHeaderBtn(isLoggedIn() ? 'Dashboard' : 'Sign Up')
    }, [])

    return (
        <header id='lp-header' className={isScrolled || !transparentHeader ? 'bg-visible' : ''}>
            <h1><Link href='/'>Shiftiatrics</Link></h1>
            <section id='header-links'>
                <NavLink href='/about'>About</NavLink>
                <NavLink href='/pricing'>Pricing</NavLink>
                <NavLink href='/support'>Support</NavLink>
                <NavLink href='/legal'>Legal</NavLink>
            </section>
            <Link href={headerBtn === 'Sign Up' ? '/signup' : '/'} id='signup-btn'>{headerBtn}</Link>
        </header>
    )
}