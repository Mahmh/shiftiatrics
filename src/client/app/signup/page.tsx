'use client'
import { useRouter } from 'next/navigation'
import { useContext, useEffect, useState } from 'react'
import { Request, sanitizeInput, validateInput, setMetadata } from '@utils'
import { TOO_MANY_REQS_MSG } from '@const'
import { isLoggedIn, ContinueWithGoogle } from '@auth'
import { dashboardContext } from '@context'
import Link from 'next/link'
import RegularPage from '@regpage'

export default function Signup() {
    const router = useRouter()
    const { setAccount } = useContext(dashboardContext)
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [error, setError] = useState<string|null>(null)
    const [isLoading, setIsLoading] = useState(false)
    const [ToSAccepted, setToSAccepted] = useState(false)

    const handleSignup = async () => {
        if (!ToSAccepted) {
            setError('Before continuing, please accept the terms of service by checking the checkbox above.')
            return
        }

        setError(null)
        setIsLoading(true)

        const sanitizedEmail = sanitizeInput(email)
        const sanitizedPassword = sanitizeInput(password)
        const validationError = validateInput(sanitizedEmail, sanitizedPassword)
        if (validationError) {
            setError(validationError)
            setIsLoading(false)
            return
        }

        await new Request(
            'accounts/signup',
            (data: { account_id: number, email: string, password: string }) => {
                setIsLoading(false)
                setAccount({ id: data.account_id, email: data.email })
                router.push('/dashboard')
            },
            (error) => {
                setIsLoading(false)
                setError(error.includes('429') ? TOO_MANY_REQS_MSG : error)
            }
        ).post({ email: sanitizedEmail, password: sanitizedPassword })
    }

    useEffect(() => {
        setMetadata({
            title: 'Sign Up | Shiftiatrics',
            description: 'Create an account to view your dashboard'
        })
    }, [])

    useEffect(() => {
        (async () => {
            if (await isLoggedIn()) router.push('/dashboard')
        })()
    }, [router])

    return (
        <RegularPage name='Sign Up' id='signup-page' transparentHeader={true} footerMarginTop={false}>
            <div id='mid-container'>
                <section>
                    <label>Email</label>
                    <input type='text' value={email} onChange={(e) => setEmail(e.target.value)} disabled={isLoading} maxLength={32}/>
                </section>
                <section>
                    <label>Password</label>
                    <input type='password' value={password} onChange={(e) => setPassword(e.target.value)} disabled={isLoading} maxLength={32}/>
                </section>
                <section id='agree-to-tos-sec'>
                    <input type='checkbox' onChange={e => setToSAccepted(e.target.checked)} required/>
                    <label>I agree to Shiftiatrics&apos; <Link href='/legal/terms'>Terms of Service</Link>.</label>
                </section>
                <p className='error' style={error === null ? { visibility: 'hidden', margin: 0 } : {}}>{error}</p>
                <button className='cred-submit-btn' onClick={handleSignup} disabled={isLoading}>
                    {isLoading ? 'Signing up...' : 'Sign Up'}
                </button>
                <p>Already have an account? <Link href='/login'>Log In</Link></p>
                <ContinueWithGoogle/>
            </div>
        </RegularPage>
    )
}