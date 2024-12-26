import { useContext, useState } from 'react'
import { AppContext, nullAccount } from '@context'
import { Choice, Request } from '@utils'
import type { Account } from '@types'

export default function Account() {
    const { account, setAccount, employees, shifts, openModal, closeModal, setModalContent } = useContext(AppContext)

    const logOut = () =>  setAccount(nullAccount)

    const deleteAccount = async () => {
        await new Request(
            'accounts',
            () => {},
            { username: account.username, password: account.password }
        ).delete()
        logOut()
    }

    const openDeleteModal = () => {
        setModalContent(<>
            <h1>Delete Your Account?</h1>
            <Choice onYes={deleteAccount} onNo={closeModal}/>
        </>)
        openModal()
    }

    const openLogOutModal = () => {
        setModalContent(<>
            <h1>Log Out?</h1>
            <Choice onYes={logOut} onNo={closeModal}/>
        </>)
        openModal()
    }

    const openEditUsernameModal = () => {
        const EditUsernameModalContent = () => {
            const [tempUsername, setTempUsername] = useState(account.username)
            const [isConfirmDisabled, setConfirmDisabled] = useState(tempUsername.trim().length < 3)

            const handleUsernameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
                const newUsername = e.target.value
                setTempUsername(newUsername)
                setConfirmDisabled(newUsername.trim().length < 3)
            }

            const confirmEdit = async () => {
                await new Request(
                    'accounts',
                    resAccount => setAccount({ ...resAccount, id: resAccount.account_id }),
                    {
                        cred: { username: account.username, password: account.password },
                        updates: { username: tempUsername }
                    }
                ).patch()
                closeModal()
            }

            return <>
                <h2>Edit Username</h2>
                <div style={{ marginBottom: 20 }}>
                    <label style={{ marginRight: 10 }}>Username: </label>
                    <input
                        type='text'
                        placeholder='New username'
                        value={tempUsername}
                        onChange={handleUsernameChange}
                        maxLength={40}
                    />
                </div>
                <button
                    onClick={confirmEdit}
                    disabled={isConfirmDisabled}
                    id={isConfirmDisabled ? 'disabled-confirm-btn' : ''}
                >
                    Confirm
                </button>
            </>
        }

        setModalContent(<EditUsernameModalContent/>)
        openModal()
    }

    const openChangePasswordModal = () => {
        const ChangePasswordModalContent = () => {
            const [tempNewPassword, setNewPassword] = useState('')
            const [tempConfirmPassword, setConfirmPassword] = useState('')
            const [isConfirmDisabled, setConfirmDisabled] = useState(tempNewPassword.trim().length < 3)

            const handleNewPasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
                const newPassword = e.target.value
                setNewPassword(newPassword)
                setConfirmDisabled(newPassword.trim().length < 3 || newPassword.trim() !== tempConfirmPassword.trim())
            }

            const handleConfirmPasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
                const confirmPassword = e.target.value
                setConfirmPassword(confirmPassword)
                setConfirmDisabled(tempNewPassword.trim().length < 3 || tempNewPassword.trim() !== confirmPassword.trim())
            }

            const confirmEdit = async () => {
                await new Request(
                    'accounts',
                    resAccount => setAccount({ ...resAccount, id: resAccount.account_id }),
                    {
                        cred: { username: account.username, password: account.password },
                        updates: { password: tempNewPassword }
                    }
                ).patch()
                closeModal()
            }

            return <>
                <h2>Edit Username</h2>
                <div className='modal-input-div'>
                    <label style={{ marginRight: 10 }}>New password: </label>
                    <input
                        type='password'
                        placeholder='New password'
                        value={tempNewPassword}
                        onChange={handleNewPasswordChange}
                        maxLength={40}
                    />
                </div>
                <div className='modal-input-div'>
                    <label style={{ marginRight: 10 }}>Confirm password: </label>
                    <input
                        type='password'
                        placeholder='Confirm password'
                        value={tempConfirmPassword}
                        onChange={handleConfirmPasswordChange}
                        maxLength={40}
                    />
                </div>
                <button
                    onClick={confirmEdit}
                    disabled={isConfirmDisabled}
                    id={isConfirmDisabled ? 'disabled-confirm-btn' : ''}
                >
                    Confirm
                </button>
            </>
        }

        setModalContent(<ChangePasswordModalContent/>)
        openModal()
    }

    return <>
        <div id='account-card'>
            <h1>{account.username}</h1>
            <div>{`${employees.length} employee${employees.length === 1 ? '' : 's'}`}</div>
            <div>{`${shifts.length} shift${shifts.length === 1 ? '' : 's'}`}</div>
        </div>
        <button id='edit-account-btn' onClick={openEditUsernameModal}>Edit Username</button>
        <button id='edit-account-btn' onClick={openChangePasswordModal}>Change Password</button>
        <button id='log-out-btn' onClick={openLogOutModal}>Log Out</button>
        <button id='delete-account-btn' onClick={openDeleteModal}>Delete Account</button>
    </>
}