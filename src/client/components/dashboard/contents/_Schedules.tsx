import { useCallback, useContext, useEffect, useMemo, useState } from 'react'
import { dashboardContext } from '@context'
import { Icon, Request, ScheduleExporter, getDaysInMonth, getEmployeeById, getMonthName, getWeekdayName, openRequestChangeModal } from '@utils'
import { MIN_YEAR, MAX_YEAR } from '@const'
import type { SupportedExportFormat, Employee, ShiftCounts, ScheduleResponse, Shift, Team } from '@types'
import closeIcon from '@icons/close.png'
import prevIcon from '@icons/prev.png'
import nextIcon from '@icons/next.png'
import backIcon from '@icons/back.png'

export default function Schedules() {
    const {
        account, employees, shifts, schedules,
        setScheduleValidity, getScheduleValidity, 
        setModalContent, openModal, closeModal,
        setContent, settings, teams, setSchedules,
        validateEmployeeById
    } = useContext(dashboardContext)
    const today = new Date()
    const [loading, setLoading] = useState(false)
    const [selectedTeam, setSelectedTeam] = useState<number|null>(null)
    const [selectedMonth, setSelectedMonth] = useState<number>(today.getMonth()) // [0-11]
    const [selectedYear, setSelectedYear] = useState<number>(today.getFullYear())
    const [isLeftChevronActive, setIsLeftChevronActive] = useState(true)
    const [isRightChevronActive, setIsRightChevronActive] = useState(true)

    const allTeamsHaveSchedules = useMemo(() => {
        const yearSchedules = schedules.get(selectedYear)
        if (!yearSchedules) return false
        return teams.every(team => {
            const teamMonthly = yearSchedules.get(team.id)
            return teamMonthly?.[selectedMonth] !== undefined && teamMonthly[selectedMonth] !== null
        })
    }, [schedules, selectedYear, selectedMonth, teams])    

    const scheduleAvailable = useMemo(() => {
        if (!selectedTeam) return false
        const yearSchedules = schedules.get(selectedYear)
        const teamMonthly = yearSchedules?.get(selectedTeam)
        return teamMonthly?.[selectedMonth] !== undefined && teamMonthly[selectedMonth] !== null
    }, [schedules, selectedYear, selectedMonth, selectedTeam])    

    const _updateSchedule = (newSchedule: ScheduleResponse) => {
        const { schedule_id: scheduleId, team_id: teamId, year, month, schedule } = newSchedule
    
        setSchedules((prevSchedules) => {
            const updatedSchedules = new Map(prevSchedules)
    
            if (!updatedSchedules.has(year)) {
                updatedSchedules.set(year, new Map())
            }
    
            const teamSchedules = updatedSchedules.get(year)!
    
            if (!teamSchedules.has(teamId)) {
                teamSchedules.set(teamId, new Array(12).fill(null))
            }
    
            const monthlySchedules = teamSchedules.get(teamId)!
            monthlySchedules[month] = {
                id: scheduleId,
                teamId: teamId,
                schedule: schedule.map(day =>
                    day.map(shift =>
                        shift.map(id => validateEmployeeById(id, employees, month, year))
                    )
                )
            }
    
            return updatedSchedules
        })
    }    

    /** Displays a modal for generating a schedule */
    const openGenerateScheduleModal = () => {
        setModalContent(
            employees.length <= 0 ?
            <>
                <h1>Invalid Input</h1>
                <label>Please register ER staff first in the &quot;Staff&quot; section.</label>
                <button onClick={() => { setContent('staff'); closeModal() }}>Register Staff</button>
            </>
            : shifts.length <= 0 ?
            <>
                <h1>Invalid Input</h1>
                <p>Please register shifts first in the &quot;Shifts Per Day&quot; section.</p>
                <button onClick={() => { setContent('shifts'); closeModal() }}>Register Shifts</button>
            </>
            : employees.length < shifts.length ?
            <>
                <h1>Invalid Input</h1>
                <p>
                    The number of employees is not sufficient for the number of shifts per day.
                    To generate a schedule, each employee must work only one shift per day.
                    Please either register more employees or remove one or more shifts.
                </p>
                <button onClick={closeModal}>Close</button>
            </>
            : loading &&
            <>
                <h2>Generating in Progress</h2>
                <p>Please wait while the server generates your schedule.</p>
                <button onClick={closeModal}>Close</button>
            </>
        )
        openModal()
    }

    /** Handles traversing between months and years */
    const handleMonthChange = (direction: 'prev'|'next') => {
        if (direction === 'prev' && !isLeftChevronActive) return
        if (direction === 'next' && !isRightChevronActive) return
        setSelectedMonth(prevMonth => {
            let newMonth = direction === 'prev' ? prevMonth-1 : prevMonth+1
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
            const [workHours, setWorkHours] = useState<ShiftCounts>(new Map())
            const [loading, setLoading] = useState(true)

            const getShiftCounts = useCallback(async () => {
                await new Request(
                    `engine/get_shift_counts_of_employees?account_id=${account.id}&team_id=${selectedTeam}&year=${selectedYear}&month=${selectedMonth}`,
                    (data: Record<number, number>) => {
                        const newShiftCounts = new Map<Employee, number>()
                        for (const [employeeId, shiftCount] of Object.entries(data)) {
                            const employee = getEmployeeById(Number(employeeId), employees)!
                            newShiftCounts.set(employee, shiftCount)
                        }
                        setShiftCounts(newShiftCounts)
                        setLoading(false)
                    }
                ).get()
            }, [setLoading])

            const getTotalWorkHours = useCallback(async () => {
                await new Request(
                    `engine/get_work_hours_of_employees?account_id=${account.id}&team_id=${selectedTeam}&year=${selectedYear}&month=${selectedMonth}`,
                    (data: Record<number, number>) => {
                        // data: Record<number, number>
                        const newWorkHours = new Map<Employee, number>()
                        for (const [employeeId, workHours] of Object.entries(data)) {
                            const employee = getEmployeeById(Number(employeeId), employees)!
                            newWorkHours.set(employee, workHours)
                        }
                        setWorkHours(newWorkHours)
                        setLoading(false)
                    }
                ).get()
            }, [setLoading])

            useEffect(() => {
                if (scheduleAvailable && triggerFetch) {
                    getShiftCounts()
                    getTotalWorkHours()
                }
            }, [getShiftCounts, getTotalWorkHours, triggerFetch])

            return scheduleAvailable
            ? <>
                <h2 style={{ textAlign: 'center' }}>
                    Total Shifts and Work Hours per ER Staff Member This Month
                </h2>
                <section id='modal-content' style={{ textAlign: 'left', margin: '0 auto', marginBottom: 5 }}>
                    {!loading ? (
                        employees.length > 0 ? (
                            employees.filter(emp => emp.teamId === selectedTeam).map((emp, i) => {
                                const numShifts = shiftCounts.get(emp) || 0;
                                const hours = workHours.get(emp) || 0;
                                return (
                                    <li key={i}>
                                        <b>{emp?.name || 'Unknown'}</b>: {numShifts} shifts ({hours} hours)
                                    </li>
                                );
                            })
                        ) : (
                            <p>
                                No ER staff member was assigned a shift in this month.
                                Please ensure you have entered correct information, then regenerate the schedule.
                            </p>
                        )
                    ) : (
                        <p>Loading...</p>
                    )}
                </section>
            </>
            : <>
                <h1>No Schedule Available</h1>
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
            const yearSchedules = schedules.get(selectedYear)
            const teamSchedules = yearSchedules?.get(selectedTeam!)
            const currentSchedule = teamSchedules?.[selectedMonth]
            if (!currentSchedule) { alert('No schedule available to export.'); return }

            const exporter = new ScheduleExporter(
                currentSchedule.schedule,
                shifts,
                employees.filter(emp => emp.teamId === selectedTeam),
                selectedYear,
                selectedMonth,
                settings.weekendDays
            )

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

    const handleTeamClick = (teamId: number) => {
        setSelectedTeam(teamId)
    }

    const goBackToTeamSelector = () => {
        setSelectedTeam(null)
    }

    const generateAllSchedules = async () => {
        if (employees.length <= 0 || shifts.length <= 0 || employees.length < shifts.length || loading) {
            openGenerateScheduleModal()
            return
        }

        setLoading(true)
        const numDays = getDaysInMonth(selectedMonth, selectedYear)

        await new Request(
            `engine/generate_schedule?account_id=${account.id}&num_shifts_per_day=${shifts.length}&num_days=${numDays}&year=${selectedYear}&month=${selectedMonth}`,
            (data: ScheduleResponse[]) => data.map(_updateSchedule),
            (error) => {
                if (!error.includes('not yet implemented')) return
                let pMsg = 'The auto-scheduling algorithm was not yet implemented for this account.'

                if (error.includes('Team')) {
                    const teamId = parseInt(error.split(' ')[1])
                    const teamName = teams.find(t => t.id === teamId)?.name ?? teamId
                    pMsg = `The auto-scheduling algorithm was not yet implemented for team "${teamName}" in your account.`
                }

                pMsg += ' Please contact us to implement this system for you.'

                setModalContent(<>
                    <h1>Cannot Generate Schedule</h1>
                    <p>{pMsg}</p>
                    <button onClick={() => openRequestChangeModal('Implement Algorithm for Account', setModalContent, openModal)}>Contact Us</button>
                </>)
                openModal()
            }
        ).get()

        setLoading(false)
    }

    const regenerateSchedule = async () => {
        await generateAllSchedules()
        setScheduleValidity(true, selectedYear, selectedMonth)
    }

    useEffect(() => {
        const schedule = schedules.get(selectedYear)?.get(selectedTeam!)?.[selectedMonth]
        const shiftsPerDayInSchedule = schedule?.schedule?.[0]?.length
    
        if (shiftsPerDayInSchedule === undefined || !(employees.length && shifts.length)) {
            setScheduleValidity(true, selectedYear, selectedMonth)
        } else if (employees.length < shifts.length || shiftsPerDayInSchedule !== shifts.length) {
            setScheduleValidity(false, selectedYear, selectedMonth)
        }
    }, [employees.length, shifts.length, schedules, selectedMonth, selectedYear, selectedTeam, setScheduleValidity])    

    useEffect(() => {
        setIsLeftChevronActive(!(selectedYear === MIN_YEAR && selectedMonth === 0))
        setIsRightChevronActive(!(selectedYear === MAX_YEAR && selectedMonth === 11))
    }, [selectedMonth, selectedYear])

    return <>
        <header>
            <section id='header-upper'>
                <section id='header-btns'>
                    {!selectedTeam ? (
                        <button onClick={allTeamsHaveSchedules ? regenerateSchedule : generateAllSchedules}>
                            {allTeamsHaveSchedules ? 'Regenerate Schedules' : 'Generate Schedules'}
                        </button>
                    ) : <>
                        <button onClick={goBackToTeamSelector} id='back-to-team-selector-btn'>
                            <Icon src={backIcon} alt='Back to Team Selector' size={23}/>
                        </button>
                        <button onClick={openDetailsModal}>Details</button>
                        <button onClick={openExportModal}>Export</button>
                    </>}
                </section>
                <section id='month-navigators'>
                    <button
                        onClick={() => handleMonthChange('prev')}
                        className={isLeftChevronActive ? '' : 'disabled-chevron'}
                    ><Icon src={prevIcon} alt='Previous month' size={28}/></button>
                    <span>{getMonthName(selectedMonth)} {selectedYear}</span>
                    <button
                        onClick={() => handleMonthChange('next')}
                        className={isRightChevronActive ? '' : 'disabled-chevron'}
                    ><Icon src={nextIcon} alt='Next month' size={28}/></button>
                </section>
            </section>
            {
                !getScheduleValidity(selectedYear, selectedMonth) && teams.length > 0
                ? 
                    <p className='header-msg invalid-msg'>
                        <span>This schedule seems to be invalid or outdated. Please try to regenerate it.</span>
                        <button onClick={() => setScheduleValidity(true, selectedYear, selectedMonth)}><Icon src={closeIcon} alt='Close'/></button>
                    </p>
                :
                    <p className='header-msg' style={!loading && (!selectedTeam || scheduleAvailable) ? { display: 'none' } : {}}>
                        {
                            loading
                            ? 'Generating...' 
                            : !scheduleAvailable && 'No schedule generated yet for this team in this month.'
                        }
                    </p>
            }
            {teams.length === 0 && <p className='header-msg'>You haven&apos;t registered any staff team yet.</p>}
        </header>

        {!selectedTeam && teams.length > 0 && <TeamSelector teams={teams} selectedTeam={selectedTeam} handleTeamClick={handleTeamClick} />}

        {scheduleAvailable && selectedTeam && schedules.get(selectedYear)?.get(selectedTeam)?.[selectedMonth] && (
            <div className='card-container'>
                {schedules.get(selectedYear)!.get(selectedTeam)![selectedMonth].schedule.map((day, dayI) => (
                    <DayCard
                        key={dayI}
                        day={day}
                        dayI={dayI}
                        selectedYear={selectedYear}
                        selectedMonth={selectedMonth}
                        shifts={shifts}
                    />
                ))}
            </div>
        )}
    </>
}


const TeamSelector = (
    { teams, selectedTeam, handleTeamClick }:
    { teams: Team[], selectedTeam: number|null, handleTeamClick: (teamId: number) => void }
) => (
    <section className='team-selector'>
        <h1>Select a team to view its generated schedule in this month:</h1>
        <div className='team-cards'>
            {teams.map(team => (
                <section
                    key={team.id}
                    className={`team-card ${selectedTeam === team.id ? 'selected' : ''}`}
                    onClick={() => handleTeamClick(team.id)}
                >
                    <h2>{team.name}</h2>
                    <Icon src={nextIcon} alt='Next month' size={40}/>
                </section>
            ))}
        </div>
    </section>
)


const DayCard = (
    { day, dayI, selectedYear, selectedMonth, shifts }:
    { day: Employee[][], dayI: number, selectedYear: number, selectedMonth: number, shifts: Shift[] }
) => (
    <div className='day-card' key={dayI}>
        <h3>Day {dayI+1} <span className='weekday-name'>| {getWeekdayName(selectedYear, selectedMonth, dayI+1).slice(0, 3)}</span></h3>
        <table>
            <thead>
                <tr><th>Shift</th><th>ER Staff Member</th></tr>
            </thead>
            <tbody>
                {day.map((shift, shiftI) => (
                    <tr key={shiftI}>
                        <td>{shifts[shiftI]?.name}</td>
                        <td>{shift.map(employee => employee.name).join(', ') || 'Unknown'}</td>
                    </tr>
                ))}
            </tbody>
        </table>
    </div>
)