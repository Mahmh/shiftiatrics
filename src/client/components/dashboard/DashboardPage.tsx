import { useContext, useEffect } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { Request } from '@utils'
import { dashboardContext } from '@context'
import { parseAccount, parseSub } from '@auth'
import type { AccountAndSubResponse } from '@types'
import Sidebar, { MenuButton } from './_Sidebar'
import Content from './_Content'
import Modal from './_Modal'
import LoadingScreen from '../_LoadingScreen'

export default function DashboardPage() {
    const router = useRouter()
    const params = useSearchParams()
    const sessionId = params.get('session_id')
    const { account, setAccount, setSubscription, setModalContent, openModal } = useContext(dashboardContext)

    useEffect(() => {
        const createSub = async () => {
            await new Request(
                `sub/${account.id}/create`,
                (data: AccountAndSubResponse) => {
                    router.push('/dashboard')
                    setAccount(parseAccount(data.account))
                    setSubscription(data.subscription ? parseSub(data.subscription) : null)
                    setModalContent(<p style={{ padding: 20 }}>Your subscription has been successfully activated.</p>)
                    openModal()
                },
                (error) => {
                    if (error.includes('session ID was already processed')) {
                        router.push('/dashboard')
                    } else {
                        setModalContent(<p style={{ padding: 20 }}>Error occurred: {error}</p>)
                        openModal()
                    }
                }
            ).post({ session_id: sessionId })
        }

        if (sessionId) createSub()
    }, [sessionId, router, account.id, setAccount, setSubscription, openModal, setModalContent])

    return <>
        <LoadingScreen/>
        <Sidebar/>
        <Content/>
        <Modal/>
        <MenuButton/>
    </>
}