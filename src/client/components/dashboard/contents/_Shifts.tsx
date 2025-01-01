import { useContext, useState } from 'react'
import { DashboardContext } from '@context'
import { Shift } from '@types'
import { Icon, Request, Choice, formatTimeToAMPM } from '@utils'
import editIcon from '@icons/edit.png'
import removeIcon from '@icons/remove.png'

const ShiftCard = ({ id, name, startTime, endTime }: Shift) => {
    const { setModalContent, openModal, closeModal, loadShifts } = useContext(DashboardContext)

    const openEditModal = () => {
        const EditModalContent = () => {
            const [tempName, setTempName] = useState(name)
            const [tempStartTime, setStartTime] = useState(startTime)
            const [tempEndTime, setEndTime] = useState(endTime)
            const [isConfirmDisabled, setConfirmDisabled] = useState(tempName.trim().length < 3 || tempName === name)

            const handleNameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
                const newName = e.target.value
                setTempName(newName)
                setConfirmDisabled(newName.trim().length < 3 || newName === name || !tempStartTime || !tempEndTime)
            }

            const handleStartTimeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
                setStartTime(e.target.value)
            }

            const handleEndTimeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
                setEndTime(e.target.value)
            }

            const confirmEdit = async () => {
                await new Request(`shifts/${id}`, () => loadShifts(), {
                    shift_name: tempName,
                    start_time: tempStartTime,
                    end_time: tempEndTime,
                }).patch()
                closeModal()
            }

            return <>
                <h2>Edit Shift</h2>
                <section style={{ marginBottom: 10 }}>
                    <label style={{ marginRight: 10 }}>Name: </label>
                    <input
                        type='text'
                        placeholder='Shift name'
                        value={tempName}
                        onChange={handleNameChange}
                        maxLength={40}
                    />
                </section>
                <section style={{ marginBottom: 10 }}>
                    <label style={{ marginRight: 10 }}>Start Time: </label>
                    <input
                        type='time'
                        value={tempStartTime}
                        onChange={handleStartTimeChange}
                    />
                </section>
                <section style={{ marginBottom: 20 }}>
                    <label style={{ marginRight: 10 }}>End Time: </label>
                    <input
                        type='time'
                        value={tempEndTime}
                        onChange={handleEndTimeChange}
                    />
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
            await new Request(`shifts/${id}`, () => loadShifts()).delete()
            closeModal()
        }

        setModalContent(<>
            <h2>Remove Shift &quot;{name}&quot;?</h2>
            <Choice onYes={confirmDelete} onNo={closeModal}/>
        </>)
        openModal()
    }

    return (
        <div className='shift-card'>
            <div className='shift-details'>
                <h1>{name}</h1>
                <span><b>Starts:</b> {formatTimeToAMPM(startTime)}</span>
                <span><b>Ends:</b> {formatTimeToAMPM(endTime)}</span>
            </div>
            <div>
                <button onClick={openEditModal}>
                    <Icon src={editIcon} alt='Edit'/>
                </button>
                <button onClick={openDeleteModal}>
                    <Icon src={removeIcon} alt='Remove'/>
                </button>
            </div>
        </div>
    )
}

export default function Shifts() {
    const { account, shifts, setModalContent, openModal, closeModal, loadShifts } = useContext(DashboardContext)

    const openAddModal = () => {
        const AddModalContent = () => {
            const [tempName, setTempName] = useState('')
            const [tempStartTime, setStartTime] = useState('')
            const [tempEndTime, setEndTime] = useState('')
            const [isConfirmDisabled, setConfirmDisabled] = useState(true)

            const handleNameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
                const newName = e.target.value
                setTempName(newName)
                setConfirmDisabled(newName.trim().length === 0 || !tempStartTime || !tempEndTime)
            }

            const handleStartTimeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
                setStartTime(e.target.value)
                setConfirmDisabled(tempName.trim().length === 0 || !e.target.value || !tempEndTime)
            }

            const handleEndTimeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
                setEndTime(e.target.value)
                setConfirmDisabled(tempName.trim().length === 0 || !tempStartTime || !e.target.value)
            }

            const confirmAdd = async () => {
                await new Request(
                    `accounts/${account.id}/shifts`,
                    () => loadShifts(),
                    { shift_name: tempName, start_time: tempStartTime, end_time: tempEndTime }
                ).post()
                closeModal()
            }

            return <>
                <h1>Add New Shift</h1>
                <div className='modal-input-sec'>
                    <label style={{ marginRight: 10 }}>Name: </label>
                    <input
                        type='text'
                        placeholder='Shift name'
                        value={tempName}
                        onChange={handleNameChange}
                        maxLength={40}
                    />
                </div>
                <div className='modal-input-sec'>
                    <label style={{ marginRight: 10 }}>Start Time: </label>
                    <input
                        type='time'
                        value={tempStartTime}
                        onChange={handleStartTimeChange}
                    />
                </div>
                <div className='modal-input-sec'>
                    <label style={{ marginRight: 10 }}>End Time: </label>
                    <input
                        type='time'
                        value={tempEndTime}
                        onChange={handleEndTimeChange}
                    />
                </div>
                <button
                    onClick={confirmAdd}
                    disabled={isConfirmDisabled}
                    id={isConfirmDisabled ? 'disabled-confirm-btn' : ''}
                >
                    Add Shift
                </button>
            </>
        }

        setModalContent(<AddModalContent/>)
        openModal()
    }

    return <>
        <header>
            <section id='header-upper'>
                <section id='header-btns'>
                    <button onClick={openAddModal}>Add New Shift</button>
                </section>
            </section>
            {shifts.length === 0 && <p className='header-msg'>No shifts registered. You could add &quot;Day&quot;, &quot;Evening&quot;, &quot;Night&quot;, or any shift name that you find suitable for your use case.</p>}
        </header>
        {shifts.length > 0 && (
            <div className='card-container'>
                {shifts.map((shift) => (
                    <ShiftCard
                        id={shift.id}
                        name={shift.name}
                        startTime={shift.startTime}
                        endTime={shift.endTime}
                        key={shift.id}
                    />
                ))}
            </div>
        )}
    </>
}