import { useContext, useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { dashboardContext } from '@context'
import { Choice, getAccountLimits, getUIDate, getUIPlanName, Icon, Request } from '@utils'
import { PRICING_PLANS } from '@const'
import { parseSub } from '@auth'
import type { PricingPlan, StripeInvoice, StripeInvoiceResponse, SubscriptionResponse } from '@types'
import checkIcon from '@icons/check.png'

const SECTIONS = ['My Plan', 'All Pricing Plans'] as const
type SubscriptionSection = typeof SECTIONS[number]


const MyPlan = ({ setShownSection }: { setShownSection: (value: SubscriptionSection) => void }) => {
    const { account, subscription, setSubscription, employees, shifts, setModalContent, openModal, closeModal } = useContext(dashboardContext)
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

    const openViewInvoiceModal = () => {
        const ModalContent = () => {
            const [invoice, setInvoice] = useState<StripeInvoice>()
            const [loading, setLoading] = useState(false)
        
            useEffect(() => {
                const getInvoice = async () => {
                    setLoading(true)
                    await new Request(
                        `sub/${account.id}/invoice`,
                        (data: StripeInvoiceResponse) => setInvoice({
                            invoiceId: data.invoice_id,
                            amountDue: data.amount_due,
                            amountPaid: data.amount_paid,
                            currency: data.currency,
                            status: data.status,
                            invoicePdf: data.invoice_pdf,
                            hostedInvoiceUrl: data.hosted_invoice_url,
                            createdAt: data.created_at,
                            dueDate: data.due_date,
                            description: data.description,
                            subscriptionId: data.subscription_id
                        })
                    ).get()
                    setLoading(false)
                }
                getInvoice()
            }, [])
        
            if (loading) return <p style={{ padding: 20 }}>Loading...</p>
            if (!invoice) return <p style={{ padding: 20 }}>No invoice found.</p>
        
            return <>
                <table style={{ borderCollapse: 'collapse', width: '100%' }}>
                    <tbody>
                        <tr>
                            <td><b>Invoice ID:</b></td>
                            <td>
                                <div style={{ maxWidth: '40vw', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                                    {invoice.invoiceId}
                                </div>
                            </td>
                        </tr>
                        <tr>
                            <td><b>Subscription ID:</b></td>
                            <td>
                                <div style={{ maxWidth: '40vw', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                                    {invoice.subscriptionId}
                                </div>
                            </td>
                        </tr>
                        <tr>
                            <td><b>Status:</b></td>
                            <td>{invoice.status.charAt(0).toUpperCase() + invoice.status.slice(1)}</td>
                        </tr>
                        <tr>
                            <td><b>Amount Due:</b></td>
                            <td>${invoice.amountDue.toFixed(2)} {invoice.currency}</td>
                        </tr>
                        <tr>
                            <td><b>Amount Paid:</b></td>
                            <td>${invoice.amountPaid.toFixed(2)} {invoice.currency}</td>
                        </tr>
                        <tr>
                            <td><b>Created At:</b></td>
                            <td>{new Date(invoice.createdAt).toLocaleString()}</td>
                        </tr>
                        <tr>
                            <td><b>Due Date:</b></td>
                            <td>{invoice.dueDate ? new Date(invoice.dueDate).toLocaleString() : 'None'}</td>
                        </tr>
                        <tr>
                            <td><b>Description:</b></td>
                            <td>{invoice.description || 'None'}</td>
                        </tr>
                    </tbody>
                </table>
                {(invoice.invoicePdf && invoice.hostedInvoiceUrl) && <section className='modal-btns'>
                    <a href={invoice.invoicePdf} target='_blank' rel='noopener noreferrer'><button>Download as PDF</button></a>
                    <a href={invoice.hostedInvoiceUrl} target='_blank' rel='noopener noreferrer'><button>View on Stripe</button></a>
                </section>}
            </>
        }

        setModalContent(<ModalContent/>)
        openModal()
    }

    const openCancelSubModal = () => {
        const ModalContent = () => {
            const [errMsg, setErrMsg] = useState<string>()
            const [loading, setLoading] = useState(false)
            const [success, setSuccess] = useState(false)

            const cancelSub = async () => {
                setLoading(true)
                await new Request(
                    `sub/${account.id}/cancel`,
                    () => {
                        setSubscription(null)
                        setSuccess(true)
                    },
                    setErrMsg
                ).delete()
                setLoading(false)
            }
        
            if (loading) return <p style={{ padding: 20 }}>Canceling your subscription...</p>
            if (errMsg) return <p style={{ padding: 20 }}>An error has occurred: {errMsg}</p>
            if (success) return <p style={{ padding: 20 }}>Your subscription has been successfully canceled.</p>

            return <>
                <h1>Are You Sure You Want to Cancel?</h1>
                <p>
                    If you cancel now, you will receive a prorated refund for any unused time. However, features of your current plan will be disabled immediately.
                    You will be downgraded to the free tier afterward.
                    {(subscription && new Date(subscription.expiresAt).getUTCDate() - new Date(subscription.createdAt).getUTCDate() === 7) && 
                        ' You will also no longer be able to start a free trial on any plan.'
                    }
                </p>
                <Choice onNo={closeModal} onYes={cancelSub} />
            </>
        }

        setModalContent(<ModalContent/>)
        openModal()
    }

    return <div className='card-container'>
        <section id='sub-card' style={{ background: cardBg }}>
            <h1>{subscription ? getUIPlanName(subscription.plan) : 'Free Tier'}</h1>
            {subscription && <p>Valid until {getUIDate(new Date(subscription.expiresAt))}</p>}
        </section>
        <section id='sub-details'>
            {((subscription && !account.subExpired) || account.subExpired) && <section>
                <h2>Actions</h2>
                <div>
                {subscription && !account.subExpired
                ?
                    <div className='sub-actions-card'>
                        <button onClick={openViewInvoiceModal} style={{ minWidth: 220 }}>View Invoice</button>
                        <button onClick={openCancelSubModal} id='cancel-sub-btn'>Cancel Subscription</button>
                    </div>
                :
                    <>
                        <p>
                            Your subscription has ended, and you are now on the free tier.  
                            Renew now to regain full access to all features!
                        </p>
                        <div>
                            <button onClick={() => setShownSection('All Pricing Plans')}>Renew or Upgrade Now</button>
                        </div>
                    </>
                }
                </div>
            </section>}

            <section>
                <h2>Monthly Usage Summary</h2>
                <div>
                    <UsagePart name='Registered pediatricians' num={employees.length} max={maxNumPediatricians}/>
                    <UsagePart name='Registered shifts per day' num={shifts.length} max={maxNumShiftsPerDay}/>
                    <UsagePart name='Schedule creation, modification, or deletion' num={numSubRequests} max={maxNumScheduleRequests}/>
                    <p style={{ fontStyle: 'italic' }}>Schedule limit resets on {getUIDate(subscription ? new Date(subscription.expiresAt) : nextMonth)}</p>
                </div>
            </section>

            {(subscription === null || ['basic', 'standard'].includes(subscription.plan)) && 
                <section>
                    <h2>Need More Schedule Requests?</h2>
                    <div>
                        <p>Upgrade to the <b>Premium Plan</b> for unlimited scheduling.</p>
                        <div>
                            <button onClick={() => setShownSection('All Pricing Plans')}>
                                {(subscription === null && !account.hasUsedTrial) ? 'Try for Free' : 'Upgrade Now'}
                            </button>
                        </div>
                    </div>
                </section>
            }
        </section>
    </div>
}


const PricingCard = ({ name, titleBg, price, features }: PricingPlan) => {
    const router = useRouter()
    const { account, subscription, setSubscription, setModalContent, openModal, closeModal } = useContext(dashboardContext)
    const { hasUsedTrial } = account
    const isCustom = typeof price === 'string'
    const isActivated = name === subscription?.plan

    const getButtonLabel = () => {
        if (isCustom) return 'Contact Us'
        if (isActivated) return 'Currently Subscribed'
        if (hasUsedTrial) return 'Subscribe'
        return 'Try for Free'
    }

    const subscribe = async () => {
        return await new Request(
            `sub/${account.id}/create_checkout_session`,
            (data: { checkout_url: string }) => router.push(data.checkout_url),
            (error) => error
        ).post({ plan_name: name })
    }

    const openChangeSubModal = () => {
        const changeSub = async () => {
            setModalContent(<p style={{ padding: 20 }}>Please wait...</p>)
    
            const error = await new Request(
                `sub/${account.id}/change`,
                (data: SubscriptionResponse) => {
                    if (data) setSubscription(parseSub(data))
                    console.log('data.subscription', data)
                    return null
                },
                (error) => error
            ).patch({ new_plan: name })
    
            setModalContent(
                <p style={{ padding: 20 }}>
                    {error ? `An error has occurred: ${error}` : 'You have successfully changed your plan!'}
                </p>
            )
        }
    
        setModalContent(<>
            <h1>Confirm Plan Change</h1>
            <p>
                Your subscription will be updated immediately, and the price difference will be handled automatically. 
                You may receive a prorated refund or be charged the difference.
            </p>
            <Choice onYes={changeSub} onNo={closeModal} />
        </>)
    }
    
    const handleClick = async () => {
        if (isCustom) {
            router.push(PRICING_PLANS[3].link!)
            return
        }

        if (subscription === null) {
            setModalContent(<p style={{ padding: 20 }}>Please wait...</p>)
            openModal()

            const error = await subscribe()
            setModalContent(
                <p style={{ padding: 20 }}>
                    {error ? `An error has occurred: ${error}` : 'You are being redirected to checkout...'}
                </p>
            )
        } else {
            openChangeSubModal()
            openModal()
        }
    }

    return (
        <div className='pricing-card'>
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
    )
}


const AllPricingPlans = () => ( 
    <div className='pricing-cards card-container'>
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
)


export default function Subscription() {
    const [shownSection, setShownSection] = useState<SubscriptionSection>('My Plan')

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
        {shownSection === 'My Plan' && <MyPlan setShownSection={setShownSection}/>}
        {shownSection === 'All Pricing Plans' && <AllPricingPlans/>}
    </>
}