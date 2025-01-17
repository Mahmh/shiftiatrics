import '@styles'
import { Icon } from '@utils'
import RegularPage from '@regpage'
import checkIcon from '@icons/check.png'

const PricingCard = ({ title, titleBg, price, features }: { title: string, titleBg: string, price: string, features: string[] }) => {
    const isCustom = isNaN(parseInt(price[1]))
    return <div className='pricing-card'>
        <section>
            <h2 style={{ background: titleBg }}>{title}</h2>
            <p>{price} {!isCustom && <span>/ month</span>}</p>
            <ul>
                {features.map((feature, i) =>
                    <li key={i}><Icon src={checkIcon} alt='Included'/>{feature}</li>
                )}
            </ul>
        </section>
        <button>{!isCustom ? 'Try for Free' : 'Contact Us'}</button>
    </div>
}

export default function Pricing() {
    return <RegularPage id='pricing-page' transparentHeader={true} footerMarginTop={false}>
        <h1>Pricing Plans</h1>
        <p>Choose the plan that fits your needs, and get started auto-scheduling right away!</p>
        <div className='pricing-cards'>
            <PricingCard
                title='Basic Plan'
                price='$29.99'
                titleBg='linear-gradient(45deg, #72acfe, #3d7cc7)'
                features={[
                    'Up to 5 pediatricians',
                    '3 shifts per day',
                    'Basic support',
                    'E-mail notifications',
                    'Export schedules to Microsoft Excel spreadsheets with simple automatic formating'
                ]}
            />
            <PricingCard
                title='Standard Plan'
                price='$69.99'
                titleBg='linear-gradient(45deg, #217cff, #5ca7ff)'
                features={[
                    'Up to 15 pediatricians',
                    '4 shifts per day',
                    'Priority support',
                    'E-mail & SMS notifications',
                    'Integration with other calendar platforms',
                    'Export schedules to Microsoft Excel spreadsheets with advanced automatic formating'
                ]}
            />
            <PricingCard
                title='Premium Plan'
                price='$129.99'
                titleBg='linear-gradient(45deg, #607eff, #47dbf3)'
                features={[
                    'Unlimited pediatricians',
                    'Unlimited shifts per day',
                    '24/7 support',
                    'E-mail & SMS notifications',
                    'Integration with other calendar platforms',
                    'Export schedules to Microsoft Excel spreadsheets with advanced automatic formating'
                ]}
            />
            <PricingCard
                title='Custom Plan'
                price='Contact Sales'
                titleBg='linear-gradient(45deg, #a463c7, #2241ad)'
                features={[
                    'Tailored for your needs',
                    'Custom shifts',
                    'Dedicated support',
                    'Custom notifications',
                    'Custom integration with other platforms',
                    'Export schedules to Microsoft Excel spreadsheets with custom automatic formating',
                    'Price evaluated based on your ROI'
                ]}
            />
        </div>
    </RegularPage>
}