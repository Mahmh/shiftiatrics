import { Metadata } from 'next'
import { RouteCard } from '@utils'
import RegularPage from '@/components/RegularPage'

export const generateMetadata = async (): Promise<Metadata> => ({
    title: `Legal | Shiftiatrics`,
    description: `Legal information about Shiftiatrics`
})

export default function Legal() {
    return <RegularPage>
        <section className='route-card-container'>
            <RouteCard 
                href='/legal/terms' 
                h='Terms of Service' 
                p='Read our terms of service to understand the rules and regulations regarding the use of our services. It outlines the legal agreements between you and our company.'
            />
            <RouteCard 
                href='/legal/privacy' 
                h='Privacy Policy' 
                p='Learn about our privacy practices and how we handle your personal information. Our privacy policy explains what data we collect, how we use it, and your rights regarding your information.'
            />
            <RouteCard 
                href='/legal/cookies' 
                h='Cookie Policy' 
                p='Understand how we use cookies and similar technologies on our website. Our cookie policy provides details on the types of cookies we use, their purposes, and how you can manage your cookie preferences.'
            />
        </section>
    </RegularPage>
}