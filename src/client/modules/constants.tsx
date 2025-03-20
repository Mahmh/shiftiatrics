import { PricingPlanName, PricingPlan } from '@types'

export const DOMAIN_NAME = 'shiftiatrics.com'
export const MIN_YEAR = 2023
export const MAX_YEAR = 2025
export const MAX_WORK_HOURS = 210 // hours per week
export const TOO_MANY_REQS_MSG = 'You have sent too many requests. Please try again later.'

export const PRICING_PLAN_NAMES: PricingPlanName[] = ['basic', 'standard', 'premium', 'custom']
export const PRICING_PLANS: PricingPlan[] = [
    {
        name: 'basic',
        price: 19.99,
        titleBg: 'linear-gradient(45deg, #72acfe, #3d7cc7)',
        link: '/signup?plan=basic',
        features: [
            'Up to 5 pediatricians',
            '2 shifts per day',
            'Generate or update schedules up to 10 times per month.',
            'Basic support',
            'Export schedules to Microsoft Excel spreadsheets with simple automatic formatting'
        ],
        details: {
            maxNumPediatricians: 5,
            maxNumShiftsPerDay: 2,
            maxNumScheduleRequests: 10
        }
    },
    {
        name: 'standard',
        price: 69.99,
        titleBg: 'linear-gradient(45deg, #217cff, #5ca7ff)',
        link: '/signup?plan=standard',
        features: [
            'Up to 12 pediatricians',
            '4 shifts per day',
            'Generate or update schedules up to 30 times per month',
            'Priority support',
            'E-mail notifications',
            'Integration with external platforms',
            'Export schedules to Microsoft Excel spreadsheets with better automatic formatting'
        ],
        details: {
            maxNumPediatricians: 12,
            maxNumShiftsPerDay: 4,
            maxNumScheduleRequests: 30
        }
    },
    {
        name: 'premium',
        price: 99.99,
        titleBg: 'linear-gradient(45deg, #607eff, #47dbf3)',
        link: '/signup?plan=premium',
        features: [
            'Unlimited pediatricians',
            'Unlimited shifts per day',
            'Generate or update schedules without limits each month',
            'Priority support',
            'E-mail notifications',
            'Integration with external platforms',
            'Export schedules to Microsoft Excel spreadsheets with advanced automatic formatting'
        ],
        details: {
            maxNumPediatricians: 999,
            maxNumShiftsPerDay: 999,
            maxNumScheduleRequests: 999
        }
    },
    {
        name: 'custom',
        price: 'Contact Sales',
        titleBg: 'linear-gradient(45deg, #a463c7, #2241ad)',
        link: '/support/contact?query_type=custom_plan',
        features: [
            'Tailored for your needs',
            'Custom shifts',
            'Custom schedule limit',
            'Dedicated support',
            'Custom notifications',
            'Custom integration with external platforms',
            'Export schedules to Microsoft Excel spreadsheets with custom automatic formatting',
            'Price evaluated based on your ROI'
        ]
    }
]
export const FREE_TIER_DETAILS = {
    maxNumPediatricians: 10,
    maxNumShiftsPerDay: 4,
    maxNumScheduleRequests: 2
}

export const PLAN_EXPIRED_MODAL_CONTENT = <>
    <h1>Your Subscription Has Expired</h1>
    <p>
        Your access has been paused because your subscription has expired.
        Renew now to continue enjoying all features.
    </p>
    <button>Renew or Upgrade Now</button>
</>