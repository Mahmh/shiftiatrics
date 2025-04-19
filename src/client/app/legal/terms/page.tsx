import { Metadata } from 'next'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import RegularPage from '@regpage'
import { DOMAIN_NAME } from '@const'

export const generateMetadata = async (): Promise<Metadata> => ({
    title: `Terms of Service | Shiftiatrics`,
    description: `Terms of Service of Shiftiatrics`
})

const MARKDOWN_CONTENT = `
## 1. Acceptance of Terms
Welcome to **Shiftiatrics** ("we," "our," or "us"). By accessing or using our website **${DOMAIN_NAME}** ("Website") and services, you agree to be bound by these Terms of Service ("Terms"). If you do not agree with any part of these Terms, you must not use our services.

## 2. Description of Service
We provide an **automated shift scheduling** platform that allows users to manage ER staff member schedules, designated holidays, and user preferences (e.g., dark mode, scheduling settings). Our services are provided "as is" and may be modified or discontinued at any time.

## 3. Account Registration
- To use our services, you must register an account using a valid email address.
- You are responsible for maintaining the confidentiality of your login credentials.
- You must be at least 18 years old or have parental/guardian consent to use our services.
- You agree not to share or transfer your account to others.

## 4. Authentication & Cookies
- We use **authentication cookies** to verify users and allow them access to their accounts.
- These cookies **do not track** users beyond authentication and account-related settings.
- For more details, refer to our **[Privacy Policy](/legal/privacy)**.

## 5. User Responsibilities
By using our services, you agree to:
- Provide accurate and up-to-date information.
- Use the services only for lawful purposes.
- Not attempt to hack, disrupt, or exploit vulnerabilities in our system.
- Not misuse the service by submitting false, misleading, or inappropriate content.
- Ensure that any ER staff member names, minimum and maximum working hours, schedules, or personal data you input comply with applicable labor and privacy laws.

## 6. Data & Privacy
- Your **personal data** (e.g., email, scheduling settings) is handled per our **[Privacy Policy](/legal/privacy)**.
- We **do not sell your data** to third parties.
- You are responsible for ensuring that any ER staff member names or scheduling data you input do not violate privacy laws.

## 7. Modifications & Downtime
- We reserve the right to modify, suspend, or discontinue any part of our services at any time.
- We are **not liable for any data loss or service interruption** due to maintenance, upgrades, or unforeseen circumstances.
- We may update our pricing, features, or functionality with or without notice.

## 8. Termination
- We may suspend or terminate your access if you violate these Terms.
- Users may delete their accounts at any time.
- Termination does not remove the obligation for any outstanding legal or contractual responsibilities.
- We reserve the right to **suspend or permanently remove accounts** that violate laws, security policies, or service integrity.

## 9. Disclaimers & Limitation of Liability
- Our services are provided "as is" without warranties of any kind.
- We are **not responsible for any missed shifts, incorrect schedules, financial loss, damages, or operational disruptions** caused by the use of our service.
- Users are responsible for reviewing and verifying all schedules before implementation.
- We **do not guarantee uninterrupted access to our services**, and we are not liable for disruptions due to system errors, third-party failures, or force majeure events.
- To the fullest extent permitted by law, our liability is **limited to the amount paid by you for the service** (if applicable).

## 10. Arbitration & Dispute Resolution
- Any disputes arising from these Terms shall be **resolved through binding arbitration** in **Qatar**, rather than in court.
- Users waive their right to participate in **class-action lawsuits** against Shiftiatrics.
- If arbitration is deemed unenforceable, disputes shall be handled in the appropriate courts in **Qatar**.

## 11. Changes to These Terms
- We may update these Terms from time to time. Changes will be posted on this page with an updated revision date.
- Continued use of our services after changes means you accept the updated Terms.

## 12. Governing Law
These Terms are governed by the laws of **Qatar**. Any disputes shall be resolved in the appropriate courts within this jurisdiction.

## 13. Contact Us
If you have any questions about these Terms, please visit our [Contact Us](/support/contact) page.

From there, you can submit your inquiry, and our team will respond as soon as possible.
`

export default function Privacy() {
    return <RegularPage id='terms-of-service'>
        <section>
            <h1>Terms of Service</h1>
            <p>Last updated: March 3, 2025</p>
        </section>
        <ReactMarkdown remarkPlugins={[remarkGfm]}>{MARKDOWN_CONTENT}</ReactMarkdown>
    </RegularPage>
}