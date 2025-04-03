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
        <p>
            Choose the plan that fits your needs, and get started auto-scheduling right away!
            You can request a refund anytime, and we&apos;ll refund the unused portion of your subscription.
        </p>
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