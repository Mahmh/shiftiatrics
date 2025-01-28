import '@styles'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useContext, useEffect, useState } from 'react'
import { isLoggedIn, Request, sanitizeInput, TOO_MANY_REQS_MSG, validateInput } from '@utils'
import { dashboardContext } from '@context'
import RegularPage from '@regpage'

export default function Signup() {
    const router = useRouter()
    const { setAccount } = useContext(dashboardContext)
    const [username, setUsername] = useState('')
    const [password, setPassword] = useState('')
    const [error, setError] = useState<string|'X'>('X')
    const [isLoading, setIsLoading] = useState(false)

    const handleSignup = async () => {
        setError('X')
        setIsLoading(true)

        const sanitizedUsername = sanitizeInput(username)
        const sanitizedPassword = sanitizeInput(password)
        const validationError = validateInput(sanitizedUsername, sanitizedPassword)
        if (validationError) {
            setError(validationError)
            setIsLoading(false)
            return
        }

        await new Request(
            'accounts/signup',
            (data: { account_id: number, username: string, password: string }) => {
                setIsLoading(false)
                setAccount({ id: data.account_id, username: data.username })
                router.push('/')
            },
            (error) => {
                setIsLoading(false)
                setError(error.includes('429') ? TOO_MANY_REQS_MSG : error)
            }
        ).post({ username: sanitizedUsername, password: sanitizedPassword })
    }

    useEffect(() => {
        (async () => {
            if (await isLoggedIn()) router.push('/')
        })()
    }, [router])

    return (
        <RegularPage name='Sign Up' id='signup-page' transparentHeader={true} footerMarginTop={false}>
            <div id='mid-container'>
                <section>
                    <label>Username</label>
                    <input type='text' value={username} onChange={(e) => setUsername(e.target.value)} disabled={isLoading} maxLength={48}/>
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
            </div>
        </RegularPage>
    )
}