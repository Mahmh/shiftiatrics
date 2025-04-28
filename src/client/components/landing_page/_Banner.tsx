import Image from 'next/image'
import Link from 'next/link'
import dashboardPreview from '@img/dashboard.png'

export default function Banner() {
    return (
        <section id='lp-banner'>
            <section id='lp-banner-text'>
                <h1>Automate Scheduling of ER Shifts</h1>
                <p>
                    Simplify shift management with our custom-tailored algorithms that auto-generate optimized schedules for ER staff, whether you manage one team or multiple. 
                    Save time and reduce stress by letting automation handle the complexities of scheduling, ensuring efficient care for your patients.
                    <b> Why struggle with manual scheduling when automation does it smarter and faster?</b>
                </p>
                <Link href='/pricing'>Choose your Plan</Link>
            </section>
            <Image src={dashboardPreview} alt='Dashboard Preview' priority={true}/>
        </section>
    )
}