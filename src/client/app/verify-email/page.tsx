'use client'
import { useRouter, useSearchParams } from 'next/navigation'
import { useState, useEffect } from 'react'
import { Request } from '@utils'
import { TOO_MANY_REQS_MSG } from '@const'
import RegularPage from '@regpage'

export default function VerifyEmail() {
    const router = useRouter()
    const params = useSearchParams()
    const [error, setError] = useState<string|null>(null)
    const [loading, setLoading] = useState(false)

    const verifyEmail = async (verifyToken: string) => {
        setLoading(true)
        await new Request(
            'auth/verify_email',
            () => setLoading(false),
            (error) => {
                setLoading(false)
                if (error.includes('429')) { setError(TOO_MANY_REQS_MSG); return }
                setError(error)
            }
        ).patch({ verify_token: verifyToken })
    }

    useEffect(() => {
        const verifyToken = params.get('token')
        if (verifyToken) verifyEmail(verifyToken)
        else router.push('/dashboard')
    }, [params, router])

    return <RegularPage id='verify-email-page' transparentHeader={true} footerMarginTop={false}>
        <div id='mid-container'>
            {
                params.get('token')
                ?
                    loading
                    ? <Actions.Loading/>
                    : error ? <Actions.ErrorOccurred error={error}/> : <Actions.EmailVerified/>
                :
                    <Actions.ErrorOccurred error='No verification token provided.'/>
            }
        </div>
    </RegularPage>
}


class Actions {
    static Loading = () => <>
        <h1>Pending Email Verification</h1>
        <p>Verifying your email...</p>
    </>

    static ErrorOccurred = ({ error }: { error: string }) => {
        const router = useRouter() 
        return <>
            <h1>Error Verifying Email</h1>
            <p>Error message: <span className='error'>{error}</span></p>
            <p>Something wrong happened when we tried to verify your email. If this issue persists, please contact us.</p>
            <button className='cred-submit-btn' style={{ marginTop: 50 }} onClick={() => router.push('/support/contact')}>Contact Us</button>
        </>
    }

    static EmailVerified = () => {
        const router = useRouter()
        const goToDashboard = () => router.push('/dashboard')
        useEffect(goToDashboard, [router])
        return <>
            <h1>Email Verified</h1>
            <p>You successfully verified your email!<br/>Now, you can go back to your dashboard</p>
            <button className='cred-submit-btn' style={{ marginTop: 50 }} onClick={goToDashboard}>Go Back to Dashboard</button>
        </>
    }
}