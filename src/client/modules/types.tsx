import type { SetStateAction, Dispatch, ReactNode, ChangeEvent } from 'react'
import { QUERY_TYPES, PLAN_NAMES } from '@const'

// Types
type SetState<T> = Dispatch<SetStateAction<T>>

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

    employees: Employee[]
    setEmployees: SetState<Employee[]>
    loadEmployees: (account: Account) => void
    validateEmployeeById: (id: number, employees: Employee[], year: number, month: number) => Employee

    shifts: Shift[]
    setShifts: SetState<Shift[]>
    loadShifts: (account: Account) => void

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

export interface AccountResponse {
    account_id: number
    email: string
    email_verified: boolean
    sub_expired: boolean
}

export interface SubscriptionResponse {
    subscription_id: number
    account_id: number
    plan: PlanName
    created_at: string
    expires_at: string
}

export interface SettingsResponse {
    dark_theme_enabled: boolean
    weekend_days: WeekendDays
}
  

export interface Account {
    id: number
    email: string
    emailVerified: boolean
    subExpired: boolean
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