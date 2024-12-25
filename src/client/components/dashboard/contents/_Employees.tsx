import { useContext, useState } from 'react'
import { AppContext } from '@context'
import { Employee } from '@types'
import { Icon, Request } from '@utils'
import editIcon from '@icons/edit.png'
import removeIcon from '@icons/remove.png'

const EmployeeCard = ({ id, name }: Employee) => {
    const { setModalContent, openModal, closeModal, loadEmployees } = useContext(AppContext)

    const openEditModal = () => {
        const EditModalContent = () => {
            const [tempName, setTempName] = useState(name)
            const [isConfirmDisabled, setConfirmDisabled] = useState(tempName.length < 3)

            const handleNameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
                const newName = e.target.value
                setTempName(newName)
                setConfirmDisabled(newName.length < 3)
            }

            const confirmEdit = async () => {
                await new Request(`employees/${id}`, () => loadEmployees(), { employee_name: tempName }).patch()
                closeModal()
            }

            return <>
                <h2>Edit Employee</h2>
                <div style={{ marginBottom: 20 }}>
                    <label style={{ marginRight: 10 }}>Name: </label>
                    <input
                        type='text'
                        placeholder='New name'
                        value={tempName}
                        onChange={handleNameChange}
                        maxLength={40}
                    />
                </div>
                <button
                    onClick={confirmEdit}
                    disabled={isConfirmDisabled}
                    id={isConfirmDisabled ? 'disabled-confirm-btn' : ''}
                >Confirm</button>
            </>
        }

        openModal()
        setModalContent(<EditModalContent/>)
    }

    const openDeleteModal = () => {
        const confirmDelete = async () => {
            await new Request(`employees/${id}`, () => loadEmployees()).delete()
            closeModal()
        }

        openModal()
        setModalContent(<>
            <h2>Remove Employee "{name}"?</h2>
            <div style={{ display: 'flex', gap: 10 }}>
                <button style={{ width: '100%' }} onClick={confirmDelete}>Yes</button>
                <button style={{ width: '100%' }} onClick={closeModal}>No</button>
            </div>
        </>)
    }

    return (
        <div className='employee-card'>
            <h1>{name}</h1>
            <div>
                <button onClick={openEditModal}><Icon src={editIcon} alt='Edit'/></button>
                <button onClick={openDeleteModal}><Icon src={removeIcon} alt='Remove'/></button>
            </div>
        </div>
    )
}


export default function Employees() {
    const { account, employees, setModalContent, openModal, closeModal, loadEmployees } = useContext(AppContext)

    const openAddModal = () => {
        const AddModalContent = () => {
            const [tempName, setTempName] = useState('')
            const [isConfirmDisabled, setConfirmDisabled] = useState(true)

            const handleNameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
                const newName = e.target.value
                setTempName(newName)
                setConfirmDisabled(newName.length < 3)
            }

            const confirmAdd = async () => {
                await new Request(
                    `accounts/${account.id}/employees`,
                    () => loadEmployees(),
                    { employee_name: tempName }
                ).post()
                closeModal()
            }

            return <>
                <h1>Add New Employee</h1>
                <div>
                    <label style={{ marginRight: 10 }}>Name: </label>
                    <input
                        type='text'
                        placeholder='Employee name'
                        value={tempName}
                        onChange={handleNameChange}
                        maxLength={40}
                    />
                </div>
                <button
                    onClick={confirmAdd}
                    disabled={isConfirmDisabled}
                    id={isConfirmDisabled ? 'disabled-confirm-btn' : ''}
                >Add Employee</button>
            </>
        }

        openModal()
        setModalContent(<AddModalContent/>)
    }

    return <>
            {
                employees.length > 0 
                ? employees.map(emp => <EmployeeCard id={emp.id} name={emp.name} key={emp.id} />)
                : <div>No employees registered.</div>
            }
            <button id='add-employee-btn' onClick={openAddModal}>Add New Employee</button>
    </>
}