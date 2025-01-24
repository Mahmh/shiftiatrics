import Head from 'next/head'
import Header from './landing_page/_Header'
import Footer from './landing_page/_Footer'
import type { ReadonlyChildren } from '@types'

export default function RegularPage(
    { children, name='', id='', transparentHeader=false, footerMarginTop=true }: 
    ReadonlyChildren & Readonly<{ name?: string, id?: string, transparentHeader?: boolean, footerMarginTop?: boolean }>
) {
    return <>
        <Head>
            <title>{name ? `${name} | ` : ''}Shiftiatrics</title>
        </Head>
        <Header transparentHeader={transparentHeader}/>
        <main id={id} style={transparentHeader ? {} : { position: 'relative', top: 120, marginBottom: '35vh' }}>
            {children}
        </main>
        <Footer marginTop={footerMarginTop}/>
    </>
}