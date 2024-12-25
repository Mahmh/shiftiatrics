'use client'
import { useState, createContext, ReactNode, useEffect } from 'react'
import type { ContextProps, ContentName, Employee, Account, Shift } from '@types'
import { Request } from '@utils'

const defaultContent: ContentName = 'schedules'
const nullAccount: Account = { id: 1, username: 'string', password: 'string' }
const nullEmployees: Employee[] = []
const nullShifts: Shift[] = []

export const AppContext = createContext<ContextProps>({
    content: defaultContent,
    setContent: () => {},

    account: nullAccount,
    setAccount: () => {},

    employees: [],
    setEmployees: () => {},
    loadEmployees: () => {},

    shifts: [],
    setShifts: () => {},
    loadShifts: () => {},

    isModalOpen: false,
    setIsModalOpen: () => {},
    modalContent: null,
    setModalContent: () => {},
    openModal: () => {},
    closeModal: () => {}
})

export function AppProvider({ children }: Readonly<{children: React.ReactNode}>) {
    const [content, setContent] = useState<ContentName>(defaultContent)
    const [account, setAccount] = useState<Account>(nullAccount)
    const [employees, setEmployees] = useState<Employee[]>(nullEmployees)
    const [shifts, setShifts] = useState<Shift[]>(nullShifts)
    const [isModalOpen, setIsModalOpen] = useState(false)
    const [modalContent, setModalContent] = useState<ReactNode>(null)

    const openModal = () => setIsModalOpen(true)
    const closeModal = () => setIsModalOpen(false)

    const loadEmployees = async () => {
        await new Request(`accounts/${account.id}/employees`, (data: any[]) => {
            setEmployees(data.map(emp => ({
                id: emp.employee_id,
                name: emp.employee_name}
            )))
        }).get()
    }

    const loadShifts = async () => {
        await new Request(`accounts/${account.id}/shifts`, (data: any[]) => {
            setShifts(data.map(shift => ({
                id: shift.shift_id,
                name: shift.shift_name,
                startTime: shift.start_time,
                endTime: shift.end_time
            })))
        }).get()
    }

    useEffect(() => {
        loadEmployees()
        loadShifts()
    }, [])

    return (
        <AppContext.Provider value={{
            account, setAccount,
            content, setContent,
            employees, setEmployees, loadEmployees,
            shifts, setShifts, loadShifts,
            isModalOpen, setIsModalOpen,
            modalContent, setModalContent,
            openModal, closeModal
        }}>{children}</AppContext.Provider>
    )
}