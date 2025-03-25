import { useState, useContext } from 'react'
import { dashboardContext } from '@context'
import { Icon, Request, Choice, getMonthName } from '@utils'
import type { Holiday, InputEvent } from '@types'
import editIcon from '@icons/edit.png'
import removeIcon from '@icons/remove.png'

const HolidayCard = ({ id, name, assignedTo, startDate, endDate }: Holiday) => {
    const { account, employees, holidays, setModalContent, openModal, closeModal, loadHolidays } = useContext(dashboardContext)

    const convertToUserFriendlyDate = (date: string) => {
        const [year, month, day] = date.split('-').map(Number)
        const monthName = getMonthName(month - 1)
        return `${monthName} ${day}, ${year}`
    }

    const openEditModal = () => {
        const EditModalContent = () => {
            const isValidDateRange = (start: string, end: string) => new Date(start) <= new Date(end)
            const holiday = holidays.find(h => h.id === id)
            const [tempName, setTempName] = useState(name)
            const [assignedTo, setAssignedTo] = useState<number[]>(holiday?.assignedTo || [])
            const [startDate, setStartDate] = useState(holiday?.startDate || '')
            const [endDate, setEndDate] = useState(holiday?.endDate || '')
            const [isConfirmDisabled, setConfirmDisabled] = useState(
                tempName.trim().length === 0 || name.trim().length === 0 || assignedTo.length === 0 || !isValidDateRange(startDate, endDate)
            )

            const handleNameChange = (e: InputEvent) => {
                setTempName(e.target.value)
                setConfirmDisabled(
                    e.target.value.trim().length === 0 || name.trim().length === 0 || assignedTo.length === 0 || !isValidDateRange(startDate, endDate)
                )
            }

            const handleCheckboxChange = (id: number) => {
                setAssignedTo(prev => {
                    const updated = prev.includes(id) ? prev.filter(empId => empId !== id) : [...prev, id]
                    setConfirmDisabled(
                        tempName.trim().length === 0 || name.trim().length === 0 || updated.length === 0 || !isValidDateRange(startDate, endDate)
                    )
                    return updated
                })
            }

            const handleStartDateChange = (e: InputEvent) => {
                setStartDate(e.target.value)
                setConfirmDisabled(
                    tempName.trim().length === 0 || name.trim().length === 0 || assignedTo.length === 0 || !isValidDateRange(e.target.value, endDate)
                )
            }

            const handleEndDateChange = (e: InputEvent) => {
                setEndDate(e.target.value)
                setConfirmDisabled(
                    tempName.trim().length === 0 || name.trim().length === 0 || assignedTo.length === 0 || !isValidDateRange(startDate, e.target.value)
                )
            }

            const confirmEdit = async () => {
                await new Request(`holidays/${id}`, () => loadHolidays(account)).patch({
                    holiday_name: tempName,
                    assigned_to: assignedTo,
                    start_date: startDate,
                    end_date: endDate,
                })
                closeModal()
            }

            return <>
                <h2>Edit Holiday</h2>
                <section style={{ marginBottom: 10 }}>
                    <label style={{ marginRight: 10 }}>Name: </label>
                    <input
                        type='text'
                        placeholder='Holiday name'
                        value={tempName}
                        onChange={handleNameChange}
                        maxLength={40}
                    />
                </section>
                <section style={{ marginBottom: 10 }}>
                    <label style={{ marginRight: 10 }}>Start Date: </label>
                    <input
                        type='date'
                        value={startDate}
                        onChange={handleStartDateChange}
                    />
                </section>
                <section style={{ marginBottom: 10 }}>
                    <label style={{ marginRight: 10 }}>End Date: </label>
                    <input
                        type='date'
                        value={endDate}
                        onChange={handleEndDateChange}
                    />
                </section>
                <section style={{ marginBottom: 10 }}>
                    <label style={{ marginRight: 10 }}>Assign to: </label>
                    <div className='checkboxes'>
                        {employees.map(employee => (
                            <div key={employee.id}>
                                <input
                                    type='checkbox'
                                    id={`employee-${employee.id}`}
                                    checked={assignedTo.includes(employee.id)}
                                    onChange={() => handleCheckboxChange(employee.id)}
                                />
                                <label htmlFor={`employee-${employee.id}`}>{employee.name}</label>
                            </div>
                        ))}
                    </div>
                </section>
                <button
                    onClick={confirmEdit}
                    disabled={isConfirmDisabled}
                    id={isConfirmDisabled ? 'disabled-confirm-btn' : ''}
                >
                    Confirm
                </button>
            </>
        }

        setModalContent(<EditModalContent/>)
        openModal()
    }

    const openDeleteModal = () => {
        const confirmDelete = async () => {
            await new Request(`holidays/${id}`, () => loadHolidays(account)).delete()
            closeModal()
        }

        setModalContent(<>
            <h1>Remove Holiday &quot;{name}&quot;?</h1>
            <Choice onYes={confirmDelete} onNo={closeModal}/>
        </>)
        openModal()
    }

    return (
        <div className='dashboard-card'>
            <div className='dashboard-card-details'>
                <h1>{name}</h1>
                <span><b>Starts:</b> {convertToUserFriendlyDate(startDate)}</span>
                <span><b>Ends:</b> {convertToUserFriendlyDate(endDate)}</span>
                <span><b>Assigned to:</b> {assignedTo.map(id => employees.find(emp => emp.id === id)?.name).join(', ')}</span>
            </div>
            <div>
                <button onClick={openEditModal}><Icon src={editIcon} alt='Edit'/></button>
                <button onClick={openDeleteModal}><Icon src={removeIcon} alt='Remove'/></button>
            </div>
        </div>
    )
}

export default function Holidays() {
    const { account, employees, holidays, setModalContent, openModal, closeModal, setContent, loadHolidays } = useContext(dashboardContext)

    const openAddModal = () => {
        const AddModalContent = () => {
            const [tempName, setTempName] = useState('')
            const [assignedTo, setAssignedTo] = useState<number[]>([])
            const [startDate, setStartDate] = useState('')
            const [endDate, setEndDate] = useState('')
            const [isConfirmDisabled, setConfirmDisabled] = useState(true)

            const isValidDateRange = (start: string, end: string) => {
                return new Date(start) <= new Date(end)
            }

            const handleNameChange = (e: InputEvent) => {
                setTempName(e.target.value)
                setConfirmDisabled(
                    e.target.value.trim().length === 0 || assignedTo.length === 0 || !isValidDateRange(startDate, endDate)
                )
            }

            const handleCheckboxChange = (id: number) => {
                setAssignedTo(prev => {
                    const updated = prev.includes(id) ? prev.filter(empId => empId !== id) : [...prev, id]
                    setConfirmDisabled(
                        tempName.trim().length === 0 || updated.length === 0 || !isValidDateRange(startDate, endDate)
                    )
                    return updated
                })
            }

            const handleStartDateChange = (e: InputEvent) => {
                setStartDate(e.target.value)
                setConfirmDisabled(
                    tempName.trim().length === 0 || assignedTo.length === 0 || !isValidDateRange(e.target.value, endDate)
                )
            }

            const handleEndDateChange = (e: InputEvent) => {
                setEndDate(e.target.value)
                setConfirmDisabled(
                    tempName.trim().length === 0 || assignedTo.length === 0 || !isValidDateRange(startDate, e.target.value)
                )
            }

            const confirmAdd = async () => {
                await new Request(`accounts/${account.id}/holidays`, () => loadHolidays(account)).post({
                    holiday_name: tempName,
                    assigned_to: assignedTo,
                    start_date: startDate,
                    end_date: endDate
                })
                closeModal()
            }

            return employees.length > 0 ? <>
                <h1>Add New Holiday</h1>
                <div className='modal-input-sec'>
                    <label style={{ marginRight: 10 }}>Name: </label>
                    <input
                        type='text'
                        placeholder='Holiday name'
                        value={tempName}
                        onChange={handleNameChange}
                        maxLength={40}
                    />
                </div>
                <div className='modal-input-sec'>
                    <label style={{ marginRight: 10 }}>Start Date: </label>
                    <input
                        type='date'
                        value={startDate}
                        onChange={handleStartDateChange}
                    />
                </div>
                <div className='modal-input-sec'>
                    <label style={{ marginRight: 10 }}>End Date: </label>
                    <input
                        type='date'
                        value={endDate}
                        onChange={handleEndDateChange}
                    />
                </div>
                <div className='modal-input-sec'>
                    <label style={{ marginRight: 10 }}>Assign to: </label>
                    <div className='checkboxes'>
                        {employees.map(employee => (
                            <div key={employee.id}>
                                <input
                                    type='checkbox'
                                    id={`employee-${employee.id}`}
                                    checked={assignedTo.includes(employee.id)}
                                    onChange={() => handleCheckboxChange(employee.id)}
                                />
                                <label htmlFor={`employee-${employee.id}`}>{employee.name}</label>
                            </div>
                        ))}
                    </div>
                </div>
                <button
                    onClick={confirmAdd}
                    disabled={isConfirmDisabled}
                    id={isConfirmDisabled ? 'disabled-confirm-btn' : ''}
                >
                    Add Holiday
                </button>
            </> :
            <>
                <h1>No Pediatrician Registered</h1>
                <p>Please add at least one pediatrician before adding a holiday.</p>
                <button onClick={() => { closeModal(); setContent('employees') }}>Add a Pediatrician</button>
            </>
        }

        setModalContent(<AddModalContent/>)
        openModal()
    }

    return <>
        <header>
            <section id='header-upper'>
                <section id='header-btns'>
                    <button onClick={openAddModal}>Add New Holiday</button>
                </section>
            </section>
            {holidays.length === 0 && <p className='header-msg'>Holidays are optional when generating a shift schedule. You can add ones here by clicking the &quot;Add New Holiday&quot; button.</p>}
        </header>
        {holidays.length > 0 && (
            <div className='card-container'>
                {holidays.map(h => <HolidayCard {...h} key={h.id}/>)}
            </div>
        )}
    </>
}