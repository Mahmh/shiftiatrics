import { useRouter } from 'next/navigation'
import { Request } from '@utils'
import type { AccountResponse, Account, AccountAndSubResponse, AccountAndSub, SubscriptionResponse, Subscription } from '@types'

/** Converts API response properties to TSX properties */
export const parseAccount = (data: AccountResponse): Account => ({
    id: data.account_id,
    email: data.email,
    emailVerified: data.email_verified,
    isOAuthOnly: data.hashed_password === null && data.oauth_provider !== null,
    hasUsedTrial: data.has_used_trial,
    subExpired: data.sub_expired,
    pendingCheckoutUrl: data.pending_checkout_url
})

export const parseSub = (data: SubscriptionResponse): Subscription => ({
    id: data.subscription_id,
    plan: data.plan,
    price: typeof data.price === 'string' ? parseFloat(data.price) : data.price,
    createdAt: data.created_at,
    expiresAt: data.expires_at,
    planDetails: {
        maxNumPediatricians: data.plan_details.max_num_pediatricians,
        maxNumShiftsPerDay: data.plan_details.max_num_shifts_per_day,
        maxNumScheduleRequests: data.plan_details.max_num_schedule_requests
    }
})


/** Returns false if the user is not logged in; otherwise, returns their account & subscription */
export const isLoggedIn = async (): Promise<AccountAndSub | false> => {
    return await new Request(
        'auth/log_in_account_with_cookies',
        (data: AccountAndSubResponse) => ({
            account: parseAccount(data.account),
            subscription: data.subscription ? parseSub(data.subscription) : null
        }),
        () => false
    ).get()
}


/** Lets a user log in or sign up with their Google account */
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