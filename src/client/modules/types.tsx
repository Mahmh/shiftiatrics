import type { SetStateAction, Dispatch, ReactNode, ChangeEvent } from 'react'

// Types
type SetState<T> = Dispatch<SetStateAction<T>>
export type ReadonlyChildren = Readonly<{children: React.ReactNode}>
export type EndpointResponse = object | { error: string }
export type InputEvent = ChangeEvent<HTMLInputElement>
export type AccountAndSubResponse = { account: AccountResponse, subscription: SubscriptionResponse | null }
export type AccountAndSub = { account: Account, subscription: Subscription | null }

export type MonthName = 'January' | 'February' | 'March' | 'April' | 'May'| 'June' | 'July' | 'August' | 'September' | 'October' | 'November' | 'December'
export type WeekendDays =  'Saturday & Sunday' | 'Friday & Saturday' | 'Sunday & Monday'
export type Interval =  'Daily' | 'Weekly' | 'Monthly'
export type SupportedExportFormat = 'csv' | 'tsv' | 'json' | 'xlsx'
export type ContentName = 'schedules' | 'employees' | 'shifts' | 'holidays' | 'settings' | 'support' | 'subscription'
export type PricingPlanName = 'basic' | 'standard' | 'premium' | 'custom'

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

    subscription: Subscription | null
    setSubscription: SetState<Subscription | null>

    employees: Employee[]
    setEmployees: SetState<Employee[]>
    loadEmployees: () => void
    validateEmployeeById: (id: number, employees: Employee[], year: number, month: number) => Employee

    shifts: Shift[]
    setShifts: SetState<Shift[]>
    loadShifts: () => void

    schedules: YearToSchedules
    setSchedules: SetState<YearToSchedules>
    setScheduleValidity: (validity: boolean, year: number, month: number) => void
    getScheduleValidity: (year: number, month: number) => boolean | undefined

    holidays: Holiday[]
    setHolidays: SetState<Holiday[]>
    loadHolidays: () => void

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

export interface AccountResponse {
    account_id: number
    email: string
    hashed_password: string | null
    email_verified: boolean
    oauth_provider: string
}

export interface SubscriptionResponse {
    subscription_id: number
    account_id: number
    plan: PricingPlanName
    price: number
    created_at: string
    expires_at: string
    plan_details: {
        max_num_pediatricians: number
        max_num_shifts_per_day: number
        max_num_schedule_requests: number
    }
}

export interface Account {
    id: number
    email: string
    emailVerified: boolean
    isOAuthOnly: boolean
}

export interface Employee {
    id: number
    name: string
    minWorkHours?: number
    maxWorkHours?: number
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
    minMaxWorkHoursEnabled: boolean
    multiEmpsInShiftEnabled: boolean
    multiShiftsOneEmpEnabled: boolean
    weekendDays: WeekendDays
    maxEmpsInShift: number
    emailNtfEnabled: boolean
    emailNtfInterval: Interval
}

export interface FAQ {
    question: string
    answer: string | null
}


// Subscription & Plans
export interface PlanDetails {
    maxNumPediatricians: number
    maxNumShiftsPerDay: number
    maxNumScheduleRequests: number
}

export interface PricingPlan {
    name: PricingPlanName
    price: number | string
    titleBg: string
    link: string
    features: string[]
    details?: PlanDetails
}

export interface SubscriptionInfo {
    plan: PricingPlanName
    price: number
    planDetails: PlanDetails
}

export interface Subscription extends SubscriptionInfo {
    id: number
    createdAt: string
    expiresAt: string
}