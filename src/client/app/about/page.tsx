import { Metadata } from 'next'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import RegularPage from '@regpage'

export const generateMetadata = async (): Promise<Metadata> => ({
    title: `About | Shiftiatrics`,
    description: `Information about Shiftiatrics`
})

const MARKDOWN_CONTENT = `
## Our Mission
We aim to **streamline the scheduling of ER staff members' shifts and holidays** by providing a fully personalized service. 
Our focus is to allow healthcare professionals to concentrate more on patient care while we handle the complexities of scheduling for them.
In other words, we make the process of converting scheduling rules into automated systems easier and more efficient.

## Key Services
- **Personalized Scheduling Setup** – We build and configure your ER team's shift schedules to match your unique needs.
- **Consideration of Staff Preferences** – We create fair and balanced schedules based on your staff members' working hours, holidays, and preferences.
- **Holiday and Leave Management** – We help you manage absences and holiday schedules without manual work.
- **Flexible Configuration** – Set your shift times, customize ER staff working hours, designate holidays, and adjust settings at any time with our help.
- **Compliance Support** – We ensure generated schedules comply with labor requirements, such as minimum and maximum working hour rules.

## How It Works
1. We work closely with you to collect information about your ER staff, their availability, and work constraints.
2. We configure your shift types, daily patterns, and preferred scheduling rules.
3. You can assign designated holidays at any time before we generate schedules.
4. We generate optimized schedules for your review and approval.
5. Need adjustments? We collaborate with you to fine-tune schedules anytime.
6. Our system delivers finalized schedules, ready for easy distribution to your teams and stakeholders.

## Contact Us
For personalized scheduling services, questions, or support, visit our [Contact Page](/support/contact).

## Legal
- [Terms of Service](/legal/terms)
- [Privacy Policy](/legal/privacy)
- [Cookie Policy](/legal/cookies)
`

export default function About() {
    return (
        <RegularPage id='about-page'>
            <section>
                <h1>About Shiftiatrics</h1>
                <p>
                    Shiftiatrics is a <b>personalized ER staff scheduling service</b> designed to remove the burden of complex shift planning from healthcare teams. 
                    Our mission is to make shift management <b>smarter, simpler, and fully tailored</b> to your department&apos;s needs.
                </p>
            </section>
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {MARKDOWN_CONTENT}
            </ReactMarkdown>
        </RegularPage>
    )
}