import Link from 'next/link'

const Section = ({ title, links, label='' }: { title: string, links: { href: string, text: string }[], label?: string }) => {
    return (
        <section>
            <h1>{title}</h1>
            <ul>
                {links.map((link, i) =>
                    <li key={i}>
                        <Link href={link.href}>{link.text}</Link>
                    </li>
                )}
            </ul>
            <label>{label}</label>
        </section>
    )
}


export default function Footer({ marginTop }: { marginTop?: boolean }) {
    return (
        <footer className='lp-footer' style={!marginTop ? { marginTop: 0 } : {}}>
            <Section 
                title="About Us" 
                links={[
                    { href: '/about/company', text: 'Company' },
                    { href: '/about/team', text: 'Team' },
                ]}
            />
            <Section 
                title="Support" 
                links={[
                    { href: '/support/contact', text: 'Contact Us' },
                    { href: '/support/faq', text: 'FAQ' }
                ]}
            />
            <Section 
                title="Legal" 
                links={[
                    { href: '/legal/terms', text: 'Terms of Service' },
                    { href: '/legal/privacy', text: 'Privacy Policy' },
                    { href: '/legal/cookies', text: 'Cookie Policy' }
                ]}
                label='© 2025 Shiftiatrics. All rights reserved.'
            />
        </footer>
    )
}