'use client'
import { useState, createContext } from 'react'
import type { ContextProps, ContentName, Employee, Account } from '@types'

const defaultContent: ContentName = 'schedules'
const nullAccount: Account = { username: '', password: '' }
const nullEmployees: Employee[] = []

export const AppContext = createContext<ContextProps>({
    content: defaultContent,
    setContent: () => {},
    account: nullAccount,
    setAccount: () => {},
    employees: [],
    setEmployees: () => {}
})

export function AppProvider({ children }: Readonly<{children: React.ReactNode}>) {
    const [content, setContent] = useState<ContentName>(defaultContent)
    const [account, setAccount] = useState<Account>(nullAccount)
    const [employees, setEmployees] = useState<Employee[]>(nullEmployees)

    return (
        <AppContext.Provider value={{
            account, setAccount,
            content, setContent,
            employees, setEmployees
        }}>{children}</AppContext.Provider>
    )
}