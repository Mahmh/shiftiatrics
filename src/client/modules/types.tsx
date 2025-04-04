import type { SetStateAction, Dispatch, ReactNode, ChangeEvent } from 'react'
import { QUERY_TYPES, PLAN_NAMES } from '@const'

// Types
type SetState<T> = Dispatch<SetStateAction<T>>
type InvoiceStatus = 'draft' | 'open' | 'paid' | 'uncollectible' | 'void'

export type ReadonlyChildren = Readonly<{children: React.ReactNode}>
export type EndpointResponse = object | { error: string }
export type InputEvent = ChangeEvent<HTMLInputElement>
export type AccountAndSubResponse = { account: AccountResponse, subscription: SubscriptionResponse | null }
export type AccountAndSub = { account: Account, subscription: Subscription }

export type QueryType = typeof QUERY_TYPES[number]
export type PlanName = typeof PLAN_NAMES[number]
export type MonthName = 'January' | 'February' | 'March' | 'April' | 'May'| 'June' | 'July' | 'August' | 'September' | 'October' | 'November' | 'December'
export type WeekendDays =  'Saturday & Sunday' | 'Friday & Saturday' | 'Sunday & Monday'
export type Interval =  'Daily' | 'Weekly' | 'Monthly'
export type SupportedExportFormat = 'csv' | 'tsv' | 'json' | 'xlsx'
export type ContentName = 'schedules' | 'employees' | 'shifts' | 'holidays' | 'settings' | 'support' | 'subscription'

export type ShiftCounts = Map<Employee, number>
export type ScheduleOfIDs = Employee['id'][][][]
export type YearToSchedules = Map<number, Schedule[]>
export type YearToSchedulesValidity = Map<number, Map<number, boolean>>


// Interfaces
export interface ContextProps {
    content: ContentName
    setContent: SetState<ContentName>

    account: Account
    setAccount: SetState<Account>

    subscription: Subscription
    setSubscription: SetState<Subscription>
    invoices: StripeInvoice[]

    employees: Employee[]
    setEmployees: SetState<Employee[]>
    validateEmployeeById: (id: number, employees: Employee[], year: number, month: number) => Employee

    shifts: Shift[]
    setShifts: SetState<Shift[]>

    schedules: YearToSchedules
    setSchedules: SetState<YearToSchedules>
    setScheduleValidity: (validity: boolean, year: number, month: number) => void
    getScheduleValidity: (year: number, month: number) => boolean | undefined

    holidays: Holiday[]
    setHolidays: SetState<Holiday[]>
    loadHolidays: (account: Account) => void

    settings: Settings
    setSettings: SetState<Settings>
    darkThemeClassName: string

    screenWidth: number
    isMenuShown: boolean
    setIsMenuShown: SetState<boolean>

    isModalOpen: boolean
    setIsModalOpen: SetState<boolean>
    modalContent: ReactNode
    setModalContent: SetState<ReactNode>
    openModal: () => void
    closeModal: () => void
}

export interface Account {
    id: number
    email: string
    emailVerified: boolean
    passwordChanged: boolean
    subExpired: boolean
}

export interface Employee {
    id: number
    name: string
    minWorkHours: number
    maxWorkHours: number
}

export interface Shift {
    id: number
    name: string
    startTime: string
    endTime: string
}

export interface Schedule {
    id: number
    schedule: Employee[][][]
}

export interface Holiday {
    id: number
    name: string
    assignedTo: number[]
    startDate: string
    endDate: string
}

export interface Settings {
    darkThemeEnabled: boolean
    weekendDays: WeekendDays
}

export interface FAQ {
    question: string
    answer: string | null
}

export interface Plan {
    name: PlanName
    price: number | string
    titleBg: string
    link?: string
    features: string[]
}

export interface Subscription {
    id: number
    plan: PlanName
    createdAt: string
    expiresAt: string
}

export interface SubscriptionResponse {
    subscription_id: number
    account_id: number
    plan: PlanName
    created_at: string
    expires_at: string
}

export interface StripeInvoiceResponse {
    invoice_id: string
    amount_due: number           // In dollars (float)
    amount_paid: number          // In dollars (float)
    currency: string             // Always uppercase, e.g. "USD"
    status: InvoiceStatus
    invoice_pdf: string          // Direct link to downloadable PDF
    hosted_invoice_url: string   // Stripe-hosted invoice page
    created_at: string           // ISO timestamp
    due_date: string | null      // ISO timestamp or null
    description: string | null   // Optional description
    subscription_id: string      // Stripe subscription ID
}

export interface StripeInvoice {
    invoiceId: string
    amountDue: number
    amountPaid: number
    currency: string
    status: InvoiceStatus
    invoicePdf: string
    hostedInvoiceUrl: string
    createdAt: string
    dueDate: string | null
    description: string | null
    subscriptionId: string
}


// Responses
export interface AccountResponse {
    account_id: number
    email: string
    email_verified: boolean
    password_changed: boolean
    sub_expired: boolean
}

export interface SubscriptionResponse {
    subscription_id: number
    account_id: number
    plan: PlanName
    created_at: string
    expires_at: string
}

export interface EmployeeResponse {
    employee_id: number
    employee_name: string
    min_work_hours: number
    max_work_hours: number
}

export interface ShiftResponse {
    shift_id: number
    shift_name: string
    start_time: string
    end_time: string
}

export interface ScheduleResponse {
    schedule_id: number
    schedule: ScheduleOfIDs
    month: number
    year: number
}

export interface HolidayResponse {
    holiday_id: number
    holiday_name: string
    assigned_to: number[]
    start_date: string
    end_date: string
}

export interface SettingsResponse {
    dark_theme_enabled: boolean
    weekend_days: WeekendDays
}


// Parsers that convert API response properties to TSX ones
export const parseAccount = (data: AccountResponse): Account => ({
    id: data.account_id,
    email: data.email,
    emailVerified: data.email_verified,
    passwordChanged: data.password_changed,
    subExpired: data.sub_expired
})

export const parseSub = (data: SubscriptionResponse): Subscription => ({
    id: data.subscription_id,
    plan: data.plan,
    createdAt: data.created_at,
    expiresAt: data.expires_at,
})

export const parseEmployee = (data: EmployeeResponse): Employee => ({
    id: data.employee_id,
    name: data.employee_name,
    minWorkHours: data.min_work_hours,
    maxWorkHours: data.max_work_hours,
})

export const parseShift = (data: ShiftResponse): Shift => ({
    id: data.shift_id,
    name: data.shift_name,
    startTime: data.start_time,
    endTime: data.end_time,
})

export const parseHoliday = (data: HolidayResponse): Holiday => ({
    id: data.holiday_id,
    name: data.holiday_name,
    assignedTo: data.assigned_to,
    startDate: data.start_date,
    endDate: data.end_date,
})

export const parseSettings = (data: SettingsResponse): Settings => ({
    darkThemeEnabled: data.dark_theme_enabled,
    weekendDays: data.weekend_days
})

export const parseStripeInvoice = (data: StripeInvoiceResponse): StripeInvoice => ({
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
    subscriptionId: data.subscription_id,
})