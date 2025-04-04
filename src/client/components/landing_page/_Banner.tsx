import Image from 'next/image'
import Link from 'next/link'
import dashboardPreview from '@img/dashboard.png'

export default function Banner() {
    return (
        <section id='lp-banner'>
            <section id='lp-banner-text'>
                <h1>Automated Scheduling for Pediatricians</h1>
                <p>
                    Streamline shift management and ensure efficient care for young patients with our intuitive scheduling solution. 
                    We save you many hours and headaches by speeding up your scheduling process efficiently and effectively.
                    <b> Why schedule manually when automation does it faster and better?</b>
                </p>
                <Link href='/pricing'>Choose your Plan</Link>
            </section>
            <Image src={dashboardPreview} alt='Dashboard Preview' priority={true}/>
        </section>
    )
}