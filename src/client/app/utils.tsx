import Image, { StaticImageData } from 'next/image'
import type { Account } from '@types'

export const Icon = ({ src, alt, size=20 }: {src: StaticImageData, alt: string, size?: number}) => (
    <Image src={src} width={size} height={size} alt={alt}/>
)

export const Choice = ({ onYes, onNo }: { onYes: () => void, onNo: () => void }) => (
    <div style={{ display: 'flex', gap: 10 }}>
        <button style={{ width: '100%' }} onClick={onYes}>Yes</button>
        <button style={{ width: '100%' }} onClick={onNo}>No</button>
    </div>
)


/**
 * Checks if a user is logged in
 * @param account Account set in the context of the app
 * @returns A boolean indicating if a user is logged in
 */
export const isLoggedIn = (account: Account): boolean => {
    return account.username?.length >= 3 && account.password?.length >= 3
}


/**
 * Converts time from 24-hour format to AM/PM format
 * @param time Time in 24-hour format
 * @returns Time in AM/PM format
 */
export const formatTimeToAMPM = (time: string): string => {
    const [hours, minutes] = time.split(':').map(Number)
    const suffix = hours >= 12 ? 'PM' : 'AM'
    const formattedHours = hours % 12 || 12 // Convert 0 -> 12 for midnight
    return `${formattedHours}:${minutes.toString().padStart(2, '0')} ${suffix}`
}


/**
 * Class for making a GET, POST, PATCH, or DELETE request to the API server
 * ### Constructor
 * @param endpoint The API endpoint to send the request
 * @param callbackFunc The callback function to apply to the retrieved JSON response
 * @param data The data payload to send to the API endpoint
 */
export class Request {
    //// Properties ////
    private readonly url: string
    private readonly data: object
    private readonly callbackFunc: (x:any)=>any
    
    constructor(endpoint: string, callbackFunc: (x:any)=>any = x=>x, data: object = {}) {
        this.url = `http://localhost:8000/${endpoint}`
        this.data = data
        this.callbackFunc = callbackFunc
    }
    
    /**
     * Makes `this.data` able to be sent to the API server
     * @param method REST API Method
     * @returns The appropriate payload for the method
     */
    private getPayload(method: string): object {
        return {
            method: method,
            body: JSON.stringify(this.data),
            headers: {'Content-Type': 'application/json'}
        }
    }

    //// Request methods ////
    /**
     * Performs a GET request
     * @returns The output of the inputted callback function
     */
    public async get(): Promise<any> {
        const response = await fetch(this.url)
        const data = await response.json()
        if ('error' in data) console.error(data.error)
        return this.callbackFunc(data)
    }

    /**
     * Performs a POST request
     * @returns The output of the inputted callback function
     */
    public async post(): Promise<any> {
        const response = await fetch(this.url, this.getPayload('POST'))
        const data = await response.json()
        if ('error' in data) console.error(data.error)
        return this.callbackFunc(data)
    }

    /**
     * Performs a PATCH request
     * @returns The output of the inputted callback function
     */
    public async patch(): Promise<any> {
        const response = await fetch(this.url, this.getPayload('PATCH'))
        const data = await response.json()
        if ('error' in data) console.error(data.error)
        return this.callbackFunc(data)
    }

    /**
     * Performs a DELETE request
     * @returns The output of the inputted callback function
     */
    public async delete(): Promise<any> {
        const response = await fetch(this.url, this.getPayload('DELETE'))
        const data = await response.json()
        if ('error' in data) console.error(data.error)
        return this.callbackFunc(data)
    }
}