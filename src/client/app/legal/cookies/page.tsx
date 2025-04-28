import { Metadata } from 'next'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import RegularPage from '@regpage'
import { DOMAIN_NAME } from '@const'

export const generateMetadata = async (): Promise<Metadata> => ({
    title: `Cookie Policy | Shiftiatrics`,
    description: `Cookie Policy of Shiftiatrics`
})

const MARKDOWN_CONTENT = `
## 1. Introduction
Welcome to **Shiftiatrics** ("we," "our," or "us"). This Cookie Policy explains how and why we use cookies when you visit our website **${DOMAIN_NAME}** ("Website").

We use cookies primarily for authentication and security purposes, ensuring secure login and session maintenance. This policy outlines how we use cookies, what essential third-party services may be involved, and how you can manage your cookie preferences.

## 2. What Are Cookies?
Cookies are small text files stored on your device (computer, smartphone, or tablet) when you visit a website. They help websites recognize users, maintain sessions, and enhance security.

Cookies used by **Shiftiatrics** are strictly necessary for the operation and security of our services.

## 3. How We Use Cookies
We use cookies only for authentication, session management, and security purposes. Specifically, our cookies help to:

- **Verify your identity** when you log in.
- **Maintain your session** while you navigate our client portal.
- **Enhance security** by preventing unauthorized access.

**No Tracking or Analytics** —  
We currently do **not** use cookies for tracking, behavioral advertising, or analytics purposes.

**Essential Third-Party Cookies** —  
In rare cases, essential third-party providers (such as hosting or infrastructure services) may set cookies necessary for basic security, load balancing, or session functionality. These are strictly technical and not used for tracking.

## 4. Types of Cookies We Use
| Cookie Type | Purpose | Expiration |
|-------------|---------|------------|
| **Authentication Cookies** | Used to verify login credentials and maintain secure sessions. | Persist until the user logs out or cookies expire. |

## 5. Managing Cookies
Because our cookies are essential for authentication and access to client services, disabling them may prevent you from logging in or using our services properly.

However, you can manage or delete cookies manually through your browser settings:

- [Manage cookies in Chrome](https://support.google.com/chrome/answer/95647)
- [Manage cookies in Firefox](https://support.mozilla.org/en-US/kb/enable-and-disable-cookies-website-preferences)
- [Manage cookies in Safari](https://support.apple.com/en-us/HT201265)
- [Manage cookies in Microsoft Edge](https://support.microsoft.com/en-us/help/4027947/microsoft-edge-delete-cookies)

## 6. Updates to This Cookie Policy
We may update this Cookie Policy periodically to reflect legal changes or updates to our Website’s functionality.  
The latest version will always be posted here with the **Last Updated** date at the top of the page.

## 7. Contact Us
If you have any questions about this Cookie Policy or our cookie usage practices, please contact us through our [Contact Page](/support/contact).
`

export default function Cookies() {
    return <RegularPage id='cookie-policy'>
        <section>
            <h1>Cookie Policy</h1>
            <p>Last updated: April 28, 2025</p>
        </section>
        <ReactMarkdown remarkPlugins={[remarkGfm]}>{MARKDOWN_CONTENT}</ReactMarkdown>
    </RegularPage>
}