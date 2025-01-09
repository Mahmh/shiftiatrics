import Image from 'next/image'
import dashboardPreview from '@img/dashboard.png'

export default function Banner() {
    return (
        <section id='lp-banner'>
            <section id='lp-banner-text'>
                <h1>Automated Scheduling for Pediatricians</h1>
                <p>Streamline shift management and ensure efficient care for young patients with our intuitive scheduling solution. We save many hours and headaches by speeding up your scheduling process efficiently and effectively.</p>
                <button>Sign Up Now</button>
            </section>
            <Image src={dashboardPreview} height={500} width={859} alt='Dashboard Preview'/>
        </section>
    )
}