import { useContext } from 'react'
import { DashboardContext } from '@context'
import { Icon } from '@utils'
import closeIcon from '@icons/close.png'

export default function Modal() {
    const { isModalOpen, setIsModalOpen, modalContent } = useContext(DashboardContext)

    return (
        <div className={`backdrop ${isModalOpen ? 'open' : 'closed'}`} onClick={() => setIsModalOpen(false)}>
            <div id='modal' className={isModalOpen ? 'open' : 'closed'} onClick={(e) => e.stopPropagation()}>
                <button id='close-modal-btn' onClick={() => setIsModalOpen(false)}>
                    <Icon src={closeIcon} alt='Close' />
                </button>
                <div id='modal-content'>{modalContent}</div>
            </div>
        </div>
    )
}