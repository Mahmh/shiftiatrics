'use client'
import { useState, createContext, ReactNode, useEffect, useCallback, useMemo } from 'react'
import { usePathname, useRouter, useSearchParams } from 'next/navigation'
import { isLoggedIn, getEmployeeById, getUIDate, hasScheduleForMonth, ChangePasswordModalContent, Request } from '@utils'
import type {
    ContextProps, ContentName, Employee,
    Account, Shift, Schedule, Holiday,
    Settings, YearToSchedules, YearToSchedulesValidity,
    ReadonlyChildren, Subscription, SettingsResponse,
    SubscriptionResponse, StripeInvoice, EmployeeResponse, ShiftResponse,
    ScheduleResponse, HolidayResponse, StripeInvoiceResponse
} from '@types'
import { parseEmployee, parseHoliday, parseSettings, parseShift, parseStripeInvoice, parseSub } from '@types'

// Context for dashboard content
const defaultContent: ContentName = 'schedules'
const nullEmployee: Employee = { id: -Infinity, name: '', minWorkHours: Infinity, maxWorkHours: Infinity }
export const nullSettings: Settings = { darkThemeEnabled: false, weekendDays: 'Friday & Saturday' }
export const nullAccount: Account = { id: -Infinity, email: '', emailVerified: false, passwordChanged: false, subExpired: true }
export const nullSub: Subscription = { id: -Infinity, plan: 'growth', createdAt: '', expiresAt: '' }

export const dashboardContext = createContext<ContextProps>({
    content: defaultContent,
    setContent: () => {},

    account: nullAccount,
    setAccount: () => {},

    subscription: nullSub,
    setSubscription: () => {},
    invoices: [],

    employees: [],
    setEmployees: () => {},
    validateEmployeeById: () => nullEmployee,

    shifts: [],
    setShifts: () => {},

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
    const [subscription, setSubscription] = useState<Subscription>(nullSub)
    const [employees, setEmployees] = useState<Employee[]>([])
    const [shifts, setShifts] = useState<Shift[]>([])
    const [schedules, setSchedules] = useState<YearToSchedules>(new Map())
    const [holidays, setHolidays] = useState<Holiday[]>([])
    const [schedulesValidity, setSchedulesValidity] = useState<YearToSchedulesValidity>(new Map())
    const [settings, setSettings] = useState(nullSettings)
    const [invoices, setInvoices] = useState<StripeInvoice[]>([])
    const [isModalOpen, setIsModalOpen] = useState(false)
    const [modalContent, setModalContent] = useState<ReactNode>(null)
    const [screenWidth, setScreenWidth] = useState(typeof window !== 'undefined' ? window.innerWidth : 0)
    const [isMenuShown, setIsMenuShown] = useState(screenWidth > 950)
    const darkThemeClassName = useMemo(() => settings.darkThemeEnabled ? 'dark-theme' : '', [settings.darkThemeEnabled])
    const openModal = useCallback(() => setIsModalOpen(true), [])
    const closeModal = useCallback(() => setIsModalOpen(false), [])
    const router = useRouter()
    const params = useSearchParams()
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
        let minWorkHours = employee?.minWorkHours
        let maxWorkHours = employee?.maxWorkHours
        if (typeof name === 'undefined') { name = 'Unknown'; setScheduleValidity(false, year, month) }
        if (typeof minWorkHours === 'undefined') { minWorkHours = -Infinity; setScheduleValidity(false, year, month)}
        if (typeof maxWorkHours === 'undefined') { maxWorkHours = -Infinity; setScheduleValidity(false, year, month) }
        return { id, name, minWorkHours, maxWorkHours }
    }, [setScheduleValidity])

    const _parseSchedules = useCallback((schedules: ScheduleResponse[], employees: Employee[]): YearToSchedules => {
        const parsedSchedules = new Map<number, Schedule[]>()

        schedules.forEach(scheduleData => {
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

        return parsedSchedules
    }, [schedulesValidity, validateEmployeeById, setScheduleValidity])

    const loadHolidays = useCallback(async (account: Account) => {
        if (account.id === -Infinity) return []
        type Response = {
            holiday_id: Holiday['id'],
            holiday_name: Holiday['name'],
            assigned_to: Holiday['assignedTo'],
            start_date: Holiday['startDate'],
            end_date: Holiday['endDate']
        }[];
        await new Request(`holidays/${account.id}`, (data: Response) => {
            setHolidays(data.map(h => ({
                id: h.holiday_id,
                name: h.holiday_name,
                assignedTo: h.assigned_to,
                startDate: h.start_date,
                endDate: h.end_date
            })))
        }).get()
    }, [account.id])

    const _checkIsSubExpiringSoon = useCallback((subscription: Subscription) => {
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

    const _handlePasswordChangeUponSignup = useCallback((passwordChanged: boolean) => {
        if (passwordChanged) return
        setModalContent(<>
            <h1>Welcome to your Shiftiatrics dashboard!</h1>
            <p>Before you start using this platform, please set your password and keep it secure.</p>
            <button onClick={() => setModalContent(<ChangePasswordModalContent setAccount={setAccount} closeModal={closeModal}/>)}>Next</button>
        </>)
        openModal()
    }, [openModal, setModalContent])

    const _handleCheckoutSessionId = useCallback(async (chkoutSessionId: string, accountId: number) => {
        await new Request(
            `sub/create/${accountId}`,
            (data: SubscriptionResponse) => {
                setSubscription(parseSub(data))
                setModalContent(<>
                    <h1>Your subscription was created!</h1>
                    <p>Now you can enjoy all of your custom-tailored features and start automatically generating your schedules.</p>
                    <button onClick={closeModal}>Proceed</button>
                </>)
                openModal()
            },
            (error) => {
                if (error.includes('session ID was processed')) {
                    router.push('/dashboard')
                } else {
                    setModalContent(<p style={{ padding: 20 }}>Error occurred: {error}</p>)
                    openModal()
                }
            }
        ).post({ chkout_session_id: chkoutSessionId })
    }, [openModal, setModalContent, setSubscription, router])

    const _load_data = async () => {
        type Response = {
            employees: EmployeeResponse[],
            shifts: ShiftResponse[],
            schedules: ScheduleResponse[],
            holidays: HolidayResponse[],
            settings: SettingsResponse,
            invoices: StripeInvoiceResponse[]
        };
        await new Request(
            'accounts/data',
            (data: Response) => {
                const parsedEmps = data.employees.map(parseEmployee)
                setEmployees(parsedEmps)
                setShifts(data.shifts.map(parseShift))
                setSchedules(_parseSchedules(data.schedules, parsedEmps))
                setHolidays(data.holidays.map(parseHoliday))
                setSettings(parseSettings(data.settings))
                if (subscription !== null)setInvoices(data.invoices.map(parseStripeInvoice))
            },
            (error) => {
                setModalContent(<>
                    <p>
                        There has been an error loading your account's data.
                        Please try to refresh the page. 
                        If this issue persists, please contact us.
                        <br/><b>Error message: {error}</b>
                    </p>
                    <button onClick={() => router.push('/support/contact')}>Report Issue</button>
                </>)
                openModal()
            }
        ).get()
    }

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
            if (res.subscription !== null) _checkIsSubExpiringSoon(res.subscription)

            await _load_data()
            _handlePasswordChangeUponSignup(res.account.passwordChanged)
    
            const chkoutSessionId = params.get('chkout_session_id')
            if (pathname === '/dashboard' && chkoutSessionId !== null) _handleCheckoutSessionId(chkoutSessionId, res.account.id)

            document.body.classList.add('logged-in')
            document.documentElement.classList.add('logged-in')
            if (darkThemeClassName) document.documentElement.classList.add(darkThemeClassName)
        }
        fetchAllData()
    }, [pathname])

    // useEffect(() => {
    //     const reloadData = async () => {
    //         if (!['/dashboard', '/login', '/signup'].includes(pathname)) return
    //         if (account.id && employees.length > 0) await _load_data()
    //     }
    //     reloadData()
    // }, [pathname, account, employees, shifts, holidays])

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
            subscription, setSubscription, invoices,
            content, setContent,
            employees, setEmployees, validateEmployeeById,
            shifts, setShifts,
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