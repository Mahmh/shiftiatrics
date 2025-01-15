import { useEffect, useRef } from 'react'

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


export default function Content() {
    return (
        <section className='lp-content'>
            <Section 
                h='Effortless Shift Scheduling' 
                p='Take the hassle out of managing pediatrician shifts. Our fast, intelligent scheduling system streamlines the process, saving time and reducing stress for everyone involved.' 
            />
            <Section 
                h='Optimize Your Workflow' 
                p='With our advanced algorithms, the scheduler ensures fair distribution of shifts while considering individual work hours, holidays, and workload balance. Say goodbye to manual conflicts and last-minute adjustments.' 
            />
            <Section 
                h='Minimize Burnout' 
                p='Pediatricians work tirelessly to care for young patients. Our system helps avoid burnout by creating balanced schedules, ensuring adequate rest, and allowing more focus on patient care.' 
            />
            <Section 
                h='Seamless Communication' 
                p='Integrated communication features allow instant notifications about schedule changes, shift swaps, and important updates. Keep your team informed and on the same page, effortlessly.' 
            />
            <Section 
                h='Customizable and Scalable' 
                p="Whether you're managing a small clinic or a large pediatric department, our shift scheduler adapts to your needs. Easily customize settings to fit your team's unique requirements."
            />
            <Section 
                h='Accessible Anywhere' 
                p='Access schedules from any device, anywhere, at any time. Our cloud-based solution ensures you’re always connected, enabling easy collaboration and quick adjustments when needed.' 
            />
            <Section 
                h='Save Time, Focus on Care' 
                p='By automating repetitive scheduling tasks, our system frees up valuable administrative time, allowing pediatricians and staff to focus on what truly matters—delivering exceptional care to children.' 
            />
        </section>
    )
}