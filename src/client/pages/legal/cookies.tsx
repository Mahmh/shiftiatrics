import '@styles'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import RegularPage from '@regpage'

const MARKDOWN_CONTENT = `
## 1. Introduction
Welcome to **Shiftiatrics** ("we," "our," or "us"). This Cookie Policy explains how and why we use cookies when you visit our website **shiftiatrics.com** ("Website").

We use cookies primarily for authentication purposes, ensuring secure login and session maintenance. Additionally, if you choose to sign in using **"Continue with Google"**, third-party cookies from Google may be used for authentication. This policy outlines how we use cookies, what third-party services may be involved, and how you can manage your cookie preferences.

## 2. What Are Cookies?
Cookies are small text files stored on your device (computer, smartphone, or tablet) when you visit a website. They help websites recognize users, maintain sessions, and enhance security.

Cookies used by **Shiftiatrics** are strictly necessary for authentication and security.

## 3. How We Use Cookies
We use cookies only for authentication and security purposes. Specifically, our cookies help to:

- **Verify your identity** when you log in.
- **Maintain your session** while navigating our website.
- **Enhance security** by preventing unauthorized access.
- **Enable third-party authentication** (if signing in with Google OAuth).

**No Tracking** – Currently, we do **not** use cookies for tracking, analytics, advertising, or marketing.  
**No Unnecessary Third-Party Cookies** – The only third-party cookies involved are from Google if you use **"Continue with Google."**

## 4. Types of Cookies We Use
| Cookie Type | Purpose | Expiration |
|------------|---------|------------|
| **Authentication Cookies** | Used to verify login credentials and maintain user sessions. | Persist until the user logs out or they reach their expiration date. |
| **Third-Party Cookies (Google OAuth)** | Set by Google to manage authentication and maintain login sessions. | Controlled by Google ([Google’s Privacy Policy](https://policies.google.com/privacy)). |

## 5. Third-Party Cookies (Google Sign-In)
If you use **"Continue with Google"**, Google may place cookies on your device to:

- Verify your identity.
- Maintain session security.
- Enable seamless login across websites that use Google authentication.

We **do not control** these cookies. For more details, review **[Google’s Privacy Policy](https://policies.google.com/privacy)** and their **[Cookie Policy](https://policies.google.com/technologies/cookies)**.

## 6. Managing Cookies
Since our cookies are essential for authentication, **disabling them may prevent you from logging in or using our website properly.**  

However, you can manage or delete cookies through your browser settings:

- **Google Chrome:** [Instructions](https://support.google.com/chrome/answer/95647)
- **Mozilla Firefox:** [Instructions](https://support.mozilla.org/en-US/kb/enable-and-disable-cookies-website-preferences)
- **Safari:** [Instructions](https://support.apple.com/en-us/HT201265)
- **Microsoft Edge:** [Instructions](https://support.microsoft.com/en-us/help/4027947/microsoft-edge-delete-cookies)

**Note:** Blocking third-party cookies may prevent Google OAuth from working correctly.

## 7. Updates to This Cookie Policy
We may update this Cookie Policy from time to time to reflect changes in legal requirements or our website’s functionality. The latest version will always be available on this page, with the **last updated** date at the top.

## 8. Contact Us
If you have any questions about this Cookie Policy or how we use cookies, please contact us at:

**Email:** [COMPANY_EMAIL]
`

export default function Cookies() {
    return <RegularPage name='Cookie Policy' id='cookie-policy'>
        <section>
            <h1>Cookie Policy</h1>
            <p>Last updated: March 1, 2025</p>
        </section>
        <ReactMarkdown remarkPlugins={[remarkGfm]}>{MARKDOWN_CONTENT}</ReactMarkdown>
    </RegularPage>
}