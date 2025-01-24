import type { Metadata } from 'next'
import { DashboardProvider } from '@context'
import '@/styles/main.css'

export const metadata: Metadata = {
    title: 'Shiftiatrics',
    description: 'Auto-scheduling for your business'
}

export default function RootLayout({ children }: Readonly<{children: React.ReactNode}>) {
    return (
        <html lang='en'>
            <body>
                <DashboardProvider>{children}</DashboardProvider>
            </body>
        </html>
    )
}