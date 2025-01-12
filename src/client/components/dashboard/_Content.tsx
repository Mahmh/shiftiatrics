import { ReactNode, useContext } from 'react'
import { dashboardContext } from '@context'
import { ContentName } from '@/app/types'
import Employees from './contents/_Employees'
import Shifts from './contents/_Shifts'
import Schedules from './contents/_Schedules'
import Holidays from './contents/_Holidays'
import Settings from './contents/_Settings'
import Support from './contents/_Support'

export default function Content() {
    const { content, darkThemeClassName } = useContext(dashboardContext)

    const wrapContent = (name: ContentName, contentElement: ReactNode) => (
        <main id={`${name}-content`} className={`content ${darkThemeClassName}`}>{contentElement}</main>
    )

    switch (content) {
        case 'employees': return wrapContent('employees', <Employees/>)
        case 'shifts': return wrapContent('shifts', <Shifts/>)
        case 'schedules': return wrapContent('schedules', <Schedules/>)
        case 'holidays': return wrapContent('holidays', <Holidays/>)
        case 'settings': return wrapContent('settings', <Settings/>)
        case 'support': return wrapContent('support', <Support/>)
        default: return <></>
    }
}