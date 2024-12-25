import Image, { StaticImageData } from 'next/image'
import type { Account } from '@types'

/**
 * Checks if a user is logged in
 * @param account Account set in the context of the app
 * @returns A boolean indicating if a user is logged in
 */
export const isLoggedIn = (account: Account): boolean => {
    return account.username?.length >= 3 && account.password?.length >= 3
}


export const Icon = ({ src, alt, size=20 }: {src: StaticImageData, alt: string, size?: number}) => (
    <Image src={src} width={size} height={size} alt={alt}/>
)