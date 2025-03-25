import { PricingPlanName, PricingPlan, PlanDetails } from '@types'

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
        link: '/signup',
        features: [
            'Up to 10 pediatricians',
            '3 shifts per day',
            'Generate, update, or delete schedules up to 20 times per month.',
            // 'Basic support',
            'Export schedules to Microsoft Excel spreadsheets with simple automatic formatting'
        ],
        details: {
            maxNumPediatricians: 10,
            maxNumShiftsPerDay: 3,
            maxNumScheduleRequests: 20
        }
    },
    {
        name: 'standard',
        price: 49.99,
        titleBg: 'linear-gradient(45deg, #217cff, #5ca7ff)',
        link: '/signup',
        features: [
            'Up to 25 pediatricians',
            '4 shifts per day',
            'Generate, update, or delete schedules up to 60 times per month',
            // 'Priority support',
            'E-mail notifications',
            // 'Integration with external platforms',
            'Export schedules to Microsoft Excel spreadsheets with better automatic formatting'
        ],
        details: {
            maxNumPediatricians: 25,
            maxNumShiftsPerDay: 4,
            maxNumScheduleRequests: 60
        }
    },
    {
        name: 'premium',
        price: 99.99,
        titleBg: 'linear-gradient(45deg, #607eff, #47dbf3)',
        link: '/signup',
        features: [
            'Unlimited pediatricians',
            'Unlimited shifts per day',
            'Generate, update, or delete schedules without limits each month',
            // 'Priority support',
            'E-mail notifications',
            // 'Integration with external platforms',
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
            // 'Custom integration with external platforms',
            'Export schedules to Microsoft Excel spreadsheets with custom automatic formatting',
            'Price evaluated based on your ROI'
        ]
    }
]

export const FREE_TIER_DETAILS: PlanDetails = {
    maxNumPediatricians: 3,
    maxNumShiftsPerDay: 2,
    maxNumScheduleRequests: 8
}