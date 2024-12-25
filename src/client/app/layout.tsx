import type { Metadata } from 'next'
import { AppProvider } from '@context'
import '@/styles/main.css'

export const metadata: Metadata = {
    title: 'AutoShift',
    description: 'Auto-scheduling for your business'
}

export default function RootLayout({ children }: Readonly<{children: React.ReactNode}>) {
    return (
        <html lang='en'>
            <body>
                <AppProvider>{children}</AppProvider>
            </body>
        </html>
    )
}