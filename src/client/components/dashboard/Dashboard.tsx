import Sidebar, { MenuButton } from './_Sidebar'
import Content from './_Content'
import Modal from './_Modal'

export default function Dashboard() {
    return (
        <>
            <Sidebar/>
            <Content/>
            <Modal/>
            <MenuButton/>
        </>
    )
}