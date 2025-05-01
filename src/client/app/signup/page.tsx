'use client'
import { useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'
import { Request, sanitizeInput, validateCred, setMetadata, LegalAgreeCheckbox } from '@utils'
import { TOO_MANY_REQS_MSG } from '@const'
import Link from 'next/link'
import RegularPage from '@regpage'

export default function Signup() {
    const router = useRouter()
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [error, setError] = useState<string|null>(null)
    const [loading, setLoading] = useState(false)
    const [legalAgree, setLegalAgree] = useState(false)

    const handleSignup = async () => {
        setError(null)
        setLoading(true)

        const sanitizedEmail = sanitizeInput(email)
        const sanitizedPassword = sanitizeInput(password)
        const validationError = validateCred(sanitizedEmail, sanitizedPassword)
        if (validationError) {
            setError(validationError)
            setLoading(false)
            return
        }

        await new Request(
            'accounts/signup',
            () => {
                setLoading(false)
                router.push('/dashboard')
            },
            (error) => {
                setLoading(false)
                setError(error.includes('429') ? TOO_MANY_REQS_MSG : error)
            }
        ).post({ cred: { email: sanitizedEmail, password: sanitizedPassword }, legal_agree: legalAgree })
    }

    useEffect(() => {
        setMetadata({
            title: 'Sign Up | Shiftiatrics',
            description: 'Create an account to view your dashboard'
        })
    }, [])

    return (
        <RegularPage id='signup-page' transparentHeader={true} footerMarginTop={false}>
            <div id='mid-container'>
                <section>
                    <label>Email</label>
                    <input type='email' value={email} onChange={(e) => setEmail(e.target.value)} disabled={loading} maxLength={32}/>
                </section>
                <section>
                    <label>Password</label>
                    <input type='password' value={password} onChange={(e) => setPassword(e.target.value)} disabled={loading} maxLength={32}/>
                </section>
                <LegalAgreeCheckbox setLegalAgree={setLegalAgree}/>
                <p className='error' style={error === null ? { visibility: 'hidden', margin: 0 } : {}}>{error}</p>
                <button className='cred-submit-btn' id='signup-btn' onClick={handleSignup} disabled={loading}>
                    {loading ? 'Signing up...' : 'Sign Up'}
                </button>
                <p>Already have an account? <Link href={'/login'}>Log In</Link></p>
            </div>
        </RegularPage>
    )
}