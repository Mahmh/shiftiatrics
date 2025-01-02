'use client'
import { useState, createContext, ReactNode, useEffect, useCallback, useMemo } from 'react'
import type { ContextProps, ContentName, Employee, Account, Shift, Schedule, Settings, YearToSchedules, YearToSchedulesValidity, ScheduleOfIDs } from '@types'
import { isLoggedIn, Request, getEmployeeById, hasScheduleForMonth } from '@utils'

const defaultContent: ContentName = 'schedules'
const nullEmployee: Employee = { id: -Infinity, name: '', minWorkHours: Infinity, maxWorkHours: Infinity }
const nullSettings: Settings = { darkThemeEnabled: false, minMaxWorkHoursEnabled: false, multiEmpsInShiftEnabled: false, multiShiftsOneEmpEnabled: false }
export const nullAccount: Account = { id: -Infinity, username: '', password: '' }

export const DashboardContext = createContext<ContextProps>({
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

    settings: nullSettings,
    setSettings: () => {},
    darkThemeClassName: '',

    isModalOpen: false,
    setIsModalOpen: () => {},
    modalContent: null,
    setModalContent: () => {},
    openModal: () => {},
    closeModal: () => {}
})

export function DashboardProvider({ children }: Readonly<{children: React.ReactNode}>) {
    const [content, setContent] = useState<ContentName>(defaultContent)
    const [account, setAccount] = useState<Account>(nullAccount)
    const [employees, setEmployees] = useState<Employee[]>([])
    const [shifts, setShifts] = useState<Shift[]>([])
    const [schedules, setSchedules] = useState<YearToSchedules>(new Map())
    const [schedulesValidity, setSchedulesValidity] = useState<YearToSchedulesValidity>(new Map())
    const [settings, setSettings] = useState(nullSettings)
    const [isModalOpen, setIsModalOpen] = useState(false)
    const [modalContent, setModalContent] = useState<ReactNode>(null)
    const darkThemeClassName = useMemo(() => settings.darkThemeEnabled ? 'dark-theme' : '', [settings.darkThemeEnabled])

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

    const loadEmployees = useCallback(async (): Promise<Employee[]> => {
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
            const parsedSchedules = new Map<number, Schedule[]>();

            data.forEach(scheduleData => {
                const { schedule_id: scheduleId, month, year } = scheduleData;

                // Initialize validity for this schedule as true
                setScheduleValidity(true, year, month);

                // Transform schedule data to match Employee['id'][][][]
                const parsedSchedule = scheduleData.schedule.map((day: number[][]) =>
                    day.map((shift: number[]) =>
                        shift.map(empId => validateEmployeeById(empId, employees, year, month))
                    )
                );

                // Ensure the year exists in the maps
                if (!parsedSchedules.has(year)) parsedSchedules.set(year, []);
                if (!schedulesValidity.has(year)) {
                    const map = new Map<number, boolean>();
                    for (let i = 0; i < 12; i++) map.set(i, true);
                    schedulesValidity.set(year, map);
                }

                const yearSchedules = parsedSchedules.get(year)!;
                yearSchedules[month] = {
                    id: scheduleId,
                    schedule: parsedSchedule,
                };
            });

            setSchedules(parsedSchedules);
        }).get();
    }, [account.id, schedulesValidity, validateEmployeeById, setScheduleValidity])


    const loadSettings = useCallback(async () => {
        type Response = { detail: null } | {
            dark_theme_enabled: boolean,
            min_max_work_hours_enabled: boolean
            multi_emps_in_shift_enabled: boolean
            multi_shifts_one_emp_enabled: boolean
        };
        await new Request(
            `accounts/${account.id}/settings`,
            (data: Response) => {
                if ('detail' in data) return
                setSettings({
                    darkThemeEnabled: data.dark_theme_enabled,
                    minMaxWorkHoursEnabled: data.min_max_work_hours_enabled,
                    multiEmpsInShiftEnabled: data.multi_emps_in_shift_enabled,
                    multiShiftsOneEmpEnabled: data.multi_shifts_one_emp_enabled
                })
            }
        ).get()
    }, [account.id, setSettings])

    useEffect(() => {
        const fetchAllData = async () => {
            if (isLoggedIn(account)) {
                const loadedEmployees = await loadEmployees()
                await loadShifts()
                await loadSchedules(loadedEmployees)
                await loadSettings()
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


    useEffect(() => {
        if (darkThemeClassName) {
            document.body.classList.add('dark-theme');
            return () => { document.body.classList.remove('dark-theme') };
        }
      }, [darkThemeClassName])

    return (
        <DashboardContext.Provider value={{
            account, setAccount,
            content, setContent,
            employees, setEmployees, loadEmployees, validateEmployeeById,
            shifts, setShifts, loadShifts,
            isModalOpen, setIsModalOpen,
            modalContent, setModalContent,
            openModal, closeModal,
            schedules, setSchedules, loadSchedules, setScheduleValidity, getScheduleValidity,
            settings, setSettings, darkThemeClassName
        }}>{children}</DashboardContext.Provider>
    )
}