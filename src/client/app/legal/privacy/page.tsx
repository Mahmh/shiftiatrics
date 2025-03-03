import { Metadata } from 'next'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import RegularPage from '@regpage'
import { DOMAIN_NAME } from '@const'

export const generateMetadata = async (): Promise<Metadata> => ({
    title: `Privacy Policy | Shiftiatrics`,
    description: `Privacy Policy of Shiftiatrics`
})

const MARKDOWN_CONTENT = `
## 1. Introduction
Welcome to **Shiftiatrics** ("we," "our," or "us"). We respect your privacy and are committed to protecting your personal data. This Privacy Policy explains how we collect, use, and protect information when you visit our website **${DOMAIN_NAME}** ("Website").

By using our Website, you agree to the collection and use of information as described in this Privacy Policy.

## 2. Information We Collect
We may collect the following types of information:

### 2.1 Personal Information
- Email address
- Account credentials (hashed passwords, if applicable)
- Any information you provide when contacting us
- Employee names, designated holidays, and other scheduling details inputted by users
- User preferences (e.g., dark theme, scheduling settings) stored within user accounts

## 3. How We Use Your Information
We use your information to:
- Provide and improve our services
- Manage and secure user accounts
- Facilitate shift scheduling and holiday tracking
- Store user preferences (e.g., theme settings, scheduling configurations)
- Respond to inquiries and support requests
- Comply with legal obligations

## 4. Cookies and Tracking Technologies
We use **only essential cookies** for authentication purposes. These cookies allow users to securely log in and access their accounts, which store their preferences (e.g., dark theme, scheduling settings). If you use **Google OAuth** for login, Google may place third-party cookies. For more details, refer to our **[Cookie Policy](/legal/cookies)**.

## 5. How We Share Your Information
We do **not** sell or rent your personal data. However, we may share information with:
- **Service providers** (e.g., hosting providers, security tools) for essential operations
- **Legal authorities** if required by law
- **Third-party authentication providers** (e.g., Google OAuth) for login

## 6. Data Retention
We retain your personal data **only as long as necessary** to fulfill the purposes outlined in this Privacy Policy. Account-related data is kept until the account is deleted. **User-inputted employee names, scheduling details, and preferences may be retained as long as necessary for account functionality, unless deleted by the user.**

## 7. Security Measures
We take appropriate security measures to protect your data, including:
- Secure HTTPS encryption
- Strong authentication measures
- Limited access to sensitive data

However, no method of transmission over the internet is 100% secure, and we cannot guarantee absolute security.

## 8. Your Rights and Choices
Depending on your jurisdiction, you may have the right to:
- Access, update, or delete your personal data
- Restrict or object to data processing
- Withdraw consent where applicable
- Request data portability

To exercise these rights, please visit our [Contact Us](/support/contact) page and submit your request. Our team will review and respond accordingly.

## 9. Third-Party Links
Our Website may contain links to external sites. We are **not responsible** for their privacy practices. Please review their Privacy Policies.

## 10. Changes to This Privacy Policy
We may update this Privacy Policy from time to time. Any changes will be posted on this page with an updated revision date.

## 11. Contact Us
If you have any questions about this Privacy Policy, please visit our [Contact Us](/support/contact) page.

From there, you can submit your inquiry, and our team will respond as soon as possible.
`

export default function Privacy() {
    return <RegularPage id='privacy-policy'>
        <section>
            <h1>Privacy Policy</h1>
            <p>Last updated: March 1, 2025</p>
        </section>
        <ReactMarkdown remarkPlugins={[remarkGfm]}>{MARKDOWN_CONTENT}</ReactMarkdown>
    </RegularPage>
}