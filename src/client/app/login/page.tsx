'use client'
import { useRouter, useSearchParams } from 'next/navigation'
import { useEffect, useState } from 'react'
import { Request, sanitizeInput, validateCred, setMetadata } from '@utils'
import { TOO_MANY_REQS_MSG } from '@const'
import { isLoggedIn, ContinueWithGoogle } from '@auth'
import Link from 'next/link'
import RegularPage from '@regpage'

export default function Login() {
    const router = useRouter()
    const params = useSearchParams()
    const plan = params.get('plan')
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [error, setError] = useState<string|null>(null)
    const [isLoading, setIsLoading] = useState(false)

    const handleLogin = async () => {
        setError(null)
        setIsLoading(true)

        const sanitizedEmail = sanitizeInput(email)
        const sanitizedPassword = sanitizeInput(password)
        const validationError = validateCred(sanitizedEmail, sanitizedPassword)
        if (validationError) {
            setError(validationError)
            setIsLoading(false)
            return
        }

        await new Request(
            'auth/login',
            () => {
                setIsLoading(false)
                router.push('/dashboard')
            },
            (error) => {
                setIsLoading(false)
                if (error.includes('429')) { setError(TOO_MANY_REQS_MSG); return }
                setError(
                    error.includes('Invalid credentials') || error.includes('does not exist')
                    ? 'You have entered invalid credentials.'
                    : error
                )
            }
        ).post({ email: sanitizedEmail, password: sanitizedPassword })
    }

    useEffect(() => {
        setMetadata({
            title: 'Log In | Shiftiatrics',
            description: 'Log in to view your dashboard'
        })
    }, [])

    useEffect(() => {
        (async () => {
            const res = await isLoggedIn()
            if (res && !('redirect' in res)) router.push('/dashboard')
        })()
    }, [router])
    
    return (
        <RegularPage id='login-page' transparentHeader={true} footerMarginTop={false}>
            <div id='mid-container'>
                <section>
                    <label>Email</label>
                    <input type='text' value={email} onChange={(e) => setEmail(e.target.value)} disabled={isLoading}/>
                </section>
                <section>
                    <label>Password</label>
                    <input type='password' value={password} onChange={(e) => setPassword(e.target.value)} disabled={isLoading}/>
                </section>
                <p className='error' style={error === null ? { visibility: 'hidden' } : {}}>{error}</p>
                <section id='login-btns'>
                    <button className='cred-submit-btn' onClick={handleLogin} disabled={isLoading}>
                        {isLoading ? 'Logging in...' : 'Log In'}
                    </button>
                    <button className='cred-submit-btn' id='forgot-pass-btn' onClick={() => router.push('/reset-password')}>
                        Forgot Password
                    </button>
                </section>
                <p>Don&apos;t have an account? <Link href={`/signup?plan=${plan}`}>Sign Up</Link></p>
                <ContinueWithGoogle/>
            </div>
        </RegularPage>
    )
}