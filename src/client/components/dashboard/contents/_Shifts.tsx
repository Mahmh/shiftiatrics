import { useContext } from 'react'
import { dashboardContext } from '@context'
import { formatTimeToAMPM, openRequestChangeModal } from '@utils'
import type { Shift } from '@types'

export default function Shifts() {
    const { shifts, setModalContent, openModal } = useContext(dashboardContext)
    return <>
        <header>
            <section id='header-upper'>
                <section id='header-btns'>
                    <button onClick={() => openRequestChangeModal(setModalContent, openModal)}>Request Change</button>
                </section>
            </section>
            {shifts.length === 0 && <p className='header-msg'>No shifts registered.</p>}
        </header>
        {shifts.length > 0 && (
            <div className='card-container'>
                {shifts.map(shift =>
                    <ShiftCard
                        id={shift.id}
                        name={shift.name}
                        startTime={shift.startTime}
                        endTime={shift.endTime}
                        key={shift.id}
                    />
                )}
            </div>
        )}
    </>
}


const ShiftCard = ({ name, startTime, endTime }: Shift) => (
    <div className='dashboard-card'>
        <div className='dashboard-card-details'>
            <h1>{name}</h1>
            <span><b>Starts:</b> {formatTimeToAMPM(startTime)}</span>
            <span><b>Ends:</b> {formatTimeToAMPM(endTime)}</span>
        </div>
    </div>
)