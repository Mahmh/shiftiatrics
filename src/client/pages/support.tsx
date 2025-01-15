import '@styles'
import RegularPage from '@/components/RegularPage'
import { RouteCard } from '@utils'

export default function Support() {
    return <RegularPage>
        <section className='route-card-container'>
            <RouteCard
                href='/support/contact'
                h='Contact Us'
                p='If you have any questions or need assistance, feel free to reach out to our support team. We are here to help you with any issues or concerns you may have. We are available to ensure you get the support you need.'
            />
            <RouteCard
                href='/support/faq'
                h='FAQ'
                p="Find answers to the most frequently asked questions about our services. Our FAQ section covers a wide range of topics to help you get the information you need quickly. If you can't find what you're looking for, don't hesitate to contact us."
            />
        </section>
    </RegularPage>
}