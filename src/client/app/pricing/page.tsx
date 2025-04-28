'use client'
import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Icon, setMetadata, getUIPlanName } from '@utils'
import { PLANS } from '@const'
import type { Plan } from '@types'
import RegularPage from '@regpage'
import checkIcon from '@icons/check.png'

export default function Pricing() {
    useEffect(() => {
        setMetadata({
            title: 'Pricing | Shiftiatrics',
            description: 'Pricing plans for using Shiftiatrics'
        })
    }, [])

    return <RegularPage id='pricing-page' transparentHeader={true} footerMarginTop={false}>
        <h1>Pricing Plans</h1>
        <div id='pricing-description'>
            <p>Select the plan that best matches your team&apos;s needs, and our team will work closely with you to personalize your scheduling solution.</p>
            <p>If you&apos;re not satisfied, you can request a refund—adjusted fairly based on any work already completed for your setup and service.</p>
        </div>
        <div className='pricing-cards'>
            {PLANS.map(plan => (
                <PricingCard
                    name={plan.name}
                    price={plan.price}
                    titleBg={plan.titleBg}
                    link={plan.link}
                    features={plan.features}
                    key={plan.name}
                />
            ))}
        </div>
    </RegularPage>
}


const PricingCard = ({ name, titleBg, price, link, features }: Plan) => {
    const router = useRouter()
    const isCustom = typeof price === 'string'

    return <div className='pricing-card'>
        <section>
            <h2 style={{ background: titleBg }}>{getUIPlanName(name)}</h2>
            <p>{!isCustom && 'Starting at US$'}{price} {!isCustom && <span>/ month</span>}</p>
            <ul>
                {features.map((feature, i) =>
                    <li key={i}><Icon src={checkIcon} alt='Included'/>{feature}</li>
                )}
            </ul>
        </section>
        <button onClick={link ? () => router.push(link) : undefined}>Contact Us</button>
    </div>
}