import '@styles'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useContext, useEffect, useState } from 'react'
import { isLoggedIn, Request, sanitizeInput, TOO_MANY_REQS_MSG, validateInput } from '@utils'
import { dashboardContext } from '@context'
import RegularPage from '@regpage'

export default function Login() {
    const router = useRouter()
    const { setAccount } = useContext(dashboardContext)
    const [username, setUsername] = useState('')
    const [password, setPassword] = useState('')
    const [error, setError] = useState<string|'X'>('X')
    const [isLoading, setIsLoading] = useState(false)

    const handleLogin = async () => {
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
            'accounts/login',
            (data: { account_id: number, username: string, password: string }) => {
                setIsLoading(false)
                setAccount({ id: data.account_id, username: data.username })
                router.push('/')
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
        ).post({ username: sanitizedUsername, password: sanitizedPassword })
    }

    useEffect(() => {
        (async () => {
            if (await isLoggedIn()) router.push('/')
        })()
    }, [router])
    
    return (
        <RegularPage name='Log In' id='login-page' transparentHeader={true} footerMarginTop={false}>
            <div id='mid-container'>
                <section>
                    <label>Username</label>
                    <input type='text' value={username} onChange={(e) => setUsername(e.target.value)} disabled={isLoading}/>
                </section>
                <section>
                    <label>Password</label>
                    <input type='password' value={password} onChange={(e) => setPassword(e.target.value)} disabled={isLoading}/>
                </section>
                {error && <p className='error' style={error === 'X' ? { visibility: 'hidden' } : {}}>{error}</p>}
                <button className='cred-submit-btn' onClick={handleLogin} disabled={isLoading}>
                    {isLoading ? 'Logging in...' : 'Log In'}
                </button>
                <p>Don&apos;t have an account? <Link href='/signup'>Sign Up</Link></p>
            </div>
        </RegularPage>
    )
}