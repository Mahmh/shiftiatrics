import type { ReadonlyChildren } from '@types'
import Header from './landing_page/_Header'
import Footer from './landing_page/_Footer'

export default function RegularPage(
    { children, id='', transparentHeader=false }: 
    ReadonlyChildren & { id?: string, transparentHeader?: boolean }
) {
    return <>
        <Header transparentHeader={transparentHeader}/>
        <main id={id} style={transparentHeader ? {} : { position: 'relative', top: 120, marginBottom: '35vh' }}>
            {children}
        </main>
        <Footer/>
    </>
}