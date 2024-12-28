import { useCallback, useContext, useEffect, useMemo, useState } from 'react'
import { AppContext } from '@context'
import { Icon, Request, ScheduleExporter, getDaysInMonth, getEmployeeById, getMonthName, hasScheduleForMonth } from '@utils'
import type { SupportedExportFormat, ScheduleOfIDs, Employee, ShiftCounts } from '@types'
import prevIcon from '@icons/prev.png'
import nextIcon from '@icons/next.png'

export default function Schedules() {
    const {
        account, employees, validateEmployeeById, shifts, 
        schedules, setSchedules, setScheduleValidity, getScheduleValidity,
        setModalContent, openModal, closeModal, setContent
    } = useContext(AppContext)
    const [isLoading, setIsLoading] = useState(false)
    const today = new Date()
    const [selectedMonth, setSelectedMonth] = useState<number>(today.getMonth())
    const [selectedYear, setSelectedYear] = useState<number>(today.getFullYear())
    const scheduleAvailable = useMemo(
        () => hasScheduleForMonth(schedules, selectedYear, selectedMonth),
        [schedules, selectedYear, selectedMonth]
    )

    /** Stores the schedule in DB */
    const storeSchedule = useCallback(async (schedule: ScheduleOfIDs) => {
        if (schedule.length <= 0) return
        await new Request(
            `accounts/${account.id}/schedules`,
            (data: { year: number, month: number, schedule_id: number, schedule: ScheduleOfIDs }) => {
                // Add the new schedule to the state with the returned data
                setSchedules((prevSchedules) => {
                    const updatedSchedules = new Map(prevSchedules)
                    if (!updatedSchedules.has(data.year)) updatedSchedules.set(data.year, [])
                    const yearSchedules = updatedSchedules.get(data.year)!

                    yearSchedules[data.month] = {
                        id: data.schedule_id,
                        schedule: data.schedule.map(row => 
                            row.map(id => validateEmployeeById(id, employees, data.month, data.year))
                        )
                    }
                    return updatedSchedules
                })
            },
            { year: selectedYear, month: selectedMonth, schedule }
        ).post()
    }, [account.id, employees, selectedMonth, selectedYear, setSchedules, validateEmployeeById])


    /** Overwrites the previously generated schedule in DB */
    const updateSchedule = useCallback(async (scheduleId: number, schedule: ScheduleOfIDs) => {
        if (schedule.length <= 0) return
        await new Request(
            `schedules/${scheduleId}`,
            (data: { year: number, month: number, schedule_id: number, schedule: ScheduleOfIDs }) => {
                // Update the schedule in the state
                setSchedules((prevSchedules) => {
                    const updatedSchedules = new Map(prevSchedules)
                    if (!updatedSchedules.has(data.year)) updatedSchedules.set(data.year, [])
                    const yearSchedules = updatedSchedules.get(data.year)!
    
                    yearSchedules[data.month] = {
                        id: data.schedule_id,
                        schedule: data.schedule.map(row => 
                            row.map(id => validateEmployeeById(id, employees, data.month, data.year))
                        )
                    }
                    return updatedSchedules
                })
            },
            { schedule }
        ).patch()
    }, [employees, setSchedules, validateEmployeeById])


    /** Displays a modal for generating a schedule */
    const openGenerateScheduleModal = useCallback(() => {
        setModalContent(
            employees.length <= 0 ?
            <>
                <h2>Invalid Input</h2>
                <label>Please register employees first in the &quot;Employees&quot; section.</label>
                <button onClick={() => { setContent('employees'); closeModal() }}>Register Employees</button>
            </>
            : shifts.length <= 0 ?
            <>
                <h2>Invalid Input</h2>
                <p>Please register shifts first in the &quot;Shifts Per Day&quot; section.</p>
                <button onClick={() => { setContent('shifts'); closeModal() }}>Register Shifts</button>
            </>
            : employees.length < shifts.length ?
            <>
                <h2>Invalid Input</h2>
                <p>
                    The number of employees is not sufficient for the number of shifts per day.
                    To generate a schedule, each employee must work only one shift per day.
                    Please either register more employees or remove one or more shifts.
                </p>
                <button onClick={closeModal}>Close</button>
            </>
            : isLoading &&
            <>
                <h2>Generating in Progress</h2>
                <p>Please wait while the server generates your schedule.</p>
                <button onClick={closeModal}>Close</button>
            </>
        )
        openModal()
    }, [employees.length, isLoading, openModal, closeModal, setContent, setModalContent, shifts.length])


    /** Handles traversing between months and years */
    const handleMonthChange = (direction: 'prev' | 'next') => {
        setSelectedMonth(prevMonth => {
            let newMonth = direction === 'prev' ? prevMonth - 1 : prevMonth + 1
            let newYear = selectedYear
            if (newMonth < 0) {
                newMonth = 11 // Wrap to December
                newYear -= 1  // Move to previous year
            } else if (newMonth > 11) {
                newMonth = 0  // Wrap to January
                newYear += 1  // Move to next year
            }
            setSelectedYear(newYear)
            return newMonth
        })
    }


    /** Displays a modal for showing additional info about the schedule */
    const openDetailsModal = () => {
        const DetailsContent = ({ triggerFetch }: { triggerFetch: boolean }) => {
            const [shiftCounts, setShiftCounts] = useState<ShiftCounts>(new Map())
            const [isLoading, setIsLoading] = useState(true)

            const getShiftCounts = useCallback(async () => {
                await new Request(
                    `engine/get_shift_counts_of_employees?account_id=${account.id}&year=${selectedYear}&month=${selectedMonth}`,
                    (data: Record<number, number>) => {
                        const newShiftCounts = new Map<Employee, number>()
                        for (const [employeeId, shiftCount] of Object.entries(data)) {
                            const employee = getEmployeeById(Number(employeeId), employees)!
                            newShiftCounts.set(employee, shiftCount)
                        }
                        setShiftCounts(newShiftCounts)
                        setIsLoading(false)
                    }
                ).post()
            }, [setIsLoading])

            useEffect(() => {
                if (scheduleAvailable && triggerFetch) {
                    getShiftCounts()
                }
            }, [getShiftCounts, triggerFetch]);

            return scheduleAvailable
            ? <>
                <h2>Total Shifts per Employee This Month</h2>
                <section id='modal-content'>
                    {!isLoading ? Array.from(shiftCounts.entries()).map(([emp, numShifts], i) => (
                        <li key={i}><b>{emp?.name || 'Unknown'}</b>: {numShifts} shifts</li>
                    )) : <p>Loading...</p>}
                </section>
            </>
            : <>
                <h2>Invalid Input</h2>
                <p>Please generate a schedule for this month to show details.</p>
                <button onClick={closeModal}>Close</button>
            </>
        }
        
        setModalContent(<DetailsContent triggerFetch={true}/>)
        openModal()
    }


    /** Displays a modal for exporting the schedule */
    const openExportModal = () => {
        const exportSchedule = (format: SupportedExportFormat) => () => {
            const currentYearSchedules = schedules.get(selectedYear)
            const currentSchedule = currentYearSchedules?.[selectedMonth]
            if (!currentSchedule) { alert('No schedule available to export.'); return }
            const exporter = new ScheduleExporter(currentSchedule, shifts)
            switch (format) {
                case 'xlsx': exporter.exportExcel(); break
                case 'csv': exporter.exportCSV(); break
                case 'tsv': exporter.exportTSV(); break
                case 'json': exporter.exportJSON(); break
                default: console.error('Unsupported export format')
            }
            closeModal()
        }

        setModalContent(
            scheduleAvailable
            ? !getScheduleValidity(selectedYear, selectedMonth) 
            ? <>
                <h2>Invalid Schedule</h2>
                <p>Please regenerate the schedule before exporting it by clicking on the &quot;Regenerate Schedule&quot; button.</p>
                <button onClick={closeModal}>Close</button>
            </>
            : <>
                <h2>Export Schedule to a File</h2>
                <section style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                    <button onClick={exportSchedule('xlsx')}>Export as Excel Spreadsheet</button>
                    <button onClick={exportSchedule('csv')}>Export as CSV</button>
                    <button onClick={exportSchedule('tsv')}>Export as TSV</button>
                    <button onClick={exportSchedule('json')}>Export as JSON</button>
                </section>
            </>
            : <>
                <h2>No Schedule Available</h2>
                <p>Please generate a schedule before exporting it by clicking on the &quot;Generate Schedule&quot; button.</p>
                <button onClick={closeModal}>Close</button>
            </>
        )
        openModal()
    }

    /** Sends an API request to the engine for schedule generation */
    const generateSchedule = useCallback(async () => {
        if (employees.length <= 0 || shifts.length <= 0 || employees.length < shifts.length || isLoading) {
            openGenerateScheduleModal(); return
        }

        setIsLoading(true)
        const numDays = getDaysInMonth(selectedMonth, selectedYear)
        let newSchedule: ScheduleOfIDs = [] // Temporary storage for the new schedule
    
        // Send a request to generate a schedule
        await new Request(
            `engine/generate_schedule?account_id=${account.id}&num_shifts_per_day=${shifts.length}&num_days=${numDays}`,
            (data: number[][]) => { newSchedule = data }
        ).post()
    
        await storeSchedule(newSchedule)
        setIsLoading(false)
    }, [account.id, employees.length, isLoading, openGenerateScheduleModal, selectedMonth, selectedYear, shifts.length, storeSchedule])


    /** Generates the schedule again then overwrites the old one in DB */
    const regenerateSchedule = useCallback(async () => {
        if (employees.length <= 0 || shifts.length <= 0 || employees.length < shifts.length || isLoading) {
            openGenerateScheduleModal(); return
        }

        setScheduleValidity(true, selectedYear, selectedMonth)
        setIsLoading(true)
        const numDays = getDaysInMonth(selectedMonth, selectedYear)
        let newSchedule: ScheduleOfIDs = [] // Temporary storage for the new schedule

        // Get the schedule ID for the current year and month
        const scheduleId = schedules.get(selectedYear)?.[selectedMonth]?.id
        if (!scheduleId) {
            alert('No schedule ID found for the selected month. Cannot regenerate.')
            setIsLoading(false)
            return
        }
    
        // Send a request to regenerate the schedule
        await new Request(
            `engine/generate_schedule?account_id=${account.id}&num_shifts_per_day=${shifts.length}&num_days=${numDays}`,
            (data: number[][]) => { newSchedule = data }
        ).post()

        await updateSchedule(scheduleId, newSchedule)
        setIsLoading(false)
    }, [account.id, employees.length, isLoading, schedules, selectedMonth, selectedYear, setScheduleValidity, shifts.length, updateSchedule, openGenerateScheduleModal])

    useEffect(() => {
        const shiftsPerDayInSchedule = schedules.get(selectedYear)?.[selectedMonth]?.schedule[0].length
        if (shiftsPerDayInSchedule === undefined || !(employees.length && shifts.length)) {
            setScheduleValidity(true, selectedYear, selectedMonth)
        } else if (employees.length < shifts.length || shiftsPerDayInSchedule !== shifts.length) {
            setScheduleValidity(false, selectedYear, selectedMonth)
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [schedules, selectedMonth, employees.length, selectedYear, shifts.length])

    return <>
        <header>
            <section id='header-btns'>
                <button onClick={scheduleAvailable ? regenerateSchedule : generateSchedule}>
                    {scheduleAvailable ? 'Regenerate Schedule' : 'Generate Schedule'}
                </button>
                <button onClick={openDetailsModal}>Details</button>
                <button onClick={openExportModal}>Export</button>
            </section>
            <section id='month-navigators'>
                <button onClick={() => handleMonthChange('prev')}><Icon src={prevIcon} alt='Previous month' size={28}/></button>
                <span>{getMonthName(selectedMonth)} {selectedYear}</span>
                <button onClick={() => handleMonthChange('next')}><Icon src={nextIcon} alt='Next month' size={28}/></button>
            </section>
        </header>
        {
            !getScheduleValidity(selectedYear, selectedMonth) &&
            <p className='header-msg invalid-msg'>This schedule seems to be invalid or outdated. Please try to regenerate it.</p>
        }
        {scheduleAvailable ? (
            <div id='schedule-area'>
                {
                    schedules.get(selectedYear)![selectedMonth].schedule.map((day, dayI) => 
                    <div className='day-card' key={dayI}>
                        <h3>Day {dayI + 1}</h3>
                        <table>
                            <thead>
                                <tr><th>Shift</th><th>Employee</th></tr>
                            </thead>
                            <tbody>
                                {day.map((employee, shiftI) => (
                                    <tr key={shiftI}>
                                        <td>{shifts[shiftI]?.name}</td>
                                        <td>{employee.name || 'Unknown'}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>
        ) : isLoading ? <p className='header-msg'>Generating...</p> : (
            <p className='header-msg'>No schedule generated yet for this month. Click &quot;Generate Schedule&quot; to create one.</p>
        )}
        
    </>
}