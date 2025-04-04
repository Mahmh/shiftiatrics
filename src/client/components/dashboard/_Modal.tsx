import { useContext, useEffect, useState } from 'react'
import { dashboardContext } from '@context'
import { Icon } from '@utils'
import closeIcon from '@icons/close.png'

export default function Modal() {
    const { account, isModalOpen, setIsModalOpen, modalContent } = useContext(dashboardContext)
    const [isModalScrollable, setIsModalScrollable] = useState(false)

    useEffect(() => {
        const checkScreen = () => setIsModalScrollable(window.innerWidth <= 815)
        checkScreen()
        window.addEventListener('resize', checkScreen)
        return () => window.removeEventListener('resize', checkScreen)
    }, [setIsModalScrollable])

    return (
        <div 
            className={`backdrop ${isModalOpen ? 'open' : 'closed'}`}
            onClick={() => account.passwordChanged ? setIsModalOpen(false) : undefined}
        >
            <div
                id='modal'
                className={isModalOpen ? 'open' : 'closed'}
                onClick={(e) => e.stopPropagation()}
                style={isModalScrollable ? { overflowY: 'auto' } : {}}
            >
                {account.passwordChanged && <button id='close-modal-btn' onClick={() => setIsModalOpen(false)}>
                    <Icon src={closeIcon} alt='Close'/>
                </button>}
                <div
                    id='modal-content'
                    style={{
                        overflowY: isModalScrollable ? 'unset' : 'auto',
                        maxHeight: isModalScrollable ? '100%' : '45vh',
                    }}
                >
                    {modalContent}
                </div>
            </div>
        </div>
    )
}