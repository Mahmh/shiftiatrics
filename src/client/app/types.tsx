import type { SetStateAction, Dispatch, ReactNode } from 'react'

type SetState<T> = Dispatch<SetStateAction<T>>
export type ContentName = 'schedules' | 'employees' | 'shifts' | 'account' | 'settings' | 'support'

export interface ContextProps {
    content: ContentName
    setContent: SetState<ContentName>
    account: Account
    setAccount: SetState<Account>
    employees: Employee[],
    setEmployees: SetState<Employee[]>
    isModalOpen: boolean
    setIsModalOpen: SetState<boolean>
    modalContent: ReactNode,
    setModalContent: SetState<ReactNode>
    openModal: () => void
    closeModal: () => void
    loadEmployees: () => void
}

export interface Account {
    id: number
    username: string
    password: string
}

export interface Employee {
    id: number
    name: string
}