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
Welcome to **Shiftiatrics** ("we," "our," or "us"). We respect your privacy and are committed to protecting your personal data. This Privacy Policy explains how we collect, use, and protect information when you engage with our services or visit our website **${DOMAIN_NAME}** ("Website").

By engaging with our services or using our Website, you agree to the collection and use of information as described in this Privacy Policy.

## 2. Information We Collect
We may collect the following types of information:

### 2.1 Personal Information
- Contact details (e.g., email address, organization name, point of contact)
- Account login credentials (email and hashed passwords)
- Any communication records related to service requests, setup, or support
- Information provided during service setup, including:
  - ER staff names
  - Staff team assignments
  - Working hours, shift configurations, and holiday designations

### 2.2 Information Collected Through Support Requests
When you submit a query through our [Contact Us](/support/contact) page, through the dashboard page, or by email, we may collect:
- Your name (if provided)
- Your email address
- Your account ID (linked to your client profile)
- The type of inquiry (e.g., billing, technical support)
- The description or content of your message

We collect this information directly from you during onboarding and while providing ongoing services.

## 3. How We Use Your Information
We use your information to:
- Provide, configure, and personalize our scheduling services
- Enable client logins and allow schedule generation through the portal
- Communicate with you regarding service updates, support, or improvements
- Send important account-related communications, such as email verification and password reset instructions
- Respond to inquiries and manage service requests
- Comply with legal obligations

## 4. Cookies and Tracking Technologies
We use **essential cookies** for authentication and secure access to client accounts.  
These cookies:
- Maintain session security
- Remember login states

We do **not** use tracking cookies or behavioral advertising cookies.  
For more details, see our **[Cookie Policy](/legal/cookies)**.

## 5. How We Share Your Information
We do **not** sell, rent, or trade your personal information. However, we may share information with:
- **Service providers** (e.g., hosting providers, IT security) for essential operational purposes
- **Legal authorities** if required by law, subpoena, or to protect our legal rights

## 6. Data Retention
We retain your personal data **only as long as necessary** to provide services and fulfill legal or contractual obligations.  
Client scheduling data (e.g., staff names, shift rules) is retained for active service delivery and securely deleted or anonymized when no longer needed.

## 7. Security Measures
We implement appropriate security measures to protect your personal data, including:
- HTTPS encryption
- Secure password storage (hashed passwords)
- Access controls and data minimization practices

However, no system can guarantee absolute security. We encourage you to use strong passwords and secure your access credentials.

## 8. Your Rights and Choices
Depending on your jurisdiction, you may have the right to:
- Access, update, or delete your personal data
- Restrict or object to data processing
- Withdraw consent where applicable
- Request a copy of your data in a portable format

To exercise your rights, please contact us through our [Contact Us](/support/contact) page.

### 8.1 Account Deletion Requests
When you request to delete your account through our Website or dashboard, the request is sent to our support team for processing.  
Account deletion is **not immediate**; it is manually reviewed and actioned by our team to ensure account ownership and complete data removal.

We will process deletion requests as soon as reasonably possible, typically within 7 business days after receiving your request.  
You will receive a confirmation once the deletion is complete.

If you wish to follow up on a pending deletion request, please contact us through our [Contact Us](/support/contact) page.

## 9. Third-Party Links
Our Website may contain links to external websites. We are **not responsible** for their privacy practices.  
We encourage you to review the privacy policies of any third-party sites you visit.

## 10. Changes to This Privacy Policy
We may update this Privacy Policy from time to time. Changes will be posted on this page with an updated revision date.  
Continued use of our services after changes constitutes acceptance of the revised Privacy Policy.

## 11. Contact Us
If you have any questions about this Privacy Policy or our data handling practices, please contact us through our [Contact Us](/support/contact) page.
`

export default function Privacy() {
    return <RegularPage id='privacy-policy'>
        <section>
            <h1>Privacy Policy</h1>
            <p>Last updated: April 28, 2025</p>
        </section>
        <ReactMarkdown remarkPlugins={[remarkGfm]}>{MARKDOWN_CONTENT}</ReactMarkdown>
    </RegularPage>
}