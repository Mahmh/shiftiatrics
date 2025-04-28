'use client'
import { useContext, useEffect } from 'react'
import { dashboardContext } from '@context'
import type { ReadonlyChildren } from '@types'
import Header from './landing_page/_Header'
import Footer from './landing_page/_Footer'

export default function RegularPage(
    { children, id='', transparentHeader=false, footerMarginTop=true }: 
    ReadonlyChildren & Readonly<{ id?: string, transparentHeader?: boolean, footerMarginTop?: boolean }>
) {
    const { setSettings, darkThemeClassName } = useContext(dashboardContext)

    useEffect(() => {
        document.body.classList.remove('logged-in')
        document.documentElement.classList.remove('logged-in')
        if (darkThemeClassName) document.documentElement.classList.remove(darkThemeClassName)
        setSettings(prev => ({ ...prev, darkThemeEnabled: false }))
    }, [setSettings, darkThemeClassName])

    return <>
        <Header transparentHeader={transparentHeader}/>
        <main id={id} style={transparentHeader ? {} : { position: 'relative', top: 120, marginBottom: '25vh' }}>
            {children}
        </main>
        <Footer marginTop={footerMarginTop}/>
    </>
}