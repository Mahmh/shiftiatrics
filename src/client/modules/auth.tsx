import { useRouter } from 'next/navigation'
import { Request } from '@utils'
import type { AccountResponse, Account } from '@types'

/** Converts API response properties to TSX properties */
export const parseAccount = (data: AccountResponse): Account => ({
    id: data.account_id,
    email: data.email,
    emailVerified: data.email_verified,
    isOAuthOnly: data.hashed_password === null && data.oauth_provider !== null
})


/** Returns false if the user is not logged in; otherwise, returns their account. */
export const isLoggedIn = async (): Promise<Account | false> => {
    return await new Request(
        'auth/log_in_account_with_cookies',
        (data: AccountResponse) => parseAccount(data),
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