import { useContext } from 'react'
import { dashboardContext } from '@context'
import { openRequestChangeModal } from '@utils'
import type { Employee, Team } from '@types'

export default function Staff() {
    const { teams, employees, setModalContent, openModal } = useContext(dashboardContext)
    return <>
        <header>
            <section id='header-upper'>
                <section id='header-btns'>
                    <button onClick={() => openRequestChangeModal('Register Staff', setModalContent, openModal)}>Request Change</button>
                </section>
            </section>
            {employees.length === 0 && <p className='header-msg'>No staff registered.</p>}
        </header>
        {
            teams.length > 0 &&
            employees.length > 0 &&
            <div className='teams-container'>
                {teams.map(t => <TeamCard key={t.id} id={t.id} name={t.name} teamEmps={employees.filter(emp => emp.teamId === t.id)}/>)}
            </div>
        }
    </>
}


const EmployeeCard = ({ name, minWorkHours, maxWorkHours }: Employee) => (
    <section className='employee-card dashboard-card'>
        <h1>{name}</h1>
        <div className='dashboard-card-details'>
            {minWorkHours && <span><b>Min work hours:</b> {minWorkHours}</span>}
            {maxWorkHours && <span><b>Max work hours:</b> {maxWorkHours}</span>}
        </div>
    </section>
)


const TeamCard = ({ name, teamEmps }: Team & { teamEmps: Employee[] }) => (
    <section className='team-card'>
        <h1 className='team-name'>{name}</h1>
        {teamEmps.length === 0 
        ? <p className='no-staff'>No staff member was registered in this team.</p> 
        : <div className='card-container'>
            {teamEmps.map(emp => 
                <EmployeeCard
                    id={emp.id}
                    name={emp.name}
                    key={emp.id}
                    minWorkHours={emp.minWorkHours}
                    maxWorkHours={emp.maxWorkHours}
                    teamId={emp.teamId}
                />
            )}
        </div>
        }
    </section>
)