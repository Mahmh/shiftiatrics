import { useCallback, useContext, useState, useMemo } from 'react'
import { AppContext, nullAccount } from '@context'
import { Choice, Request } from '@utils'
import type { Account } from '@types'

export default function Account() {
    const { account, setAccount, employees, shifts, openModal, closeModal, setModalContent } = useContext(AppContext)
    const employeeCountText = useMemo(
        () => `${employees.length} employee${employees.length === 1 ? '' : 's'}`,
        [employees.length]
    )
    const shiftCountText = useMemo(
        () => `${shifts.length} shift${shifts.length === 1 ? '' : 's'} per day`,
        [shifts.length]
    )

    /** Logs out of the account */
    const logOut = useCallback(() => setAccount(nullAccount), [setAccount])

    /** Sends an API request to delete the account */
    const deleteAccount = useCallback(async () => {
        await new Request(
            'accounts',
            () => {},
            { username: account.username, password: account.password }
        ).delete()
        logOut()
    }, [account, logOut])

    /** Displays an account deletion modal */
    const openDeleteModal = useCallback(() => {
        setModalContent(<>
            <h1>Delete Your Account?</h1>
            <Choice onYes={deleteAccount} onNo={closeModal}/>
        </>)
        openModal()
    }, [deleteAccount, closeModal, openModal, setModalContent])

    /** Displays a modal for confirming log-out */
    const openLogOutModal = useCallback(() => {
        setModalContent(<>
            <h1>Log Out?</h1>
            <Choice onYes={logOut} onNo={closeModal}/>
        </>)
        openModal()
    }, [logOut, closeModal, openModal, setModalContent])

    /** Displays a modal for editing the account's username */
    const openEditUsernameModal = useCallback(() => {
        const EditUsernameModalContent = () => {
            const [tempUsername, setTempUsername] = useState(account.username)
            const [isConfirmDisabled, setConfirmDisabled] = useState(tempUsername.trim().length < 3 || account.username === tempUsername)

            const handleUsernameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
                const newUsername = e.target.value
                setTempUsername(newUsername)
                setConfirmDisabled(newUsername.trim().length < 3 || account.username === newUsername)
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
                <section style={{ marginBottom: 20 }}>
                    <label style={{ marginRight: 10 }}>Username: </label>
                    <input
                        type='text'
                        placeholder='New username'
                        value={tempUsername}
                        onChange={handleUsernameChange}
                        maxLength={40}
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

        setModalContent(<EditUsernameModalContent/>)
        openModal()
    }, [account.username, account.password, setAccount, openModal, closeModal, setModalContent])

    /** Displays a modal for creating a new password */
    const openChangePasswordModal = useCallback(() => {
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
                <section className='modal-input-sec'>
                    <label style={{ marginRight: 10 }}>New password: </label>
                    <input
                        type='password'
                        placeholder='New password'
                        value={tempNewPassword}
                        onChange={handleNewPasswordChange}
                        maxLength={40}
                    />
                </section>
                <section className='modal-input-sec'>
                    <label style={{ marginRight: 10 }}>Confirm password: </label>
                    <input
                        type='password'
                        placeholder='Confirm password'
                        value={tempConfirmPassword}
                        onChange={handleConfirmPasswordChange}
                        maxLength={40}
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

        setModalContent(<ChangePasswordModalContent/>)
        openModal()
    }, [account.username, account.password, setAccount, openModal, closeModal, setModalContent])

    return <>
        <div id='account-card'>
            <h1>{account.username}</h1>
            <div>{employeeCountText}</div>
            <div>{shiftCountText}</div>
        </div>
        <div id='account-actions-card'>
            <button id='edit-account-btn' onClick={openEditUsernameModal}>Edit Username</button>
            <button id='edit-account-btn' onClick={openChangePasswordModal}>Change Password</button>
            <button id='log-out-btn' onClick={openLogOutModal}>Log Out</button>
            <button id='delete-account-btn' onClick={openDeleteModal}>Delete Account</button>
        </div>
    </>
}