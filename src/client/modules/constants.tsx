import { Plan } from '@types'

const CURRENT_YEAR = new Date().getFullYear()
export const MIN_YEAR = CURRENT_YEAR - 2
export const MAX_YEAR = CURRENT_YEAR + 2
export const TOO_MANY_REQS_MSG = 'You have sent too many requests. Please try again later.'
export const DOMAIN_NAME = 'shiftiatrics.com'

export const WEEKDAY_NAMES = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'] as const
export const MONTH_NAMES = [
    'January', 'February', 'March', 'April', 'May', 'June', 
    'July', 'August', 'September', 'October', 'November', 'December'
] as const

export const PLAN_NAMES = ['starter', 'growth', 'advanced', 'enterprise'] as const
export const PLANS: Plan[] = [
    {
        name: 'starter',
        price: 79,
        link: '/support/contact?query_type=starter_plan',
        titleBg: 'linear-gradient(45deg, #72acfe, #3d7cc7)',
        features: [
            'Up to 6 staff members',
            'One staff team',
            'D/E/N shift types',
            'Manual holiday assignment',
            'Standard schedule format',
            'Standard support'
        ],
    },
    {
        name: 'growth',
        price: 149,
        link: '/support/contact?query_type=growth_plan',
        titleBg: 'linear-gradient(45deg, #217cff, #5ca7ff)',
        features: [
            'Up to 20 staff members',
            'Up to 3 staff teams',
            'D/E/N shift types',
            'Manual holiday assignment',
            'Minor formatting requests',
            'Standard support'
        ],
    },
    {
        name: 'advanced',
        price: 249,
        link: '/support/contact?query_type=advanced_plan',
        titleBg: 'linear-gradient(45deg, #607eff, #47dbf3)',
        features: [
            'Up to 50 staff members',
            'Up to 6 staff teams',
            'D/E/N shift types',
            'Manual holiday assignment',
            'Custom schedule output formats',
            'Standard support'
        ],
    },
    {
        name: 'enterprise',
        price: 'Custom Quote',
        link: '/support/contact?query_type=enterprise_plan',
        titleBg: 'linear-gradient(45deg, #a463c7, #2241ad)',
        features: [
            'Unlimited staff members and teams',
            'D/E/N shift types (or custom shift configurations)',
            'Automatic holiday assignment',
            'Custom integrations with hospital systems',
            'Full custom formatting support',
            'Dedicated priority support team'
        ],
    }
]

export const QUERY_TYPES = [
    'General Inquiry',
    'Starter Plan',
    'Growth Plan',
    'Advanced Plan',
    'Enterprise Plan',
    'Change My Plan',
    'Register Staff',
    'Register a Daily Shift',
    'Technical Issue',
    'Bug Report',
    'Feature Suggestion',
    'Feature Feedback',
    'Business Inquiry',
    'Partnership & Collaboration',
    'Billing & Payment Issue',
    'Refund Request',
    'Account Access Issue',
    'Implement Algorithm for Account',
    'Integration Request',
    'Customization Inquiry',
    'Data & Privacy Concerns',
    'Job & Career Opportunities',
    'Other'
] as const