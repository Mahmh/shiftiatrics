'use client'
import { useState, createContext, ReactNode, useEffect, useCallback, useMemo } from 'react'
import { usePathname, useRouter } from 'next/navigation'
import { Request, getEmployeeById, getUIDate, hasScheduleForMonth } from '@utils'
import { isLoggedIn } from '@auth'
import type { ContextProps, ContentName, Employee, Account, Shift, Schedule, Holiday, Settings, YearToSchedules, YearToSchedulesValidity, ScheduleOfIDs, WeekendDays, ReadonlyChildren, Interval, Subscription } from '@types'

// Context for dashboard content
const defaultContent: ContentName = 'schedules'
const nullEmployee: Employee = { id: -Infinity, name: '', minWorkHours: Infinity, maxWorkHours: Infinity }
export const nullSettings: Settings = {
    darkThemeEnabled: false,
    minMaxWorkHoursEnabled: true,
    multiEmpsInShiftEnabled: false,
    multiShiftsOneEmpEnabled: false,
    weekendDays: 'Friday & Saturday',
    maxEmpsInShift: 1,
    emailNtfEnabled: false,
    emailNtfInterval: 'Monthly'
}
export const nullSub: Subscription = {
    id: -Infinity,
    plan: 'basic',
    price: -Infinity,
    planDetails: { maxNumPediatricians: -Infinity, maxNumShiftsPerDay: -Infinity, maxNumScheduleRequests: -Infinity },
    createdAt: '',
    expiresAt: ''
}
export const nullAccount: Account = { id: -Infinity, email: '', emailVerified: false, isOAuthOnly: false, hasUsedTrial: false, subExpired: false }

export const dashboardContext = createContext<ContextProps>({
    content: defaultContent,
    setContent: () => {},

    account: nullAccount,
    setAccount: () => {},

    subscription: nullSub,
    setSubscription: () => {},

    employees: [],
    setEmployees: () => {},
    loadEmployees: () => {},
    validateEmployeeById: () => nullEmployee,

    shifts: [],
    setShifts: () => {},
    loadShifts: () => {},

    schedules: new Map(),
    setSchedules: () => {},
    setScheduleValidity: () => {},
    getScheduleValidity: () => undefined,

    holidays: [],
    setHolidays: () => {},
    loadHolidays: () => {},

    settings: nullSettings,
    setSettings: () => {},
    darkThemeClassName: '',

    screenWidth: 0,
    isMenuShown: false,
    setIsMenuShown: () => {},

    isModalOpen: false,
    setIsModalOpen: () => {},
    modalContent: null,
    setModalContent: () => {},
    openModal: () => {},
    closeModal: () => {}
})

export function DashboardProvider({ children }: ReadonlyChildren) {
    const [hydrated, setHydrated] = useState(false)
    const [content, setContent] = useState<ContentName>(defaultContent)
    const [account, setAccount] = useState<Account>(nullAccount)
    const [subscription, setSubscription] = useState<Subscription | null>(nullSub)
    const [employees, setEmployees] = useState<Employee[]>([])
    const [shifts, setShifts] = useState<Shift[]>([])
    const [schedules, setSchedules] = useState<YearToSchedules>(new Map())
    const [holidays, setHolidays] = useState<Holiday[]>([])
    const [schedulesValidity, setSchedulesValidity] = useState<YearToSchedulesValidity>(new Map())
    const [settings, setSettings] = useState(nullSettings)
    const [isModalOpen, setIsModalOpen] = useState(false)
    const [modalContent, setModalContent] = useState<ReactNode>(null)
    const [screenWidth, setScreenWidth] = useState(typeof window !== 'undefined' ? window.innerWidth : 0)
    const [isMenuShown, setIsMenuShown] = useState(screenWidth > 950)
    const router = useRouter()
    const darkThemeClassName = useMemo(() => settings.darkThemeEnabled ? 'dark-theme' : '', [settings.darkThemeEnabled])
    const openModal = useCallback(() => setIsModalOpen(true), [])
    const closeModal = useCallback(() => setIsModalOpen(false), [])
    const pathname = usePathname()

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
        const employee = getEmployeeById(id, employees)
        let name = employee?.name
        const minWorkHours = employee?.minWorkHours
        const maxWorkHours = employee?.maxWorkHours
        if (typeof name === 'undefined') {
            name = 'Unknown'
            setScheduleValidity(false, year, month)
        }
        return { id, name, minWorkHours, maxWorkHours }
    }, [setScheduleValidity])

    const loadEmployees = useCallback(async (account: Account): Promise<Employee[]> => {
        if (account.id === -Infinity) return []
        return new Promise(async (resolve) => {
            type Response = {
                employee_id: Employee['id'],
                employee_name: Employee['name'],
                min_work_hours: Employee['minWorkHours'],
                max_work_hours: Employee['maxWorkHours']
            }[];
            await new Request(`accounts/${account.id}/employees`, (data: Response) => {
                const loadedEmployees = data.map(emp => ({
                    id: emp.employee_id,
                    name: emp.employee_name,
                    minWorkHours: emp.min_work_hours,
                    maxWorkHours: emp.max_work_hours
                }))
                setEmployees(loadedEmployees)
                resolve(loadedEmployees)
            }).get()
        })
    }, [account.id])

    const loadShifts = useCallback(async (account: Account) => {
        if (account.id === -Infinity) return []
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

    const loadSchedules = useCallback(async (account: Account, employees: Employee[]) => {
        if (account.id === -Infinity) return []
        type Response = { account_id: Account['id'], schedule_id: Schedule['id'], month: number, year: number, schedule: ScheduleOfIDs }[];
        await new Request(`accounts/${account.id}/schedules`, (data: Response) => {
            const parsedSchedules = new Map<number, Schedule[]>()

            data.forEach(scheduleData => {
                const { schedule_id: scheduleId, month, year } = scheduleData

                // Initialize validity for this schedule as true
                setScheduleValidity(true, year, month)

                // Transform schedule data to match Employee['id'][][][]
                const parsedSchedule = scheduleData.schedule.map((day: number[][]) =>
                    day.map((shift: number[]) =>
                        shift.map(empId => validateEmployeeById(empId, employees, year, month))
                    )
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

    const loadHolidays = useCallback(async (account: Account) => {
        if (account.id === -Infinity) return []
        type Response = {
            holiday_id: Holiday['id'],
            holiday_name: Holiday['name'],
            assigned_to: Holiday['assignedTo'],
            start_date: Holiday['startDate'],
            end_date: Holiday['endDate']
        }[];
        await new Request(`accounts/${account.id}/holidays`, (data: Response) => {
            setHolidays(data.map(h => ({
                id: h.holiday_id,
                name: h.holiday_name,
                assignedTo: h.assigned_to,
                startDate: h.start_date,
                endDate: h.end_date
            })))
        }).get()
    }, [account.id])

    const loadSettings = useCallback(async (account: Account) => {
        if (account.id === -Infinity) return []
        type Response = { detail: null } | {
            dark_theme_enabled: boolean,
            min_max_work_hours_enabled: boolean
            multi_emps_in_shift_enabled: boolean
            multi_shifts_one_emp_enabled: boolean
            weekend_days: WeekendDays
            max_emps_in_shift: number
            email_ntf_enabled: boolean
            email_ntf_interval: Interval
        };
        await new Request(
            `accounts/${account.id}/settings`,
            (data: Response) => {
                if ('detail' in data) return
                setSettings({
                    darkThemeEnabled: data.dark_theme_enabled,
                    minMaxWorkHoursEnabled: data.min_max_work_hours_enabled,
                    multiEmpsInShiftEnabled: data.multi_emps_in_shift_enabled,
                    multiShiftsOneEmpEnabled: data.multi_shifts_one_emp_enabled,
                    weekendDays: data.weekend_days,
                    maxEmpsInShift: data.max_emps_in_shift,
                    emailNtfEnabled: data.email_ntf_enabled,
                    emailNtfInterval: data.email_ntf_interval
                })
            }
        ).get()
    }, [account.id, setSettings])

    const checkIsSubExpiringSoon = useCallback((subscription: Subscription) => {
        const now = new Date()
        const expiryDate = new Date(subscription.expiresAt)
        const timeDiff = expiryDate.getTime() - now.getTime()
        const daysLeft = Math.floor(timeDiff / (1000 * 60 * 60 * 24))
        if (daysLeft === 3) {
            setModalContent(<>
                <h1>Subscription Expiring Soon</h1>
                <p>
                    Your current plan will expire in {daysLeft} day(s) on {getUIDate(expiryDate)}.
                    To avoid service interruptions, upgrade now and continue enjoying all features.
                </p>
                <button>Renew or Upgrade Now</button>
            </>)
            openModal()
        }
    }, [openModal, setModalContent])

    useEffect(() => {
        setHydrated(true)
        const fetchAllData = async () => {
            if (!['/dashboard', '/login', '/signup'].includes(pathname)) return

            const res = await isLoggedIn()
            if (res === false) {
                document.body.classList.remove('logged-in')
                document.documentElement.classList.remove('logged-in')
                if (pathname === '/dashboard') router.push('/')
                return
            }

            if (['/login', '/signup'].includes(pathname)) {
                router.push('/dashboard')
                return
            }

            setAccount(res.account)
            setSubscription(res.subscription)
            if (res.subscription !== null) checkIsSubExpiringSoon(res.subscription)

            const loadedEmployees = await loadEmployees(res.account)
            await loadShifts(res.account)
            await loadSchedules(res.account, loadedEmployees)
            await loadHolidays(res.account)
            await loadSettings(res.account)

            document.body.classList.add('logged-in')
            document.documentElement.classList.add('logged-in')
            if (darkThemeClassName) document.documentElement.classList.add(darkThemeClassName)
        }
        fetchAllData()
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [pathname])

    useEffect(() => {
        const regenerateSchedules = async () => {
            if (!['/dashboard', '/login', '/signup'].includes(pathname)) return
            if (account.id && employees.length > 0) await loadSchedules(account, employees)
        }
        regenerateSchedules()
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [pathname, account, employees, shifts, holidays])

    useEffect(() => {
        if (pathname !== '/dashboard') return
        if (settings.darkThemeEnabled) {
            document.body.classList.add('logged-in')
            document.documentElement.classList.add('dark-theme')
        } else {
            document.body.classList.remove('logged-in')
            document.documentElement.classList.remove('dark-theme')
        }
    }, [pathname, settings.darkThemeEnabled])

    useEffect(() => {
        if (typeof window === 'undefined') return
        const handleResize = () => {
            setScreenWidth(window.innerWidth)
            setIsMenuShown(window.innerWidth > 950)
        }
        window.addEventListener('resize', handleResize)
        return () => { window.removeEventListener('resize', handleResize) }
    }, [])

    if (!hydrated) return null

    return (
        <dashboardContext.Provider value={{
            account, setAccount,
            subscription, setSubscription,
            content, setContent,
            employees, setEmployees, loadEmployees, validateEmployeeById,
            shifts, setShifts, loadShifts,
            schedules, setSchedules, setScheduleValidity, getScheduleValidity,
            holidays, setHolidays, loadHolidays,
            settings, setSettings, darkThemeClassName,
            isModalOpen, setIsModalOpen,
            modalContent, setModalContent,
            openModal, closeModal,
            screenWidth, isMenuShown, setIsMenuShown
        }}>{children}</dashboardContext.Provider>
    )
}