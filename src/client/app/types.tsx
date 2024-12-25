import type { SetStateAction, Dispatch } from 'react'

type SetState<T> = Dispatch<SetStateAction<T>>
export type ContentName = 'schedules' | 'employees' | 'shifts' | 'account' | 'settings' | 'support'

export interface ContextProps {
    content: ContentName
    setContent: SetState<ContentName>
    account: Account
    setAccount: SetState<Account>
    employees: Employee[],
    setEmployees: SetState<Employee[]>
}

export interface Account {
    username: string
    password: string
}

export interface Employee {
    name: string
}