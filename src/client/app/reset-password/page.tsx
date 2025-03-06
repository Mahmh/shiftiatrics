'use client'
import { useEffect, useMemo, useState } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { Request, setMetadata, sanitizeInput, validateEmail, validatePassword } from '@utils'
import { TOO_MANY_REQS_MSG } from '@const'
import RegularPage from '@regpage'

const NoResetToken = () => {
    const [email, setEmail] = useState('')
    const [error, setError] = useState<string|null>(null)
    const [isLoading, setIsLoading] = useState(false)
    const [submitted, setSubmitted] = useState(false)

    const requestResetPassword = async () => {
        setError(null)
        setIsLoading(true)
    
        const sanitizedEmail = sanitizeInput(email)
        const validationError = validateEmail(sanitizedEmail)
        if (validationError) {
            setError(validationError)
            setIsLoading(false)
            return
        }

        await new Request(
            'auth/request_reset_password',
            () => setSubmitted(true),
            (error) => {
                setIsLoading(false)
                if (error.includes('429')) { setError(TOO_MANY_REQS_MSG); return }
                setError(
                    error.includes('Invalid credentials') || error.includes('does not exist')
                    ? 'You have entered invalid credentials.'
                    : error
                )
            },
            false
        ).post({ email })
    }
    
    return submitted
    ? <>
        <section>
            <h1>Reset Password Request Sent</h1>
            <p>
                We&apos;ve sent you a password reset link for the account associated with the email you provided.
                Please check your inbox and follow the instructions to reset your password.
            </p>
        </section>
    </> 
    : <>
        <section>
            <h1>Reset Password Request</h1>
            <p>We will send you an email for you to reset your password.</p>
        </section>
        <section>
            <label>Email</label>
            <input type='text' value={email} onChange={e => setEmail(e.target.value)} disabled={isLoading}/>
        </section>
        <p className='error' style={error === null ? { visibility: 'hidden' } : {}}>{error}</p>
        <button className='cred-submit-btn' onClick={requestResetPassword} disabled={isLoading}>
            {isLoading ? 'Submitting...' : 'Submit'}
        </button>
    </>
}

const WithResetToken = ({ resetToken }: { resetToken: string }) => {
    const router = useRouter()
    const [password, setPassword] = useState('')
    const [confirmPassword, setConfirmPassword] = useState('')
    const [error, setError] = useState<string|null>(null)
    const [isLoading, setIsLoading] = useState(false)
    const [submitted, setSubmitted] = useState(false)

    const resetPassword = async () => {
        setError(null)
        setIsLoading(true)
    
        const validationError1 = validatePassword(sanitizeInput(password))
        const validationError2 = validatePassword(sanitizeInput(confirmPassword))
        if (validationError1) {
            setError(validationError1)
            setIsLoading(false)
            return
        } else if (validationError2) {
            setError(validationError2)
            setIsLoading(false)
            return
        }

        if (password !== confirmPassword) {
            setError('New password and confirmation do not match. Please try again.')
            setIsLoading(false)
            return
        }

        await new Request(
            'auth/reset_password',
            () => setSubmitted(true),
            (error) => {
                setIsLoading(false)
                if (error.includes('429')) { setError(TOO_MANY_REQS_MSG); return }
                setError(
                    error.includes('Invalid credentials') || error.includes('does not exist')
                    ? 'You have entered invalid credentials.'
                    : error
                )
            },
            false
        ).patch({ new_password: password, reset_token: resetToken })
    }

    return submitted
    ? <>
        <section>
            <h1>Confirmed</h1>
            <p>Your password was successfully reset. Now, try to log in back.</p>
            <button className='cred-submit-btn' style={{ marginTop: 40 }} onClick={() => router.push('/login')}>Log In</button>
        </section>
    </>
    : <>
        <section>
            <h1>Reset Your Password</h1>
        </section>
        <section>
            <label>New Password</label>
            <input type='password' value={password} onChange={e => setPassword(e.target.value)} disabled={isLoading}/>
        </section>
        <section>
            <label>Confirm Password</label>
            <input type='password' value={confirmPassword} onChange={e => setConfirmPassword(e.target.value)} disabled={isLoading}/>
        </section>
        <p className='error' style={error === null ? { visibility: 'hidden' } : {}}>{error}</p>
        <button className='cred-submit-btn' onClick={resetPassword} disabled={isLoading}>
            {isLoading ? 'Confirming...' : 'Confirm'}
        </button>
    </>
}

export default function ResetPassword() {
    const params = useSearchParams()
    const resetToken = useMemo(() => params.get('token'), [params])

    useEffect(() => {
        setMetadata({
            title: 'Reset Password | Shiftiatrics',
            description: 'Reset your password in case you forgot it'
        })
    }, [])

    return (
        <RegularPage id='reset-password-page' transparentHeader={true} footerMarginTop={false}>
            <div id='mid-container'>
                {
                    resetToken
                    ? <WithResetToken resetToken={resetToken}/>
                    : <NoResetToken/>
                }
            </div>
        </RegularPage>
    )
}