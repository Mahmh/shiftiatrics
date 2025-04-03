'use client'
import { useState, FormEvent, ChangeEvent, useEffect } from 'react'
import { useSearchParams } from 'next/navigation'
import { PLANS, QUERY_TYPES } from '@const'
import { PlanName, QueryType } from '@types'
import { Dropdown, getUIPlanName, Request, setMetadata } from '@utils'
import RegularPage from '@regpage'

type SubmissionData = { name?: string, email: string, queryType: QueryType, description: string }
const DEFAULT_QUERY_TYPE: QueryType = 'General Inquiry'
const DEFAULT_SUBMISSION_DATA: SubmissionData = { name: '', email: '', queryType: DEFAULT_QUERY_TYPE, description: '' }

export default function Contact() {
    const params = useSearchParams()
    const queryType = params.get('query_type')
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

    useEffect(() => {
        setMetadata({
            title: 'Contact Us | Shiftiatrics',
            description: 'Contact us to seek our help regarding your issues'
        })

        if (queryType === 'partnership') setFormData(prev => ({ ...prev, queryType: 'Partnership & Collaboration' }))
        if (queryType && PLANS.map(p => p.name).includes(queryType.replace('_plan', '') as PlanName)) {
            setFormData(prev => ({ ...prev, queryType: getUIPlanName(queryType as PlanName) as QueryType }))
        }
    }, [params, queryType])

    return (
        <RegularPage id='contact-page'>
            <h1>Contact Us</h1>
            <p>We&apos;re here to help! Reach out for support or inquiries.</p>

            {submitted
            ? (
                <p className='submit-msg'>
                    {
                        errMsg 
                        ? <>An error occured: {errMsg}<br/>Please try again later.</>
                        : <>Thank you for reaching out!<br/>We&apos;ll reply to you through email soon.</>
                    }
                </p>
            )
            : (
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