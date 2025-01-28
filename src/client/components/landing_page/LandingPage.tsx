import Banner from './_Banner'
import Content from './_Content'
import RegularPage from '../RegularPage'

export default function LandingPage() {
    return <>
        <RegularPage transparentHeader={true}>
            <Banner/>
            <Content/>
        </RegularPage>
    </>
}