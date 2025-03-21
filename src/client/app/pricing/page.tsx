'use client'
import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Icon, setMetadata, getUIPlanName } from '@utils'
import { PRICING_PLANS } from '@const'
import type { PricingPlan } from '@types'
import RegularPage from '@regpage'
import checkIcon from '@icons/check.png'

const PricingCard = ({ name, titleBg, price, link, features }: PricingPlan) => {
    const router = useRouter()
    const isCustom = typeof price === 'string'

    return <div className='pricing-card'>
        <section>
            <h2 style={{ background: titleBg }}>{getUIPlanName(name)}</h2>
            <p>{!isCustom && 'US$'}{price} {!isCustom && <span>/ month</span>}</p>
            <ul>
                {features.map((feature, i) =>
                    <li key={i}><Icon src={checkIcon} alt='Included'/>{feature}</li>
                )}
            </ul>
        </section>
        <button onClick={link ? () => router.push(link) : undefined}>{!isCustom ? 'Try for Free' : 'Contact Us'}</button>
    </div>
}


export default function Pricing() {
    useEffect(() => {
        setMetadata({
            title: 'Pricing | Shiftiatrics',
            description: 'Pricing plans for using Shiftiatrics'
        })
    }, [])

    return <RegularPage id='pricing-page' transparentHeader={true} footerMarginTop={false}>
        <h1>Pricing Plans</h1>
        <p>
            Choose the plan that fits your needs, and get started auto-scheduling right away!
            You can request a refund anytime, and we&apos;ll refund the unused portion of your subscription.
        </p>
        <div className='pricing-cards'>
            {PRICING_PLANS.map(plan => (
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