import { useRouter } from 'next/navigation'
import { Request } from '@utils'
import type { Account } from '@types'

/** Returns false if the user is not logged in; otherwise, returns their account. */
export const isLoggedIn = async (): Promise<Account | false> => {
    return await new Request(
        'accounts/log_in_account_with_cookies',
        (data) => 'account_id' in data && 'email' in data ? { id: data.account_id, email: data.email } : false,
        () => false
    ).get()
}


/** Lets a user log in or sign up with their Google account. */
export const ContinueWithGoogle = () => {
    const router = useRouter()

    const redirect = async () => {
        await new Request(
            'auth/google',
            (data: { login_url: string }) => router.push(data.login_url)
        ).get()
    }

    return <button id='google-auth-btn' onClick={redirect}>Continue with Google</button>
}