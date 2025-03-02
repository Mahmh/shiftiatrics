import Sidebar, { MenuButton } from './_Sidebar'
import Content from './_Content'
import Modal from './_Modal'
import LoadingScreen from '../_LoadingScreen'

export default function DashboardPage() {
    return <>
        <LoadingScreen/>
        <Sidebar/>
        <Content/>
        <Modal/>
        <MenuButton/>
    </>
}