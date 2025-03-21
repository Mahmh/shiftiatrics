import { useContext, useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { dashboardContext } from '@context'
import { getAccountLimits, getUIDate, getUIPlanName, Icon, Request } from '@utils'
import { PRICING_PLANS } from '@const'
import type { PricingPlan } from '@types'
import checkIcon from '@icons/check.png'

const MyPlan = () => {
    const { account, subscription, employees, shifts } = useContext(dashboardContext)
    const { maxNumPediatricians, maxNumShiftsPerDay, maxNumScheduleRequests } = getAccountLimits(subscription)
    const [numSubRequests, setNumSubRequests] = useState<number|null>(null)
    const [loading, setLoading] = useState(true)
    const cardBg = subscription ? PRICING_PLANS.filter(p => p.name === subscription.plan)[0].titleBg : 'linear-gradient(45deg, rgb(66 95 135), rgb(150 179 228))'
    const today = new Date()
    const nextMonth = new Date(today.getFullYear(), today.getMonth() + 1, 2)

    useEffect(() => {
        const getSubRequests = async () => {
            setLoading(true)
            await new Request(
                `sub/${account.id}/schedule_requests`,
                (data: { num_requests: number }) => setNumSubRequests(data.num_requests),
                () => setNumSubRequests(null)
            ).get()
            setLoading(false)
        }
        getSubRequests()
    }, [account.id])

    const UsagePart = ({ name, num, max }: { name: string, num: number | null, max: number }) => (
        <p>
            {name}:
            <span className={num && (num >= max) ? 'limit-reached' : ''}>
                {loading && num ? '...' : max === 999 ? ' Unlimited' : ` ${num} / ${max}`}
            </span>
        </p>
    )

    return <div className='card-container'>
        <section id='sub-card' style={{ background: cardBg }}>
            <h1>{subscription ? getUIPlanName(subscription.plan) : 'Free Tier'}</h1>
            {subscription && <p>Expires at {getUIDate(new Date(subscription.expiresAt))}</p>}
        </section>
        <section id='sub-details'>
            <section>
                <h2>Billing Information</h2>
                <div>
                {subscription && !account.subExpired
                ?
                    <>
                        <p>Visa •••• 1234</p>
                        <p>Next Billing: <strong>March 30, 2025</strong></p>
                        <div>
                            <button id='cancel-sub-btn'>Cancel Subscription</button>
                            <button>View Invoice</button>
                        </div>
                    </>
                : 
                    account.subExpired 
                    ?
                    <>
                        <p>
                            Your subscription has expired, and you&apos;re now on the free tier.  
                            Renew now to regain full access to all features!
                        </p>
                        <div>
                            <button>Renew or Upgrade Now</button>
                        </div>
                    </>
                    :
                    <>
                        <p>No billing information found. Add a payment method to activate your selected plan.</p>
                        <div>
                            <button>Add Payment Method</button>
                        </div>
                    </>
                }
                </div>
            </section>

            <section>
                <h2>Usage Summary</h2>
                <div>
                    <UsagePart name='Registered pediatricians' num={employees.length} max={maxNumPediatricians}/>
                    <UsagePart name='Registered shifts per day' num={shifts.length} max={maxNumShiftsPerDay}/>
                    <UsagePart name='Schedule creation, modification, or deletion' num={numSubRequests} max={maxNumScheduleRequests}/>
                    <p style={{ fontStyle: 'italic' }}>Limit resets on {getUIDate(subscription ? new Date(subscription.expiresAt) : nextMonth)}</p>
                </div>
            </section>

            {(subscription === null || ['basic', 'standard'].includes(subscription.plan)) && 
                <section>
                    <h2>Need More Schedule Requests?</h2>
                    <div>
                        <p>Upgrade to the <strong>Premium Plan</strong> for unlimited scheduling.</p>
                        <div>
                            {(subscription === null && !account.hasUsedTrial) && <button>Try for Free</button>}
                            <button>Upgrade Now</button>
                        </div>
                    </div>
                </section>
            }
        </section>
    </div>
}


const PricingCard = ({ name, titleBg, price, features }: PricingPlan) => {
    const { account, subscription, setModalContent, openModal } = useContext(dashboardContext)
    const router = useRouter()
    const isCustom = typeof price === 'string'
    const isActivated = name === subscription?.plan
    const { hasUsedTrial } = account

    const getButtonLabel = () => {
        if (isCustom) return 'Contact Us'
        if (isActivated) return 'Currently Subscribed'
        if (hasUsedTrial) return 'Subscribe'
        return 'Try for Free'
    }

    const handleClick = () => {
        if (isCustom) {
            router.push(PRICING_PLANS[3].link!)
            return
        }

        if (hasUsedTrial) {
            setModalContent(<></>)
        } else {
            setModalContent(<></>)
        }

        openModal()
    }

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
        <button onClick={handleClick} disabled={isActivated} className={isActivated ? 'sub-activated-btn' : ''}>
            {getButtonLabel()}
        </button>
    </div>
}


const AllPricingPlans = () => {
    return <div className='pricing-cards card-container'>
        {PRICING_PLANS.map(plan => (
            <PricingCard
                name={plan.name}
                price={plan.price}
                titleBg={plan.titleBg}
                features={plan.features}
                key={plan.name}
            />
        ))}
    </div>
}


export default function Subscription() {
    const SECTIONS = ['My Plan', 'All Pricing Plans'] as const
    const [shownSection, setShownSection] = useState<typeof SECTIONS[number]>('My Plan')

    return <>
        <header>
            <section id='header-upper'>
                <section id='header-tabs'>
                    {SECTIONS.map(s => 
                        <button
                            key={s}
                            onClick={() => setShownSection(s)}
                            className={`tab-btn ${s === shownSection ? 'active-tab-btn' : ''}`}
                        >
                            {s}
                        </button>
                    )}
                </section>
            </section>
        </header>
        {shownSection === 'My Plan' && <MyPlan/>}
        {shownSection === 'All Pricing Plans' && <AllPricingPlans/>}
    </>
}