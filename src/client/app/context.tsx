'use client'
import { useState, createContext, ReactNode, useEffect, useCallback } from 'react'
import type { ContextProps, ContentName, Employee, Account, Shift, Schedule, YearToSchedules, YearToSchedulesValidity, ScheduleOfIDs } from '@types'
import { isLoggedIn, Request, getEmployeeById, hasScheduleForMonth } from '@utils'

const defaultContent: ContentName = 'schedules'
const nullEmployee: Employee = { id: -Infinity, name: '' }
export const nullAccount: Account = { id: -Infinity, username: '', password: '' }

export const AppContext = createContext<ContextProps>({
    content: defaultContent,
    setContent: () => {},

    account: nullAccount,
    setAccount: () => {},

    employees: [],
    setEmployees: () => {},
    loadEmployees: () => {},
    validateEmployeeById: () => nullEmployee,

    shifts: [],
    setShifts: () => {},
    loadShifts: () => {},

    schedules: new Map(),
    setSchedules: () => {},
    loadSchedules: async () => {},
    setScheduleValidity: () => {},
    getScheduleValidity: () => undefined,

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
    const [employees, setEmployees] = useState<Employee[]>([])
    const [shifts, setShifts] = useState<Shift[]>([])
    const [schedules, setSchedules] = useState<YearToSchedules>(new Map())
    const [schedulesValidity, setSchedulesValidity] = useState<YearToSchedulesValidity>(new Map())
    const [isModalOpen, setIsModalOpen] = useState(false)
    const [modalContent, setModalContent] = useState<ReactNode>(null)

    const openModal = useCallback(() => setIsModalOpen(true), [])
    const closeModal = useCallback(() => setIsModalOpen(false), [])

    /** Collects whether a schedule is valid  */
    const setScheduleValidity = useCallback((validity: boolean, year: number, month: number) => {
        setSchedulesValidity((prev) => {
            const updatedValidity = new Map(prev)
            if (!updatedValidity.has(year)) updatedValidity.set(year, new Map())
            const yearValidity = updatedValidity.get(year)!
            yearValidity.set(month, validity)
            return updatedValidity
        })
    }, [])
    
    /** Returns whether a schedule is valid */
    const getScheduleValidity = useCallback((year: number, month: number): boolean | undefined => {
        if (!hasScheduleForMonth(schedules, year, month)) return true
        return schedulesValidity.get(year)?.get(month)
    }, [schedules, schedulesValidity])

    /** Helper function for showing an invalid message if any employee is missing */
    const validateEmployeeById = useCallback((id: number, employees: Employee[], year: number, month: number): Employee => {
        if (employees.length === 0) return nullEmployee
        let name = getEmployeeById(id, employees)?.name
        if (typeof name === 'undefined') {
            name = 'Unknown'
            setScheduleValidity(false, year, month)
        }
        return { id, name }
    }, [setScheduleValidity])

    const loadEmployees = useCallback(async (): Promise<Employee[]> => {
        return new Promise(async (resolve) => {
            type Response = { employee_id: Employee['id'], employee_name: Employee['name'] }[];
            await new Request(`accounts/${account.id}/employees`, (data: Response) => {
                const loadedEmployees = data.map(emp => ({ id: emp.employee_id, name: emp.employee_name }))
                setEmployees(loadedEmployees)
                resolve(loadedEmployees)
            }).get()
        })
    }, [account.id])

    const loadShifts = useCallback(async () => {
        type Response = { shift_id: Shift['id'], shift_name: Shift['name'], start_time: Shift['startTime'], end_time: Shift['endTime'] }[];
        await new Request(`accounts/${account.id}/shifts`, (data: Response) => {
            setShifts(data.map(shift => ({
                id: shift.shift_id,
                name: shift.shift_name,
                startTime: shift.start_time,
                endTime: shift.end_time
            })))
        }).get()
    }, [account.id])

    const loadSchedules = useCallback(async (employees: Employee[]) => {
        type Response = { account_id: Account['id'], schedule_id: Schedule['id'], month: number, year: number, schedule: ScheduleOfIDs }[];
        await new Request(`accounts/${account.id}/schedules`, (data: Response) => {
            const parsedSchedules = new Map<number, Schedule[]>()
    
            data.forEach(scheduleData => {
                const { schedule_id: scheduleId, month, year } = scheduleData
    
                // Initialize validity for this schedule as true
                setScheduleValidity(true, year, month)
    
                // Transform schedule data to match Employee[][]
                const parsedSchedule = scheduleData.schedule.map((day: number[]) =>
                    day.map(empId => validateEmployeeById(empId, employees, year, month))
                )
    
                // Ensure the year exists in the maps
                if (!parsedSchedules.has(year)) parsedSchedules.set(year, [])
                if (!schedulesValidity.has(year)) {
                    const map = new Map<number, boolean>()
                    for (let i = 0; i < 12; i++) map.set(i, true)
                    schedulesValidity.set(year, map)
                }
    
                const yearSchedules = parsedSchedules.get(year)!
                yearSchedules[month] = {
                    id: scheduleId,
                    schedule: parsedSchedule,
                }
            })

            setSchedules(parsedSchedules)
        }).get()
    }, [account.id, schedulesValidity, validateEmployeeById, setScheduleValidity])

    useEffect(() => {
        const fetchAllData = async () => {
            if (isLoggedIn(account)) {
                const loadedEmployees = await loadEmployees()
                await loadShifts()
                await loadSchedules(loadedEmployees)
            }
        }
        fetchAllData()
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [account])


    useEffect(() => {
        const regenerateSchedules = async () => {
            if (isLoggedIn(account) && employees.length > 0) await loadSchedules(employees)
        }
        regenerateSchedules()
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [employees, shifts, account])

    return (
        <AppContext.Provider value={{
            account, setAccount,
            content, setContent,
            employees, setEmployees, loadEmployees, validateEmployeeById,
            shifts, setShifts, loadShifts,
            isModalOpen, setIsModalOpen,
            modalContent, setModalContent,
            openModal, closeModal,
            schedules, setSchedules, loadSchedules, setScheduleValidity, getScheduleValidity
        }}>{children}</AppContext.Provider>
    )
}