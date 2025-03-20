import { useContext, useEffect, useState } from 'react'
import { dashboardContext } from '@context'
import { getUIDate, getUIPlanName, Request } from '@utils'
import { PRICING_PLANS, FREE_TIER_DETAILS } from '@const'


export default function Subscription() {
    const { account, employees, shifts, subscription } = useContext(dashboardContext)
    const [numSubRequests, setNumSubRequests] = useState<number|null>(null)
    const [loading, setLoading] = useState(true)
    const cardBg = subscription ? PRICING_PLANS.filter(p => p.name === subscription.plan)[0].titleBg : 'linear-gradient(45deg, rgb(90 100 114), rgb(191 191 191))'

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

    return <>
        <section id='sub-card' style={{ background: cardBg }}>
            <h1>{subscription ? getUIPlanName(subscription.plan) : 'Free Tier'}</h1>
            {subscription && <p>Expires at {getUIDate(new Date(subscription.expiresAt))}</p>}
        </section>
        <section id='sub-details'>
            <section>
                <h2>Billing Information</h2>
                {subscription 
                ? 
                    <div>
                        <p>💳 Visa •••• 1234</p>
                        <p>Next Billing: <strong>March 30, 2025</strong></p>
                        <div>
                            <button id='cancel-sub-btn'>Cancel Subscription</button>
                            <button>View Invoice</button>
                        </div>
                    </div>
                :
                    <div><p>No billing information available. You haven&apos;t added a payment method yet.</p></div>
                }
            </section>

            <section>
                <h2>Usage Summary</h2>
                <div>
                    <UsagePart
                        name='Schedule Requests'
                        num={numSubRequests}
                        max={subscription ? subscription.planDetails.maxNumScheduleRequests : FREE_TIER_DETAILS.maxNumScheduleRequests}
                    />
                    <UsagePart
                        name='Registered pediatricians'
                        num={employees.length}
                        max={subscription ? subscription.planDetails.maxNumPediatricians: FREE_TIER_DETAILS.maxNumPediatricians}
                    />
                    <UsagePart
                        name='Registered shifts per day'
                        num={shifts.length}
                        max={subscription ? subscription.planDetails.maxNumShiftsPerDay : FREE_TIER_DETAILS.maxNumShiftsPerDay}
                    />
                </div>
            </section>

            {!subscription || ['basic', 'standard'].includes(subscription.plan) && <section>
                <h2>Need More Schedule Requests?</h2>
                <div>
                    <p>Upgrade to the <strong>Premium Plan</strong> for unlimited scheduling.</p>
                    <div><button>Upgrade Now</button></div>
                </div>
            </section>}
        </section>
    </>
}