import '@styles'
import { useState } from 'react'
import { ChevronDown } from 'lucide-react'
import * as Accordion from "@radix-ui/react-accordion";
import type { FAQ } from '@types'
import RegularPage from '@/components/RegularPage'
import FAQSections from '@/public/faq.json'

const FAQItem = ({ question, answer }: FAQ) => {
    const [isOpen, setIsOpen] = useState(false)

    return (
        <Accordion.Item className='accordion-item' value={question}>
            <Accordion.Header>
                <Accordion.Trigger
                    className='accordion-header'
                    onClick={() => setIsOpen(!isOpen)}
                >
                    {question}
                    <ChevronDown className={`chevron ${isOpen ? 'chevron-rotated' : ""}`} />
                </Accordion.Trigger>
            </Accordion.Header>
            <Accordion.Content className='accordion-content'>
                {answer}
            </Accordion.Content>
        </Accordion.Item>
    )
}


const FAQAccordion = ({ questions }: { questions: FAQ[] }) => {
    return (
        <Accordion.Root type='multiple' className='accordion'>
            {questions.map((faq, idx) => (
                <FAQItem key={idx} question={faq.question} answer={faq.answer}/>
            ))}
        </Accordion.Root>
    )
}


export default function FAQPage() {
    return <RegularPage name='FAQ' id='faq-page'>
        {FAQSections.map(({ category, questions }) => (
            <section key={category} className='faq-section'>
                <h2>{category}</h2>
                <FAQAccordion questions={questions} />
            </section>
        ))}
    </RegularPage>
}