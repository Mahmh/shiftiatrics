'use client'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useContext, useEffect, useState } from 'react'
import { Request, sanitizeInput, validateInput } from '@utils'
import { TOO_MANY_REQS_MSG } from '@const'
import { isLoggedIn, ContinueWithGoogle } from '@auth'
import { dashboardContext } from '@context'
import RegularPage from '@regpage'

export default function Signup() {
    const router = useRouter()
    const { setAccount } = useContext(dashboardContext)
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [error, setError] = useState<string|'X'>('X')
    const [isLoading, setIsLoading] = useState(false)

    const handleSignup = async () => {
        setError('X')
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
                {error && <p className='error' style={error === 'X' ? { visibility: 'hidden' } : {}}>{error}</p>}
                <button className='cred-submit-btn' onClick={handleSignup} disabled={isLoading}>
                    {isLoading ? 'Signing up...' : 'Sign Up'}
                </button>
                <p>Already have an account? <Link href='/login'>Log In</Link></p>
                <ContinueWithGoogle/>
            </div>
        </RegularPage>
    )
}