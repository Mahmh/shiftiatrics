'use client'
import { useRouter, useSearchParams } from 'next/navigation'
import { useEffect, useState } from 'react'
import { Request, sanitizeInput, validateCred, setMetadata, pySerializePlan } from '@utils'
import { TOO_MANY_REQS_MSG, PRICING_PLAN_NAMES } from '@const'
import { isLoggedIn, ContinueWithGoogle } from '@auth'
import type { PricingPlanName } from '@types'
import Link from 'next/link'
import RegularPage from '@regpage'

export default function Signup() {
    const router = useRouter()
    const params = useSearchParams()
    const plan = params.get('plan') as PricingPlanName
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [error, setError] = useState<string|null>(null)
    const [isLoading, setIsLoading] = useState(false)
    const [ToSAccepted, setToSAccepted] = useState(false)

    const getSubInfo = () => {
        switch (plan) {
            case 'basic': return pySerializePlan('basic')
            case 'standard': return pySerializePlan('standard')
            case 'premium': return pySerializePlan('premium')
            default: throw new Error(`Unsupported plan: "${plan}"`)
        }
    }

    const handleSignup = async () => {
        if (!ToSAccepted) {
            setError('Before continuing, please accept the terms of service by checking the checkbox above.')
            return
        }

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
            'accounts/signup',
            () => {
                setIsLoading(false)
                router.push('/dashboard')
            },
            (error) => {
                setIsLoading(false)
                setError(error.includes('429') ? TOO_MANY_REQS_MSG : error)
            }
        ).post({
            cred: { email: sanitizedEmail, password: sanitizedPassword },
            sub_info: getSubInfo()
        })
    }

    useEffect(() => {
        setMetadata({
            title: 'Sign Up | Shiftiatrics',
            description: 'Create an account to view your dashboard'
        })

        if (plan === null || plan === 'custom' || !PRICING_PLAN_NAMES.includes(plan)) {
            router.push('/pricing')
        }
    }, [router, plan])

    useEffect(() => {
        (async () => {
            const res = await isLoggedIn()
            if (res && !('redirect' in res)) router.push('/dashboard')
        })()
    }, [router])

    return (
        <RegularPage id='signup-page' transparentHeader={true} footerMarginTop={false}>
            <div id='mid-container'>
                <section>
                    <label>Email</label>
                    <input type='email' value={email} onChange={(e) => setEmail(e.target.value)} disabled={isLoading} maxLength={32}/>
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
                <p>Already have an account? <Link href={`/login?plan=${plan}`}>Log In</Link></p>
                <ContinueWithGoogle plan={plan}/>
            </div>
        </RegularPage>
    )
}