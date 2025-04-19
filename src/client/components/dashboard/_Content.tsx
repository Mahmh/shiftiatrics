import { ReactNode, useContext } from 'react'
import { dashboardContext } from '@context'
import { ContentName } from '@types'
import Staff from './contents/_Staff'
import Shifts from './contents/_Shifts'
import Schedules from './contents/_Schedules'
import Holidays from './contents/_Holidays'
import Settings from './contents/_Settings'
import Subscription from './contents/_Subscription'
import Sidebar from './_Sidebar'

export default function Content() {
    const { content, darkThemeClassName } = useContext(dashboardContext)

    const wrapContent = (name: ContentName, contentElement: ReactNode) => (
        <main id={`${name}-content`} className={`content ${darkThemeClassName}`}>
            <Sidebar/>
            {contentElement}
        </main>
    )

    switch (content) {
        case 'staff': return wrapContent('staff', <Staff/>)
        case 'shifts': return wrapContent('shifts', <Shifts/>)
        case 'schedules': return wrapContent('schedules', <Schedules/>)
        case 'holidays': return wrapContent('holidays', <Holidays/>)
        case 'settings': return wrapContent('settings', <Settings/>)
        case 'subscription': return wrapContent('subscription', <Subscription/>)
        default: return <></>
    }
}