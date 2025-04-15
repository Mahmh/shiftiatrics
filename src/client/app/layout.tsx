import '@styles'
import type { Metadata } from 'next'
import { Suspense } from 'react'
import { DashboardProvider } from '@context'

export const metadata: Metadata = {
    title: 'Shiftiatrics',
    description: 'Auto-scheduling for your business'
}

export default function RootLayout({ children }: Readonly<{children: React.ReactNode}>) {
    return (
        <html lang='en'>
            <body>
                <Suspense fallback={<div>Loading app...</div>}>
                    <DashboardProvider>{children}</DashboardProvider>
                </Suspense>
            </body>
        </html>
    )
}