import { Plan } from '@types'

export const DOMAIN_NAME = 'shiftiatrics.com'
export const MIN_YEAR = 2023
export const MAX_YEAR = 2025
export const TOO_MANY_REQS_MSG = 'You have sent too many requests. Please try again later.'

export const PLAN_NAMES = ['starter', 'growth', 'advanced', 'enterprise'] as const
export const PLANS: Plan[] = [
    {
        name: 'starter',
        price: 249,
        link: '/support/contact?query_type=starter',
        titleBg: 'linear-gradient(45deg, #72acfe, #3d7cc7)',
        features: [
            'For small teams (1–5 doctors)',
            'Standard shift setup',
            'Monthly schedule generation included',
        ],
    },
    {
        name: 'growth',
        price: 'Custom Quote',
        link: '/support/contact?query_type=growth',
        titleBg: 'linear-gradient(45deg, #217cff, #5ca7ff)',
        features: [
            'For 5–15 doctors',
            'Common rotation patterns',
            'Basic holiday and absence support',
            'Monthly schedule updates',
        ],
    },
    {
        name: 'advanced',
        price: 'Custom Quote',
        link: '/support/contact?query_type=advanced',
        titleBg: 'linear-gradient(45deg, #607eff, #47dbf3)',
        features: [
            'For 15+ doctors',
            'Custom shift rules and rotation logic',
            'Advanced fairness and fatigue constraints',
            'Weekly schedule adjustments',
        ],
    },
    {
        name: 'enterprise',
        price: 'Custom Quote',
        link: '/support/contact?query_type=enterprise',
        titleBg: 'linear-gradient(45deg, #a463c7, #2241ad)',
        features: [
            'White-glove onboarding',
            'Integrations with internal systems',
            'Custom notifications and exports',
            'Dedicated support team',
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
    'Register a Pediatrican',
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
    'Unable to Log In',
    'Integration Request',
    'Customization Inquiry',
    'Data & Privacy Concerns',
    'Job & Career Opportunities',
    'Other'
] as const