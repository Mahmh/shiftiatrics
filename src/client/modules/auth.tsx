import { Request } from '@utils'
import type { AccountResponse, Account, AccountAndSubResponse, AccountAndSub, SubscriptionResponse, Subscription, SettingsResponse, Settings } from '@types'

/** Converts API response properties to TSX properties */
export const parseAccount = (data: AccountResponse): Account => ({
    id: data.account_id,
    email: data.email,
    emailVerified: data.email_verified,
    passwordChanged: data.password_changed,
    subExpired: data.sub_expired
})

export const parseSub = (data: SubscriptionResponse): Subscription => ({
    id: data.subscription_id,
    plan: data.plan,
    createdAt: data.created_at,
    expiresAt: data.expires_at,
})

export const parseSettings = (data: SettingsResponse): Settings => ({
    darkThemeEnabled: data.dark_theme_enabled,
    weekendDays: data.weekend_days
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