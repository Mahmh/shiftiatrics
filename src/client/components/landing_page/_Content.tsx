import { useEffect, useRef } from 'react'

export default function Content() {
    return (
        <section className='lp-content'>
            <Section 
                h="Effortless Shift Scheduling" 
                p="Take the hassle out of managing ER staff shifts. Our expert-built intelligent scheduling system streamlines the process, saving time and reducing stress for your entire team."
            />
            <Section 
                h="Optimize Your Workflow" 
                p="Using our advanced algorithms and personalized setup, your scheduler ensures fair distribution of shifts while considering your team's work hours, holidays, and workload balance. We tailor the system to your exact needs—no more manual conflicts or last-minute stress."
            />
            <Section 
                h="Minimize Burnout" 
                p="ER staff work tirelessly to care for patients. Our personalized scheduling service helps avoid burnout by designing balanced schedules based on your rules, ensuring proper rest, and empowering better patient care."
            />
            <Section 
                h="Customizable and Scalable" 
                p="Whether you're managing a small clinic or a large ER department, we adapt the scheduling solution to fit your specific requirements. Our team works closely with you to customize settings, shift rules, and schedule formats—making sure it matches your team's unique rhythm."
            />
            <Section 
                h="Accessible Anywhere" 
                p="Access schedules from any device, anywhere, anytime. Our cloud-based solution ensures you're always securely connected, enabling easy collaboration and fast updates whenever needed."
            />
            <Section 
                h="Save Time, Focus on Care" 
                p="By automating repetitive scheduling tasks, and handling setup and updates for you, our service frees up valuable administrative time—allowing ER staff to focus on what truly matters: delivering exceptional patient care."
            />
        </section>
    )
}


const Section = ({ h, p }: { h: string, p: string }) => {
    const sectionRef = useRef<HTMLDivElement>(null)

    useEffect(() => {
        const handleScroll = () => {
            if (sectionRef.current) {
                const rect = sectionRef.current.getBoundingClientRect()
                if (rect.top >= 0 && rect.bottom <= window.innerHeight) sectionRef.current.classList.add('fade-in-out')
            }
        }
        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, [])

    return (
        <section ref={sectionRef}>
            <div style={{ background: '#002958f5', padding: 2, borderRadius: 10 }}></div>
            <div>
                <h1>{h}</h1>
                <p>{p}</p>
            </div>
        </section>
    )
}