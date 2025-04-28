import { useContext, useState } from 'react'
import { useRouter } from 'next/navigation'
import { dashboardContext } from '@context'
import { getUIDate, getUIPlanName, Icon } from '@utils'
import { PLANS } from '@const'
import type { Plan, StripeInvoice } from '@types'
import checkIcon from '@icons/check.png'

const SECTIONS = ['My Plan', 'All Pricing Plans'] as const
type SubscriptionSection = typeof SECTIONS[number]


const InvoiceCard = ({ invoice }: { invoice: StripeInvoice }) => (
    <section className='invoice-card'>
        <table>
            <tbody>
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
            </tbody>
        </table>
        {(invoice.invoicePdf && invoice.hostedInvoiceUrl) && <section className='invoice-btns'>
            <a href={invoice.invoicePdf} target='_blank' rel='noopener noreferrer'><button>Download as PDF</button></a>
            <a href={invoice.hostedInvoiceUrl} target='_blank' rel='noopener noreferrer'><button>View on Stripe</button></a>
        </section>}
    </section>
)


const MyPlan = () => {
    const { subscription, invoices } = useContext(dashboardContext)
    const cardBg = subscription ? PLANS.filter(p => p.name === subscription.plan)[0].titleBg : 'linear-gradient(45deg, rgb(66 95 135), rgb(150 179 228))'

    return (
        <div className='card-container'>
            <section id='sub-card' style={{ background: cardBg }}>
                <h1>{subscription ? getUIPlanName(subscription.plan) : 'Free Tier'}</h1>
                {subscription && <p>Valid until {getUIDate(new Date(subscription.expiresAt))}</p>}
            </section>

            <section className='invoices-card'>
                <h2>Invoices</h2>
                <div className='invoices'>
                    {invoices.map(invoice => <InvoiceCard invoice={invoice} key={invoice.invoiceId}/>)}
                </div>
            </section>
        </div>
    )
}


const PricingCard = ({ name, titleBg, price, features }: Plan) => {
    const router = useRouter()
    const { subscription } = useContext(dashboardContext)
    const isActivated = name === subscription?.plan

    return (
        <div className='pricing-card'>
            <section>
                <h2 style={{ background: titleBg }}>{getUIPlanName(name)}</h2>
                <p>{typeof price === 'number' && 'Starting at US$'}{price} {typeof price === 'number' && <span>/ month</span>}</p>
                <ul>
                    {features.map((feature, i) => <li key={i}><Icon src={checkIcon} alt='Included'/>{feature}</li>)}
                </ul>
            </section>
            <button
                onClick={() => router.push(`/support/contact?query_type=${name}_plan`)}
                disabled={isActivated}
                className={isActivated ? 'sub-activated-btn' : ''}
            >
                {isActivated ? 'Currently Activated' : 'Contact Us'}
            </button>
        </div>
    )
}


const AllPlans = () => ( 
    <div className='pricing-cards card-container'>
        {PLANS.map(plan => <PricingCard name={plan.name} price={plan.price} titleBg={plan.titleBg} features={plan.features} key={plan.name}/>)}
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
        {shownSection === 'My Plan' && <MyPlan/>}
        {shownSection === 'All Pricing Plans' && <AllPlans/>}
    </>
}