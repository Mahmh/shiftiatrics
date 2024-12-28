import type { SetStateAction, Dispatch, ReactNode } from 'react'

// Types
type SetState<T> = Dispatch<SetStateAction<T>>
export type MonthName = 'January' | 'February' | 'March' | 'April' | 'May'| 'June' | 'July' | 'August' | 'September' | 'October' | 'November' | 'December'
export type SupportedExportFormat = 'csv' | 'tsv' | 'json' | 'xlsx'
export type ContentName = 'schedules' | 'employees' | 'shifts' | 'account' | 'settings' | 'support'
export type ShiftCounts = Map<Employee, number>
export type ScheduleOfIDs = Employee['id'][][]
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
    loadSchedules: (employees: Employee[]) => Promise<void>
    setScheduleValidity: (validity: boolean, year: number, month: number) => void
    getScheduleValidity: (year: number, month: number) => boolean | undefined

    isModalOpen: boolean
    setIsModalOpen: SetState<boolean>
    modalContent: ReactNode,
    setModalContent: SetState<ReactNode>
    openModal: () => void
    closeModal: () => void
}


// Entities
export interface Account {
    id: number
    username: string
    password: string
}

export interface Employee {
    id: number
    name: string
}

export interface Shift {
    id: number
    name: string
    startTime: string
    endTime: string
}

export interface Schedule {
    id: number
    schedule: Employee[][]
}