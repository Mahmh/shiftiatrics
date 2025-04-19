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
We aim to **streamline scheduling of ER staff members' shifts and holidays**, allowing healthcare professionals to focus more on patient care rather than administrative tasks.

## Key Features
- **Automated Scheduling** – Reduce manual work and auto-generate shifts.
- **ER Staff Members' Preferences** – Ensure fair scheduling with customization.
- **Holidays & Leaves** – Account for absences effortlessly.
- **Flexibility** – Set when shifts start and end, register ER staff members and their working hours, optionally designate holidays to ER staff members, and regenerate schedules when needed.
- **Compliance** – Manage the generation of schedules to comply with labor laws, such as setting minimum and maximum working hours for ER staff members.

## How It Works
1. Add ER staff members and their availability.
2. Set the shifts per day, including their starting and ending time.
3. Set designated holidays and scheduling preferences.
4. Let Shiftiatrics generate an optimized schedule.
5. Review, adjust, and regenerate if needed. Shiftiatrics allows you to see the number of shifts and working hours per ER staff member in the generated schedule.
6. Export the schedule and share with stakeholders.

## Contact Us
For inquiries or support, visit our [Contact Page](/support/contact).

## Legal
- [Terms of Service](/legal/terms)
- [Privacy Policy](/legal/privacy)
- [Cookie Policy](/legal/cookies)
`

export default function About() {
    return <RegularPage id='about-page'>
        <section>
            <h1>About Shiftiatrics</h1>
            <p>
                Shiftiatrics is an <b>automated shift scheduling platform</b> designed for ER staff members.
                Our goal is to make shift management <b>faster, smarter, and more efficient</b>.
            </p>
        </section>
        <ReactMarkdown remarkPlugins={[remarkGfm]}>{MARKDOWN_CONTENT}</ReactMarkdown>
    </RegularPage>
}