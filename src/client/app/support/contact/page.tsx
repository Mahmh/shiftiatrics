'use client'
import { useState, FormEvent, ChangeEvent } from 'react'
import { Dropdown, Request } from '@utils'
import RegularPage from '@regpage'

const QUERY_TYPES = [
    'Technical Issue',
    'Bug Report',
    'Feature Suggestion',
    'Feature Feedback',
    'Business Inquiry',
    'Partnership & Collaboration',
    'Billing & Payment Issue',
    'Account Access Issue',
    'Unable to Log In',
    'Integration Request',
    'Customization Inquiry',
    'Data & Privacy Concerns',
    'Job & Career Opportunities',
    'General Inquiry',
    'Other'
] as const

type QueryType = typeof QUERY_TYPES[number]
type SubmissionData = {
    name?: string
    email: string
    queryType: QueryType
    description: string
}

const DEFAULT_QUERY_TYPE: QueryType = 'General Inquiry'
const DEFAULT_SUBMISSION_DATA: SubmissionData = { name: '', email: '', queryType: DEFAULT_QUERY_TYPE, description: '' }

export default function Contact() {
    const [formData, setFormData] = useState<SubmissionData>(DEFAULT_SUBMISSION_DATA)
    const [submitted, setSubmitted] = useState(false)
    const [errMsg, setErrMsg] = useState<string>('')

    const handleChange = (e: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
        setFormData({ ...formData, [e.target.name]: e.target.value })
    }

    const handleDropdownChange = (option: QueryType) => {
        setFormData({ ...formData, queryType: option })
    }

    const handleSubmit = async (e: FormEvent) => {
        e.preventDefault()

        if (!formData.email.trim() || !formData.description.trim()) {
            alert('Please fill out the required fields.')
            return
        }

        await new Request('contact', undefined, setErrMsg, false).post({
            name: formData.name,
            email: formData.email,
            query_type: formData.queryType,
            description: formData.description
        })
        setSubmitted(true)
    }

    return (
        <RegularPage name='Contact Us' id='contact-page'>
            <h1>Contact Us</h1>
            <p>We&apos;re here to help! Reach out for support or inquiries.</p>

            {submitted ? (
                <p className='submit-msg'>
                    {
                        errMsg 
                        ? <>An error occured: {errMsg}<br/>Please try again later.</>
                        : <>Thank you for reaching out!<br/>We&apos;ll reply to you through email soon.</>
                    }
                </p>
            ) : (
                <form onSubmit={handleSubmit}>
                    <section>
                        <input
                            type='text'
                            name='name'
                            placeholder='Your Name (Optional)'
                            className='input'
                            value={formData.name}
                            onChange={handleChange}
                        />
                        <input
                            type='email'
                            name='email'
                            placeholder='Your Email'
                            className='input'
                            required
                            value={formData.email}
                            onChange={handleChange}
                        />
                    </section>
                    <section>
                        <Dropdown
                            label='Query Type'
                            options={QUERY_TYPES}
                            selectedOption={formData.queryType}
                            setSelectedOption={handleDropdownChange as (option: string) => void}
                        />
                        <textarea
                            name='description'
                            placeholder='Describe your issue or message.'
                            rows={4}
                            className='input'
                            required
                            value={formData.description}
                            onChange={handleChange}
                        ></textarea>
                    </section>
                    <button type='submit'>Submit</button>
                </form>
            )}
        </RegularPage>
    )
}