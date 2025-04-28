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
Welcome to **Shiftiatrics** ("we," "our," or "us"). By engaging with our services through our website **${DOMAIN_NAME}** ("Website") or directly with our team, you agree to be bound by these Terms of Service ("Terms"). If you do not agree to these Terms, you must not use our services.

## 2. Description of Service
We provide a **personalized ER shift scheduling service** where we work directly with clients to configure, generate, and deliver optimized schedules for ER staff.  
Our services are provided on a custom basis, tailored to each client's needs, and may be modified as agreed upon during engagement.

## 3. Service Engagement
- Clients engage our services by selecting a plan and contacting us.
- We work with clients to gather required information (e.g., staff names, working hours, holidays).
- Client accounts are created during onboarding, allowing clients to log in and generate schedules. No self-registration is available.
- All schedules are generated based on the information, preferences, and parameters provided by the client. We rely on the accuracy, completeness, and timeliness of the data shared with us. Clients are responsible for ensuring that the data provided is correct, lawful, and suitable for schedule generation. We do not independently verify the validity of the client-provided information.
- Clients will have the opportunity to review the generated schedules and may request reasonable adjustments if needed.

## 4. Data & Privacy
- We handle any personal data (e.g., staff names, work schedules) in accordance with our **[Privacy Policy](/legal/privacy)**.
- We do not sell or misuse client data.
- Clients are responsible for ensuring the accuracy and legality of the information provided to us.

## 5. Client Responsibilities
By using our services, you agree to:
- Provide accurate and up-to-date information necessary for schedule generation.
- Ensure compliance with applicable labor and privacy laws regarding any data shared with us.
- Review delivered schedules carefully before implementing them operationally.
- Use the services only for lawful purposes.
- Not attempt to hack, disrupt, or exploit vulnerabilities in our system.
- Not misuse the service by submitting false, misleading, or inappropriate content.

## 6. Downtime, Delays, and Service Interruptions
- While we strive for high service availability, we do not guarantee uninterrupted access to our website or services.
- Scheduled maintenance, unexpected outages, force majeure events (e.g., natural disasters, power failures), or third-party provider issues may result in temporary unavailability.
- In the event of downtime or delays, we will make reasonable efforts to notify active clients and resume services as quickly as possible.
- We are not liable for any loss or damages resulting from service interruptions, delays in schedule delivery, or other unforeseen operational disruptions.

## 7. Refunds & Cancellations
- Refunds are handled fairly based on the proportion of work completed at the time of cancellation.
- Setup fees for delivered work are non-refundable once major customization begins.
- Clients may cancel future ongoing services with prior written notice.

## 8. Modifications to Service
- We reserve the right to modify service offerings, methods, or features based on evolving client needs or operational improvements.
- Any major changes affecting active clients will be communicated directly.
- Service modifications will not materially reduce the quality of services for active clients without prior notice.

## 9. Termination
- Either party may terminate service engagement with reasonable notice.
- We reserve the right to terminate services immediately if clients violate legal, ethical, security, or professional standards.
- Please note that account deletions are processed manually by our team and may take a few business days to complete.

## 10. Disclaimers & Limitation of Liability
- Our services are provided "as is" without warranties of any kind.
- While we aim for high accuracy, we are **not responsible for missed shifts, financial losses, or operational disruptions** resulting from schedule use.
- Clients are responsible for reviewing and verifying all schedules before distribution or operational use.
- We do not guarantee that schedules will be error-free or meet every operational scenario unless specifically agreed in writing.
- To the fullest extent permitted by law, our liability is limited to the amount paid by the client for the service delivered.

## 11. Dispute Resolution
- Any disputes shall be **resolved through binding arbitration** in **Qatar**.
- If arbitration is unenforceable, disputes will be handled in the courts of **Qatar**.
- Clients waive the right to participate in any class-action lawsuits against Shiftiatrics.

## 12. Changes to These Terms
- We may update these Terms from time to time. Changes will be posted on this page with a revised date.
- Continued engagement with our services after changes constitutes acceptance of the updated Terms.

## 13. Governing Law
These Terms are governed by the laws of **Qatar**. Any disputes will be resolved within this jurisdiction.

## 14. Contact Us
If you have any questions regarding these Terms, please contact us through our [Contact Page](/support/contact).
`

export default function Privacy() {
    return <RegularPage id='terms-of-service'>
        <section>
            <h1>Terms of Service</h1>
            <p>Last updated: April 28, 2025</p>
        </section>
        <ReactMarkdown remarkPlugins={[remarkGfm]}>{MARKDOWN_CONTENT}</ReactMarkdown>
    </RegularPage>
}