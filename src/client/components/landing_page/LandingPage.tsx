import LoadingScreen from '../_LoadingScreen'
import Banner from './_Banner'
import Content from './_Content'
import RegularPage from '../RegularPage'

export default function LandingPage() {
    return <>
        <LoadingScreen/>
        <RegularPage transparentHeader={true}>
            <Banner/>
            <Content/>
        </RegularPage>
    </>
}