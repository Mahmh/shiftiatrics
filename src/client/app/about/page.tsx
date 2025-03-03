import { Metadata } from 'next'
import RegularPage from '@regpage'

export const generateMetadata = async (): Promise<Metadata> => ({
    title: `About | Shiftiatrics`,
    description: `Information about Shiftiatrics`
})

export default function About() {
    return <RegularPage name='About'>
        <></>
    </RegularPage>
}