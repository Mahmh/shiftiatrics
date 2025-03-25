import { useContext, useState } from 'react'
import { dashboardContext } from '@context'
import { Icon, Request, Choice, getAccountLimits } from '@utils'
import { MAX_WORK_HOURS } from '@const'
import type { Employee, InputEvent } from '@types'
import editIcon from '@icons/edit.png'
import removeIcon from '@icons/remove.png'

const EmployeeCard = ({ id, name, minWorkHours, maxWorkHours }: Employee) => {
    const { account, settings, setModalContent, openModal, closeModal, loadEmployees, loadHolidays } = useContext(dashboardContext)

    /** Displays a modal for editing employee details */
    const openEditModal = () => {
        const EditModalContent = () => {
            const [tempName, setTempName] = useState(name)
            const [tempMinWorkHours, setTempMinWorkHours] = useState<number>(minWorkHours ?? 0)
            const [tempMaxWorkHours, setTempMaxWorkHours] = useState<number>(maxWorkHours ?? 0)
            const [isConfirmDisabled, setConfirmDisabled] = useState(
                tempName.trim().length < 3 ||
                (settings.minMaxWorkHoursEnabled && (
                    (minWorkHours !== undefined && tempMinWorkHours <= 0) ||
                    (maxWorkHours !== undefined && tempMaxWorkHours <= 0) ||
                    (tempMinWorkHours > tempMaxWorkHours) ||
                    (tempMinWorkHours > MAX_WORK_HOURS) ||
                    (tempMaxWorkHours > MAX_WORK_HOURS)
                ))
            )
    
            const handleNameChange = (e: InputEvent) => {
                const newName = e.target.value
                setTempName(newName)
                setConfirmDisabled(
                    newName.trim().length < 3 ||
                    (settings.minMaxWorkHoursEnabled && (
                        (minWorkHours !== undefined && tempMinWorkHours <= 0) ||
                        (maxWorkHours !== undefined && tempMaxWorkHours <= 0) ||
                        (tempMinWorkHours > tempMaxWorkHours) ||
                        (tempMinWorkHours > MAX_WORK_HOURS) ||
                        (tempMaxWorkHours > MAX_WORK_HOURS)
                    ))
                )
            }
    
            const handleMinWorkHoursChange = (e: InputEvent) => {
                const minHours = parseInt(e.target.value) || minWorkHours || 0
                setTempMinWorkHours(minHours)
                setConfirmDisabled(
                    tempName.trim().length < 3 ||
                    (settings.minMaxWorkHoursEnabled && (
                        (minHours <= 0) ||
                        (tempMaxWorkHours <= 0) ||
                        (minHours > tempMaxWorkHours) ||
                        (minHours > MAX_WORK_HOURS) ||
                        (tempMaxWorkHours > MAX_WORK_HOURS)
                    ))
                )
            }
    
            const handleMaxWorkHoursChange = (e: InputEvent) => {
                const maxHours = parseInt(e.target.value) || maxWorkHours || 0
                setTempMaxWorkHours(maxHours)
                setConfirmDisabled(
                    tempName.trim().length < 3 ||
                    (settings.minMaxWorkHoursEnabled && (
                        (tempMinWorkHours <= 0) ||
                        (maxHours <= 0) ||
                        (tempMinWorkHours > maxHours) ||
                        (tempMinWorkHours > MAX_WORK_HOURS) ||
                        (maxHours > MAX_WORK_HOURS)
                    ))
                )
            }
    
            const confirmEdit = async () => {
                await new Request(`employees/${id}`, () => loadEmployees(account)).patch({
                    employee_name: tempName,
                    min_work_hours: settings.minMaxWorkHoursEnabled ? tempMinWorkHours : undefined,
                    max_work_hours: settings.minMaxWorkHoursEnabled ? tempMaxWorkHours : undefined,
                })
                closeModal()
            }
    
            return (
                <>
                    <h2>Edit Employee</h2>
                    <div className='modal-input-sec'>
                        <label style={{ marginRight: 10 }}>Name: </label>
                        <input
                            type='text'
                            placeholder='New name'
                            value={tempName}
                            onChange={handleNameChange}
                            maxLength={40}
                        />
                    </div>
                    {settings.minMaxWorkHoursEnabled && (
                        <>
                            <div className='modal-input-sec'>
                                <label style={{ marginRight: 10 }}>Minimum work hours per month: </label>
                                <input
                                    type='number'
                                    value={tempMinWorkHours}
                                    onChange={handleMinWorkHoursChange}
                                    min={0}
                                    max={MAX_WORK_HOURS}
                                />
                            </div>
                            <div className='modal-input-sec'>
                                <label style={{ marginRight: 10 }}>Maximum work hours per month: </label>
                                <input
                                    type='number'
                                    value={tempMaxWorkHours}
                                    onChange={handleMaxWorkHoursChange}
                                    min={0}
                                    max={MAX_WORK_HOURS}
                                />
                            </div>
                        </>
                    )}
                    <button
                        onClick={confirmEdit}
                        disabled={isConfirmDisabled}
                        id={isConfirmDisabled ? 'disabled-confirm-btn' : ''}
                    >
                        Confirm
                    </button>
                </>
            )
        }

        setModalContent(<EditModalContent/>)
        openModal()
    }

    /** Displays a modal for confirmation of employee deletion  */
    const openDeleteModal = () => {
        const confirmDelete = async () => {
            await new Request(`employees/${id}`, () => { loadEmployees(account); loadHolidays(account) }).delete()
            closeModal()
        }

        setModalContent(<>
            <h1>Remove Pediatrician &quot;{name}&quot;?</h1>
            <p>This will remove the pediatrician and their name from any assigned holidays. Holidays that only include this pediatrician will also be deleted.</p>
            <Choice onYes={confirmDelete} onNo={closeModal}/>
        </>)
        openModal()
    }

    return (
        <div className='dashboard-card'>
            <div className='dashboard-card-details' style={minWorkHours && maxWorkHours && settings.minMaxWorkHoursEnabled ? { paddingBottom: 10 } : {}}>
                <h1>{name}</h1>
                {minWorkHours && settings.minMaxWorkHoursEnabled && <span><b>Min work hours:</b> {minWorkHours}</span>}
                {maxWorkHours && settings.minMaxWorkHoursEnabled && <span><b>Max work hours:</b> {maxWorkHours}</span>}
            </div>
            <div>
                <button onClick={openEditModal}><Icon src={editIcon} alt='Edit'/></button>
                <button onClick={openDeleteModal}><Icon src={removeIcon} alt='Remove'/></button>
            </div>
        </div>
    )
}


export default function Employees() {
    const { account, subscription, employees, settings, setModalContent, openModal, closeModal, loadEmployees } = useContext(dashboardContext)
    const { maxNumPediatricians } = getAccountLimits(subscription)

    /** Displays a modal for adding an employee */
    const openAddModal = () => {
        const AddModalContent = () => {
            const [tempName, setTempName] = useState('')
            const [tempMinWorkHours, setTempMinWorkHours] = useState<number>(0)
            const [tempMaxWorkHours, setTempMaxWorkHours] = useState<number>(0)
            const [isConfirmDisabled, setConfirmDisabled] = useState(true)

            const handleNameChange = (e: InputEvent) => {
                const newName = e.target.value
                setTempName(newName)
                setConfirmDisabled(
                    newName.trim().length < 3 ||
                    (settings.minMaxWorkHoursEnabled && (
                        tempMinWorkHours <= 0 ||
                        tempMaxWorkHours <= 0 ||
                        tempMinWorkHours > tempMaxWorkHours ||
                        tempMinWorkHours > MAX_WORK_HOURS ||
                        tempMaxWorkHours > MAX_WORK_HOURS
                    ))
                )
            }
    
            const handleMinWorkHoursChange = (e: InputEvent) => {
                const minHours = parseInt(e.target.value) || 0
                setTempMinWorkHours(minHours)
                setConfirmDisabled(
                    tempName.trim().length < 3 ||
                    (settings.minMaxWorkHoursEnabled && (
                        minHours <= 0 ||
                        tempMaxWorkHours <= 0 ||
                        minHours > tempMaxWorkHours ||
                        minHours > MAX_WORK_HOURS ||
                        tempMaxWorkHours > MAX_WORK_HOURS
                    ))
                )
            }
    
            const handleMaxWorkHoursChange = (e: InputEvent) => {
                const maxHours = parseInt(e.target.value) || 0
                setTempMaxWorkHours(maxHours)
                setConfirmDisabled(
                    tempName.trim().length < 3 ||
                    (settings.minMaxWorkHoursEnabled && (
                        tempMinWorkHours <= 0 ||
                        maxHours <= 0 ||
                        tempMinWorkHours > maxHours ||
                        tempMinWorkHours > MAX_WORK_HOURS ||
                        maxHours > MAX_WORK_HOURS
                    ))
                )
            }
    
            const confirmAdd = async () => {
                await new Request(`accounts/${account.id}/employees`, () => loadEmployees(account)).post({
                    employee_name: tempName,
                    min_work_hours: settings.minMaxWorkHoursEnabled ? tempMinWorkHours : undefined,
                    max_work_hours: settings.minMaxWorkHoursEnabled ? tempMaxWorkHours : undefined,
                })
                closeModal()
            }
    
            return (
                <>
                    <h1>Add New Pediatrician</h1>
                    <section className='modal-input-sec'>
                        <label style={{ marginRight: 10 }}>Name: </label>
                        <input
                            type='text'
                            placeholder='Pediatrician name'
                            value={tempName}
                            onChange={handleNameChange}
                            maxLength={40}
                        />
                    </section>
                    {settings.minMaxWorkHoursEnabled && (
                        <>
                            <section className='modal-input-sec'>
                                <label style={{ marginRight: 10 }}>Minimum work hours per month: </label>
                                <input
                                    type='number'
                                    value={tempMinWorkHours}
                                    onChange={handleMinWorkHoursChange}
                                    min={0}
                                    max={MAX_WORK_HOURS}
                                />
                            </section>
                            <section className='modal-input-sec'>
                                <label style={{ marginRight: 10 }}>Maximum work hours per month: </label>
                                <input
                                    type='number'
                                    value={tempMaxWorkHours}
                                    onChange={handleMaxWorkHoursChange}
                                    min={0}
                                    max={MAX_WORK_HOURS}
                                />
                            </section>
                        </>
                    )}
                    <button
                        onClick={confirmAdd}
                        disabled={isConfirmDisabled}
                        id={isConfirmDisabled ? 'disabled-confirm-btn' : ''}
                    >
                        Add Pediatrician
                    </button>
                </>
            )
        }
    
        const SubLimitModalContent = () =>  <>
            <h1>Pediatrician Limit Reached</h1>
            <p>
            You have reached the maximum number of pediatricians allowed ({maxNumPediatricians}). 
            Please upgrade your plan to add more.
            </p>
        </>

        setModalContent(
            employees.length < maxNumPediatricians
            ? <AddModalContent/>
            : <SubLimitModalContent/>
        )
        openModal()
    }

    return <>
        <header>
            <section id='header-upper'>
                <section id='header-btns'>
                    <button onClick={openAddModal}>Add New Pediatrician</button>
                </section>
            </section>
            {employees.length === 0 && <p className='header-msg'>No pediatrician registered.</p>}
        </header>
        {
            employees.length > 0 && 
            <div className='card-container'>{employees.map(emp => 
                <EmployeeCard id={emp.id} name={emp.name} key={emp.id} minWorkHours={emp.minWorkHours} maxWorkHours={emp.maxWorkHours}
            />)}</div>
        }
    </>
}