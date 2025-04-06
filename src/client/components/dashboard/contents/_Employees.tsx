import { useContext } from 'react'
import { dashboardContext } from '@context'
import { openRequestChangeModal } from '@utils'
import type { Employee } from '@types'

export default function Employees() {
    const { employees, setModalContent, openModal } = useContext(dashboardContext)
    return <>
        <header>
            <section id='header-upper'>
                <section id='header-btns'>
                    <button onClick={() => openRequestChangeModal('Register a Pediatrican', setModalContent, openModal)}>Request Change</button>
                </section>
            </section>
            {employees.length === 0 && <p className='header-msg'>No pediatrician registered.</p>}
        </header>
        {employees.length > 0 && 
            <div className='card-container'>
                {employees.map(emp => 
                    <EmployeeCard
                        id={emp.id}
                        name={emp.name}
                        key={emp.id}
                        minWorkHours={emp.minWorkHours}
                        maxWorkHours={emp.maxWorkHours}
                    />
                )}
            </div>
        }
    </>
}


const EmployeeCard = ({ name, minWorkHours, maxWorkHours }: Employee) => (
    <div className='dashboard-card'>
        <h1>{name}</h1>
        <div className='dashboard-card-details'>
            {minWorkHours && <span><b>Min work hours:</b> {minWorkHours}</span>}
            {maxWorkHours && <span><b>Max work hours:</b> {maxWorkHours}</span>}
        </div>
    </div>
)