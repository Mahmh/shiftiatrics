import ExcelJS from 'exceljs'
import Image, { StaticImageData } from 'next/image'
import type { Account, MonthName, Schedule, YearToSchedules, Employee, Shift, SupportedExportFormat } from '@types'

/** Component for icons */
export const Icon = ({ src, alt, size=20 }: {src: StaticImageData, alt: string, size?: number}) => (
    <Image src={src} width={size} height={size} alt={alt}/>
)


/** Component for Yes and No buttons in the modal */
export const Choice = ({ onYes, onNo }: { onYes: () => void, onNo: () => void }) => (
    <section style={{ display: 'flex', gap: 10 }}>
        <button style={{ width: '100%' }} onClick={onYes}>Yes</button>
        <button style={{ width: '100%' }} onClick={onNo}>No</button>
    </section>
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


/** @returns The number of days in the current month */
export const getDaysInCurrentMonth = (): number => {
    const now = new Date()
    const year = now.getFullYear()
    const month = now.getMonth()
    // Create a date for the first day of the next month, then go one day back
    const lastDayOfMonth = new Date(year, month + 1, 0)
    return lastDayOfMonth.getDate()
}


/** @returns The number of days in a month given its index (0-11) */
export const getDaysInMonth = (i: number, year: number): number | null => {
    if (i < 0 || i > 11) throw new Error('Invalid month index. Must be between 0 and 11.')
    return new Date(year, i+1, 0).getDate()
}


/** @returns The name of the month given its index (0-11) */
export const getMonthName = (i: number): MonthName => {
    if (i < 0 || i > 11) throw new Error('Invalid month index. Must be between 0 and 11.')
    const monthNames: MonthName[] = [
        'January', 'February', 'March', 'April', 'May', 'June', 
        'July', 'August', 'September', 'October', 'November', 'December'
    ]
    return monthNames[i]
}


/** @returns The employee given its ID */
export const getEmployeeById = (id: number, employees: Employee[]): Employee | undefined => (
    employees.find(emp => emp.id === id)
)


/** @returns True if the schedule for a specific year & month was already generated  */
export const hasScheduleForMonth = (schedules: YearToSchedules, year: number, month: number): boolean => (
    (schedules.get(year)?.[month]?.schedule.length ?? 0) > 0
)


/**
 * Class for making a GET, POST, PATCH, or DELETE request to the API server
 * ### Constructor
 * @param endpoint The API endpoint to send the request
 * @param callbackFunc The callback function to apply to the retrieved JSON response
 * @param data The data payload to send to the API endpoint
 *
 */
/* eslint-disable @typescript-eslint/no-explicit-any */
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
            headers: { 'Content-Type': 'application/json' }
        }
    }

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
/* eslint-enable @typescript-eslint/no-explicit-any */


/** Collection of functions that export a given schedule in supported formats */
export class ScheduleExporter {
    private readonly scheduleToExport: Employee[][]
    private readonly shifts: Shift[]

    constructor(scheduleToExport: Schedule, shifts: Shift[]) {
        this.scheduleToExport = scheduleToExport.schedule
        this.shifts = shifts
    }

    /** Exports the given schedule in JSON format */
    public exportJSON(): void {
        let fileContent = 'data:application/json;charset=utf-8,' 
        fileContent += encodeURIComponent(JSON.stringify(this.scheduleToExport, null, 2))

        const link = document.createElement('a')
        link.setAttribute('href', fileContent)
        link.setAttribute('download', `schedule.json`)
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
    }

    /** Exports the given schedule as an Excel spreadsheet */
    public async exportExcel(): Promise<void> {
        const workbook = new ExcelJS.Workbook()
        const worksheet = workbook.addWorksheet(`Schedule`)

        // Add column headers
        worksheet.columns = [
            { header: 'Day', key: 'day', width: 10 },
            { header: 'Shift', key: 'shift', width: 15 },
            { header: 'Employee', key: 'employee', width: 25 }
        ]

        // Add rows
        this.scheduleToExport.forEach((day, dayI) => {
            day.forEach((employee, shiftI) => {
                worksheet.addRow({
                    day: dayI + 1,
                    shift: this.shifts[shiftI].name,
                    employee: employee.name,
                })
            })
        })

        // Apply styling & write the workbook to a file
        worksheet.getRow(1).font = { bold: true }
        const buffer = await workbook.xlsx.writeBuffer()
        // Create a blob and trigger download
        const blob = new Blob([buffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
        const link = document.createElement('a')
        link.href = URL.createObjectURL(blob)
        link.download = 'schedule.xlsx'
        link.click()
    }

    /** Exports the given schedule as a downloadable CSV file */
    public exportCSV(): void { this.exportDelimited(',', 'csv') }

    /** Exports the given schedule as a downloadable TSV file */
    public exportTSV(): void { this.exportDelimited('\t', 'tsv') }

    /**
     * Generic function to export the given schedule in a delimited format
     * @param schedules - Array of schedules
     * @param selectedMonth - The selected month index
     * @param delimiter - The delimiter for the format (e.g., ',' for CSV, '\t' for TSV)
     * @param extension - The file extension (e.g., 'csv', 'tsv')
     */
    private exportDelimited(delimiter: string, extension: SupportedExportFormat): void {
        const columnHeaders = ['Day', 'Shift', 'Employee']
        let fileContent = 'data:text/plain;charset=utf-8,'
        // Adds the column headers as the first row
        fileContent += [
            columnHeaders.join(delimiter), ...this.scheduleToExport.map((day, dayI) =>
                day.map((employee, shiftI) => `${dayI + 1}${delimiter}${this.shifts[shiftI].name}${delimiter}${employee.name}`).join('\n')
            )
        ].join('\n')
        const encodedUri = encodeURI(fileContent)

        const link = document.createElement('a')
        link.setAttribute('href', encodedUri)
        link.setAttribute('download', `schedule.${extension}`)
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
    }
}