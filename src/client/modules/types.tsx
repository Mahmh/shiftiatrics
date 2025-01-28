import type { SetStateAction, Dispatch, ReactNode, ChangeEvent } from 'react'

// Types
type SetState<T> = Dispatch<SetStateAction<T>>
export type ReadonlyChildren = Readonly<{children: React.ReactNode}>
export type EndpointResponse = object | { error: string }
export type InputEvent = ChangeEvent<HTMLInputElement>

export type MonthName = 'January' | 'February' | 'March' | 'April' | 'May'| 'June' | 'July' | 'August' | 'September' | 'October' | 'November' | 'December'
export type WeekendDays =  'Saturday & Sunday' | 'Friday & Saturday' | 'Sunday & Monday'
export type SupportedExportFormat = 'csv' | 'tsv' | 'json' | 'xlsx'
export type ContentName = 'schedules' | 'employees' | 'shifts' | 'holidays' | 'settings' | 'support'

export type ShiftCounts = Map<Employee, number>
export type ScheduleOfIDs = Employee['id'][][][]
export type YearToSchedules = Map<number, Schedule[]>
export type YearToSchedulesValidity = Map<number, Map<number, boolean>>


// Context
export interface ContextProps {
    content: ContentName
    setContent: SetState<ContentName>

    account: Account
    setAccount: SetState<Account>

    employees: Employee[]
    setEmployees: SetState<Employee[]>
    loadEmployees: () => void
    validateEmployeeById: (id: number, employees: Employee[], year: number, month: number) => Employee

    shifts: Shift[]
    setShifts: SetState<Shift[]>
    loadShifts: () => void

    schedules: YearToSchedules,
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


// Entities
export interface Account {
    id: number
    username: string
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
}