'use client'
import { useState, useContext, FormEvent, ReactNode } from 'react'
import Image, { StaticImageData } from 'next/image'
import Link from 'next/link'
import ExcelJS from 'exceljs'
import * as DropdownMenu from '@radix-ui/react-dropdown-menu'
import { ChevronDown } from 'lucide-react'
import { dashboardContext } from '@context'
import { MONTH_NAMES, QUERY_TYPES, TOO_MANY_REQS_MSG, WEEKDAY_NAMES } from '@const'
import { parseAccount, parseSub } from '@types'
import type {
    MonthName, YearToSchedules, Employee, Shift, Schedule,
    SupportedExportFormat, WeekendDays, EndpointResponse, PlanName,
    InputEvent, QueryType, AccountResponse, Account, AccountAndSub,
    AccountAndSubResponse
} from '@types'
import routeIcon from '@icons/route.png'


/** Component for icons */
export const Icon = ({ src, alt, size=20 }: {src: StaticImageData, alt: string, size?: number}) => (
    <Image src={src} width={size} height={size} alt={alt}/>
)


/** Component for including Yes & No buttons in the modal */
export const Choice = ({ onYes, onNo }: { onYes: () => void, onNo: () => void }) => (
    <section style={{ display: 'flex', gap: 10 }}>
        <button style={{ width: '100%' }} onClick={onYes}>Yes</button>
        <button style={{ width: '100%' }} onClick={onNo}>No</button>
    </section>
)


/** Component for toggling switches in settings */
export const Switch = ({ label, handleClick, enabled }: { label: string, handleClick: () => void, enabled: boolean }) => (
    <div className='switch-div' onClick={handleClick}>
        <label>{label}</label>
        <button className={enabled ? 'switch-btn-enabled' : ''}>
            <div className='switch-circle'></div>
        </button>
    </div>
)


/** Component for incrementing/decrementing a value using only arrow buttons */
export const NumInput = ({ label, initialValue, min=1, max, onChange }: { label: string, initialValue: number, min?: number, max: number, onChange: (value: number) => Promise<void> }) => {
    const [count, setCount] = useState(initialValue)

    const decrement = async () => {
        setCount(c => c-1)
        await onChange(count-1)
    }
    
    const increment = async () => {
        setCount(c => c+1)
        await onChange(count+1)
    }

    return (
        <div className='num-input-div'>
            <label>{label}</label>
            <div>
                <button onClick={decrement} disabled={count <= min} className={count <= min ? 'disabled-num-input-btn' : ''}>-</button>
                <span>{count}</span>
                <button onClick={increment} disabled={count >= max} className={count >= max ? 'disabled-num-input-btn' : ''}>+</button>
            </div>
        </div>
    )
}


/** Component for selecting an option from a dropdown list */
export const Dropdown = (
    { label, options, selectedOption, setSelectedOption }:
    { label?: string, options: readonly string[], selectedOption: string, setSelectedOption: (option: string) => void }
) => {
    const { settings } = useContext(dashboardContext)
    const [open, setOpen] = useState(false)

    return (
        <div className='dropdown'>
            {label && <label>{label}: </label>}
            <DropdownMenu.Root open={open} onOpenChange={setOpen}>
                <DropdownMenu.Trigger className='dropdown-trigger'>
                    {selectedOption || 'Select an option'}
                    <ChevronDown
                        className={`chevron ${open ? 'chevron-rotated' : ''}`}
                        size={18}
                        color={settings.darkThemeEnabled ? 'white' : undefined}
                    />
                </DropdownMenu.Trigger>

                <DropdownMenu.Portal>
                    <DropdownMenu.Content 
                        className='dropdown-menu'
                        align='start'
                        side='bottom'
                        sideOffset={4}
                        style={{ overflowY: options.length > 3 ? 'scroll' : undefined }}
                    >
                        {options.map(option => (
                            <DropdownMenu.Item
                                key={option}
                                className='dropdown-item'
                                onSelect={() => { setSelectedOption(option); setOpen(false) }}
                            >
                                {option}
                            </DropdownMenu.Item>
                        ))}
                    </DropdownMenu.Content>
                </DropdownMenu.Portal>
            </DropdownMenu.Root>
        </div>
    )
}


/** Component for selecting a route in the UI */
export const RouteCard = ({ href, h, p }: { href: string, h: string, p: string }) => (
    <Link href={href} className='route-card'>
        <section className='rc-text-sec'>
            <h1>{h}</h1>
            <p>{p}</p>
        </section>
        <section className='rc-img-sec'>
            <Icon src={routeIcon} alt='Go To' size={35}/>
        </section>
    </Link>
)


/** Function for setting metadata in client components */
export const setMetadata = ({ title, description }: { title: string, description: string }) => {
    document.title = title

    // Update the meta description
    const metaDescription = document.querySelector('meta[name="description"]')
    if (metaDescription) {
        metaDescription.setAttribute('content', description)
    } else {
        // If no meta tag exists, create one
        const newMeta = document.createElement('meta')
        newMeta.name = 'description'
        newMeta.content = description
        document.head.appendChild(newMeta)
    }
}


/** @returns false if the user is not logged in; otherwise, returns their account & subscription */
export const isLoggedIn = async (): Promise<AccountAndSub | false> => {
    return await new Request(
        'auth/log_in_account_with_cookies',
        (data: AccountAndSubResponse) => ({
            account: parseAccount(data.account),
            subscription: data.subscription ? parseSub(data.subscription) : null
        }),
        () => false
    ).get()
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


/** @returns The number of days in a month given its index (0-11) & year */
export const getDaysInMonth = (i: number, year: number): number => {
    if (i < 0 || i > 11) throw new Error('Invalid month index. Must be between 0 and 11.')
    return new Date(year, i+1, 0).getDate()
}


/** @returns The name of the month given its index (0-11) */
export const getMonthName = (i: number): MonthName => {
    if (i < 0 || i > 11) throw new Error('Invalid month index. Must be between 0 and 11.')
    return MONTH_NAMES[i]
}


/** @returns The name of the weekday given the year, month (0-11), and its index (1-31) in the month */
export const getWeekdayName = (year: number, month: number, day: number): string => {
    const date = new Date(year, month, day)
    return WEEKDAY_NAMES[date.getDay()]
}


/** @returns The employee given its ID */
export const getEmployeeById = (id: number, employees: Employee[]): Employee | undefined => (
    employees.find(emp => emp.id === id)
)


/** @returns True if any team has a schedule for the specific year & month */
export const hasScheduleForMonth = (schedules: YearToSchedules, year: number, month: number): boolean => {
    const yearMap = schedules.get(year)
    if (!yearMap) return false

    for (const teamSchedules of yearMap.values()) {
        const schedule = teamSchedules?.[month]
        if (schedule && schedule.schedule.length > 0) {
            return true
        }
    }

    return false
}


/** Sanitizes input credentials to prevent XSS and SQL injection */
export const sanitizeInput = (input: string): string => {
    const sanitized = input.replace(/[^\w\s@.-]/gi, '').trim(); // Allow only alphanumeric characters, spaces, @, ., and -
    return sanitized.replace(/['"]/g, ''); // Remove single and double quotes
}


/** Validates input credentials */
export const validateCred = (email: string, password: string): string | null => {
    const emailError = validateEmail(email)
    const passwordError = validatePassword(password)
    if (emailError) return emailError
    if (passwordError) return passwordError
    return null 
}

/** Validates email input */
export const validateEmail = (email: string): string | null => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(email)) return 'Invalid email format.'
    return null
}

/** Validates password input */
export const validatePassword = (password: string): string | null => {
    if (password.length < 8) return 'Password must be at least 8 characters long.'
    return null
}


/** E.g., 'basic' -> 'Basic Plan'  */
export const getUIPlanName = (name: PlanName) => (
    `${name.charAt(0).toUpperCase() + name.slice(1)} Plan`
)


/** Converts a UTC date object into a user-readable date */
export const getUIDate = (date: Date) => (
    `${getMonthName(date.getUTCMonth())} ${date.getUTCDate()}, ${date.getUTCFullYear()}`
)


/** Used during sign up or account setup */
export const LegalAgreeCheckbox = ({ setLegalAgree }: { setLegalAgree: (value: boolean) => void }) => (
    <section id='agree-to-tos-sec'>
        <input type='checkbox' onChange={e => setLegalAgree(e.target.checked)} required/>
        <label>
            I agree to Shiftiatrics&apos;
            <span> </span>
            <Link href='/legal/terms' target='_blank' rel='noopener noreferrer'>Terms of Service</Link>,
            <span> </span>
            <Link href='/legal/privacy' target='_blank' rel='noopener noreferrer'>Privacy Policy</Link>, and
            <span> </span>
            <Link href='/legal/cookies' target='_blank' rel='noopener noreferrer'>Cookie Policy</Link>.
        </label>
    </section>
)


/** Modal content for changing an account's password */
export const ChangePasswordModalContent = (
    { requireCurrent=true, setAccount, closeModal }:
    { requireCurrent?: boolean, setAccount: (account: Account) => void, closeModal: () => void }
) => {
    const [tempCurrentPassword, setCurrentPassword] = useState('')
    const [tempNewPassword, setNewPassword] = useState('')
    const [tempConfirmPassword, setConfirmPassword] = useState('')
    const [isConfirmDisabled, setConfirmDisabled] = useState(true)
    const [error, setError] = useState('')
    const [legalAgree, setLegalAgree] = useState(false)

    const validateInputs = (current: string, newPass: string, confirmPass: string) => {
        const isValid =
            (!requireCurrent || current.trim().length >= 3) &&
            newPass.trim().length >= 3 &&
            confirmPass.trim().length >= 3 &&
            (!requireCurrent || legalAgree)

        setConfirmDisabled(!isValid)
    }

    const handleCurrentPasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const currentPassword = e.target.value
        setCurrentPassword(currentPassword)
        validateInputs(currentPassword, tempNewPassword, tempConfirmPassword)
    }

    const handleNewPasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const newPassword = e.target.value
        setNewPassword(newPassword)
        validateInputs(tempCurrentPassword, newPassword, tempConfirmPassword)
    }

    const handleConfirmPasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const confirmPassword = e.target.value
        setConfirmPassword(confirmPassword)
        validateInputs(tempCurrentPassword, tempNewPassword, confirmPassword)
    }

    const confirmEdit = async () => {
        if (tempNewPassword.trim() !== tempConfirmPassword.trim()) {
            setError('Make sure both entered passwords exactly match.')
            return
        }

        const payload: Record<string, string|boolean> = { new_password: tempNewPassword.trim() }
        if (requireCurrent) {
            payload.current_password = tempCurrentPassword.trim()
        } else {
            payload.legal_agree = legalAgree
        }

        await new Request(
            requireCurrent ? 'accounts/password' : 'accounts/password_upon_signup',
            (data: AccountResponse) => {
                setAccount(parseAccount(data))
                closeModal()
            },
            (error) => {
                if (error.includes('429')) {
                    setError(TOO_MANY_REQS_MSG)
                    return
                }
                setError(
                    error.includes('Invalid cookies')
                    ? 'Session has expired. Please log out then log in again to update your password.'
                    : error
                )
            }
        ).patch(payload)
    }

    return (
        <>
            <h2>Change Password</h2>

            {requireCurrent && (
                <section className="modal-input-sec">
                    <label style={{ marginRight: 10 }}>Current password: </label>
                    <input
                        type="password"
                        placeholder="Current password"
                        value={tempCurrentPassword}
                        onChange={handleCurrentPasswordChange}
                        maxLength={32}
                    />
                </section>
            )}

            <section className="modal-input-sec">
                <label style={{ marginRight: 10 }}>New password: </label>
                <input
                    type="password"
                    placeholder="New password"
                    value={tempNewPassword}
                    onChange={handleNewPasswordChange}
                    maxLength={32}
                />
            </section>

            <section className="modal-input-sec">
                <label style={{ marginRight: 10 }}>Confirm password: </label>
                <input
                    type="password"
                    placeholder="Confirm password"
                    value={tempConfirmPassword}
                    onChange={handleConfirmPasswordChange}
                    maxLength={32}
                />
            </section>

            {!requireCurrent && <LegalAgreeCheckbox setLegalAgree={setLegalAgree}/>}

            {error && <p className="error">{error}</p>}

            <button
                onClick={confirmEdit}
                disabled={isConfirmDisabled}
                id={isConfirmDisabled ? 'disabled-confirm-btn' : ''}
            >
                Confirm
            </button>
        </>
    )
}


/** Dashboard component for contacting us without the user manually inputting their email */
export const openRequestChangeModal = (queryType: QueryType, setModalContent: (content: ReactNode) => void, openModal: () => void) => {
    const RequestChangeContent = () => {
        const [formData, setFormData] = useState<{ queryType: QueryType, description: string }>({ queryType, description: '' })
        const [submitted, setSubmitted] = useState(false)
        const [errMsg, setErrMsg] = useState<string>('')

        const handleSubmit = async (e: FormEvent) => {
            e.preventDefault()
    
            if (!formData.description.trim()) {
                alert('Please fill out the description field.')
                return
            }
    
            await new Request('contact', undefined, setErrMsg, false).post({ query_type: formData.queryType, description: formData.description })
            setSubmitted(true)
        }

        return submitted ? (
            <p className='submit-msg'>
                {
                    errMsg 
                    ? <>An error occured: {errMsg}<br/>Please try again later.</>
                    : <>Thank you for reaching out!<br/>We&apos;ll reply to you through email soon.</>
                }
            </p>
        ) :  <form>
            <h1>Request Change</h1>
            <Dropdown
                label='Query Type'
                options={QUERY_TYPES}
                selectedOption={formData.queryType}
                setSelectedOption={option => setFormData({ ...formData, queryType: option as QueryType })}
            />
            <textarea
                name='description'
                placeholder='Describe your issue or message.'
                rows={4}
                className='input'
                required
                value={formData.description}
                onChange={e => setFormData({ ...formData, description: e.target.value })}
            ></textarea>
            <button onClick={handleSubmit}>Submit</button>
        </form>
    }

    setModalContent(<RequestChangeContent/>)
    openModal()
}


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
    private readonly endpointUrl: string
    private readonly responseCallback: (data: any) => any
    private readonly errorHandler: (error: string) => void
    private readonly includeCookies: boolean

    public constructor(
        endpoint: string,
        responseCallback: (data: any) => any = (x) => x,
        errorHandler: (error: string) => void = (error) => console.error(error),
        includeCookies: boolean = true
    ) {
        this.endpointUrl = `/api/${endpoint}`
        this.responseCallback = responseCallback
        this.errorHandler = errorHandler
        this.includeCookies = includeCookies
    }

    /**
     * Performs a GET request
     * @returns The output of the inputted callback function
     */
    public async get(requestData: object = {}): Promise<any> {
        const response = await fetch(this.endpointUrl, this.getPayload('GET', requestData))
        if (!response.ok) return this.errorHandler(`${response.status} HTTP error`)
        const data: EndpointResponse = await response.json()
        return 'error' in data ? this.errorHandler(data.error) : this.responseCallback(data)
    }

    /**
     * Performs a POST request
     * @returns The output of the inputted callback function
     */
    public async post(requestData: object = {}): Promise<any> {
        const response = await fetch(this.endpointUrl, this.getPayload('POST', requestData))
        if (!response.ok) return this.errorHandler(`${response.status} HTTP error`)
        const data: EndpointResponse = await response.json()
        return 'error' in data ? this.errorHandler(data.error) : this.responseCallback(data)
    }

    /**
     * Performs a PATCH request
     * @returns The output of the inputted callback function
     */
    public async patch(requestData: object = {}): Promise<any> {
        const response = await fetch(this.endpointUrl, this.getPayload('PATCH', requestData))
        if (!response.ok) return this.errorHandler(`${response.status} HTTP error`)
        const data: EndpointResponse = await response.json()
        return 'error' in data ? this.errorHandler(data.error) : this.responseCallback(data)
    }

    /**
     * Performs a DELETE request
     * @returns The output of the inputted callback function
     */
    public async delete(requestData: object = {}): Promise<any> {
        const response = await fetch(this.endpointUrl, this.getPayload('DELETE', requestData))
        if (!response.ok) return this.errorHandler(`${response.status} HTTP error`)
        const data: EndpointResponse = await response.json()
        return 'error' in data ? this.errorHandler(data.error) : this.responseCallback(data)
    }

    /**
     * Makes `this.requestData` able to be sent to the API server
     * @param method REST API Method
     * @returns The appropriate payload for the method
     */
    private getPayload(method: 'GET'|'POST'|'PATCH'|'DELETE', requestData: object): Record<string, string|object|undefined> {
        const payload: Record<string, string|object|undefined> = {
            method: method,
            headers: method !== 'GET' ? { 'Content-Type': 'application/json' } : undefined,
            credentials: this.includeCookies ? 'include': undefined
        }
        if (method !== 'GET') payload.body = JSON.stringify(requestData)
        return payload
    }
}
/* eslint-enable @typescript-eslint/no-explicit-any */


/**
 * Collection of functions that export a given schedule in supported formats
 * ### Constructor
 * @param scheduleToExport The schedule to export
 * @param shifts Shifts per day in the schedule
 * @param year The year of the schedule
 * @param month The month of the schedule
 */
export class ScheduleExporter {
    private readonly scheduleToExport: Schedule['schedule']
    private readonly shifts: Shift[]
    private readonly employees: Employee[]
    private readonly year: number
    private readonly month: number
    private readonly weekendDays: WeekendDays

    public constructor(
        scheduleToExport: Schedule['schedule'],
        shifts: Shift[],
        employees: Employee[],
        year: number,
        month: number,
        weekendDays: WeekendDays
    ) {
        this.scheduleToExport = scheduleToExport
        this.shifts = shifts
        this.employees = employees
        this.year = year
        this.month = month
        this.weekendDays = weekendDays
    }

    /** Exports the given schedule as an Excel spreadsheet */
    public async exportExcel(): Promise<void> {
        const workbook = new ExcelJS.Workbook()
        const worksheet = workbook.addWorksheet(`Schedule`)
        const daysInMonth = new Date(this.year, this.month + 1, 0).getDate() // Get the number of days in the month
        const uniqueShifts = [...new Set(this.shifts.map(shift => shift.name))] // Define unique shift names

        // Add a title row spanning all columns
        const monthNameOfSchedule = getMonthName(this.month)
        const title = `${monthNameOfSchedule} ${this.year}`
        const totalColumns = daysInMonth + uniqueShifts.length + 2
        worksheet.mergeCells(1, 1, 1, totalColumns) // Merge across all day columns, shift count columns, and total column
        const titleCell = worksheet.getCell(1, 1)
        titleCell.value = title
        titleCell.alignment = { horizontal: 'center', vertical: 'middle' }
        titleCell.font = { bold: true, size: 14, name: 'Calibri', color: { argb: 'FF000000' } } // Bold and larger font
        titleCell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF93CDDD' } } // Light blue background


        // Add the Employee column header spanning two rows
        worksheet.mergeCells('A2:A3')
        const employeeHeaderCell = worksheet.getCell('A2')
        employeeHeaderCell.value = 'Employee'
        employeeHeaderCell.alignment = { vertical: 'middle', horizontal: 'center' }
        employeeHeaderCell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF00FFFF' } } // Cyan background
        employeeHeaderCell.font = { bold: true, color: { argb: 'FF000000' }, name: 'Calibri', size: 12 } // Black text

        // Adjust Employee column width
        worksheet.getColumn(1).width = 30

        // Add day number and weekday name headers
        for (let dayIndex = 0; dayIndex < daysInMonth; dayIndex++) {
            const dayNumber = dayIndex + 1
            const weekdayName = getWeekdayName(this.year, this.month, dayNumber)
            const isWeekend = this.weekendDays.split(' & ').includes(weekdayName)

            // Day number (Row 2)
            const dayNumberCell = worksheet.getCell(2, dayIndex + 2)
            dayNumberCell.value = dayNumber
            dayNumberCell.alignment = { horizontal: 'center' }
            dayNumberCell.font = { bold: true, color: { argb: 'FF000000' }, name: 'Calibri', size: 12 } // Black text with custom font
            dayNumberCell.fill = {
                type: 'pattern',
                pattern: 'solid',
                fgColor: { argb: isWeekend ? 'FF92D050' : 'FFFFFF00' }, // Green for weekends, Yellow for weekdays
            }
            dayNumberCell.border = {
                top: { style: 'thin' },
                left: { style: 'thin' },
                bottom: { style: 'thin' },
                right: { style: 'thin' },
            }

            // Weekday name (Row 3)
            const weekdayCell = worksheet.getCell(3, dayIndex + 2)
            weekdayCell.value = weekdayName.slice(0, 3).toUpperCase()
            weekdayCell.alignment = { horizontal: 'center' }
            weekdayCell.font = { bold: true, color: { argb: 'FF000000' }, name: 'Calibri', size: 12 } // Black text with custom font
            weekdayCell.fill = {
                type: 'pattern',
                pattern: 'solid',
                fgColor: { argb: isWeekend ? 'FF92D050' : 'FFFFFF00' }, // Green for weekends, Yellow for weekdays
            }
            weekdayCell.border = {
                top: { style: 'thin' },
                left: { style: 'thin' },
                bottom: { style: 'thin' },
                right: { style: 'thin' },
            }
        }

        // Prepare data structure to store employees and their shifts for each day
        const employeeShiftMap = new Map<string, Record<string, string | number>>()

        this.scheduleToExport.forEach((day, dayIndex) => {
            day.forEach((shift, shiftIndex) => {
                const shiftName = this.shifts[shiftIndex]?.name || 'Unknown'
                shift.forEach(employee => {
                    const employeeName = employee.name
                    if (!employeeShiftMap.has(employeeName)) {
                        const record: Record<string, string | number> = { employee: employeeName }
                        for (let i = 1; i <= daysInMonth; i++) {
                            record[`day${i}`] = '' // Initialize empty shifts for all days
                        }
                        uniqueShifts.forEach(shift => {
                            record[shift] = 0 // Initialize count for each shift
                        })
                        record['(Total)'] = 0 // Initialize total column
                        employeeShiftMap.set(employeeName, record)
                    }
                    const record = employeeShiftMap.get(employeeName)!
                    record[`day${dayIndex + 1}`] = record[`day${dayIndex + 1}`]
                        ? `${record[`day${dayIndex + 1}`]}, ${shiftName}`
                        : shiftName // Append or set shift name
                    record[shiftName] = (record[shiftName] as number) + 1 // Increment shift count for this shift
                    record['(Total)'] = (record['(Total)'] as number) + 1 // Increment total count
                })
            })
        })

        // Ensure all registered employees are included in the export, even if they did not work any shifts
        this.employees.forEach(emp => {
            if (!employeeShiftMap.has(emp.name)) {
                const record: Record<string, string | number> = { employee: emp.name }
                for (let i = 1; i <= daysInMonth; i++) {
                    record[`day${i}`] = '-' // Default to hyphen for no shifts
                }
                uniqueShifts.forEach(shift => {
                    record[shift] = 0
                })
                record['(Total)'] = 0
                employeeShiftMap.set(emp.name, record)
            }
        })

        // Add shift count headers for each unique shift
        uniqueShifts.forEach((shift, index) => {
            const shiftColumnIndex = daysInMonth + 2 + index

            // Header cell for shift name (Row 2)
            if (!worksheet.getCell(2, shiftColumnIndex).isMerged) {
                worksheet.mergeCells(2, shiftColumnIndex, 3, shiftColumnIndex)
            }
            const shiftHeaderCell = worksheet.getCell(2, shiftColumnIndex)
            shiftHeaderCell.value = shift
            shiftHeaderCell.alignment = { vertical: 'middle', horizontal: 'center' }
            shiftHeaderCell.font = { bold: true, color: { argb: 'FF000000' }, name: 'Calibri', size: 12 }
            shiftHeaderCell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'BFE4EE' } } // Light blue background
            shiftHeaderCell.border = {
                top: { style: 'thin' },
                left: { style: 'thin' },
                bottom: { style: 'thin' },
                right: { style: 'thin' },
            }
        })

        // Add "Total" column header
        const totalColumnIndex = daysInMonth + uniqueShifts.length + 2
        if (!worksheet.getCell(2, totalColumnIndex).isMerged) {
            worksheet.mergeCells(2, totalColumnIndex, 3, totalColumnIndex)
        }
        const totalHeaderCell = worksheet.getCell(2, totalColumnIndex)
        totalHeaderCell.value = "(Total)"
        totalHeaderCell.alignment = { vertical: 'middle', horizontal: 'center' }
        totalHeaderCell.font = { bold: true, color: { argb: 'FF000000' }, name: 'Calibri', size: 12 }
        totalHeaderCell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'BFE4EE' } } // Light blue background
        totalHeaderCell.border = {
            top: { style: 'thin' },
            left: { style: 'thin' },
            bottom: { style: 'thin' },
            right: { style: 'thin' },
        }

        // Fill rows with data
        employeeShiftMap.forEach((record) => {
            const row = worksheet.addRow(record)

            // Apply background color for employee names
            const employeeCell = row.getCell(1)
            employeeCell.value = record.employee // Add employee name(s) to the Employee column
            employeeCell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF00FFFF' } } // Cyan background
            employeeCell.font = { bold: true, color: { argb: 'FF000000' }, name: 'Calibri', size: 12 } // Black text with custom font
            employeeCell.border = {
                top: { style: 'thin' },
                left: { style: 'thin' },
                bottom: { style: 'thin' },
                right: { style: 'thin' },
            }

            // Fill shift names for each day and color them based on the day column
            for (let dayIndex = 1; dayIndex <= daysInMonth; dayIndex++) {
                const shiftCell = row.getCell(dayIndex + 1)
                const dayNumber = dayIndex
                const weekdayName = getWeekdayName(this.year, this.month, dayNumber)
                const isWeekend = this.weekendDays.split(' & ').includes(weekdayName)

                shiftCell.value = record[`day${dayIndex}`] || '-' // Hyphen for empty cells
                shiftCell.alignment = { horizontal: 'center' }
                shiftCell.font = { name: 'Calibri', size: 12 } // Custom font

                if (isWeekend && shiftCell.value !== '-') {
                    shiftCell.fill = {
                        type: 'pattern',
                        pattern: 'solid',
                        fgColor: { argb: 'FF92D050' }, // Green for valid weekend cells
                    }
                } else if (!isWeekend && shiftCell.value !== '-') {
                    shiftCell.fill = {
                        type: 'pattern',
                        pattern: 'solid',
                        fgColor: { argb: 'FFFFFF00' }, // Yellow for valid weekday cells
                    }
                } else {
                    shiftCell.fill = {
                        type: 'pattern',
                        pattern: 'solid',
                        fgColor: { argb: 'FFB2B2B2' }, // Gray for empty cells
                    }
                }

                shiftCell.border = {
                    top: { style: 'thin' },
                    left: { style: 'thin' },
                    bottom: { style: 'thin' },
                    right: { style: 'thin' },
                }
            }

            // Fill shift count columns for each unique shift
            uniqueShifts.forEach((shift, index) => {
                const shiftColumnIndex = daysInMonth + 2 + index
                const shiftCountCell = row.getCell(shiftColumnIndex)
                shiftCountCell.value = record[shift] || 0 // Fetch or default to 0
                shiftCountCell.alignment = { horizontal: 'center' }
                shiftCountCell.font = { name: 'Calibri', size: 12 }
                shiftCountCell.fill = {
                    type: 'pattern',
                    pattern: 'solid',
                    fgColor: { argb: 'BFE4EE' }, // Light blue for shift count columns
                }
                shiftCountCell.border = {
                    top: { style: 'thin' },
                    left: { style: 'thin' },
                    bottom: { style: 'thin' },
                    right: { style: 'thin' },
                }
            })

            // Fill total column
            const totalCell = row.getCell(totalColumnIndex)
            totalCell.value = record['(Total)'] || 0
            totalCell.alignment = { horizontal: 'center' }
            totalCell.font = { name: 'Calibri', size: 12 }
            totalCell.fill = {
                type: 'pattern',
                pattern: 'solid',
                fgColor: { argb: 'BFE4EE' }, // Light blue for total column
            }
            totalCell.border = {
                top: { style: 'thin' },
                left: { style: 'thin' },
                bottom: { style: 'thin' },
                right: { style: 'thin' },
            }
        })

        // Adjust column widths dynamically based on content, including the "Employee" column
        worksheet.columns.forEach((column, colIndex) => {
            if (column && typeof column.eachCell === 'function') { // Ensure the column and its method are defined
                let maxWidth = 10; // Default minimum width
                column.eachCell({ includeEmpty: true }, (cell) => {
                    const cellValue = cell.value ? cell.value.toString() : '';
                    if (cellValue.length > maxWidth) {
                        maxWidth = cellValue.length + 2; // Add padding
                    }
                });
                worksheet.getColumn(colIndex + 1).width = maxWidth; // Apply calculated width
            }
        });

        // Write the workbook to a buffer and trigger download
        const buffer = await workbook.xlsx.writeBuffer()
        const blob = new Blob([buffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
        const link = document.createElement('a')
        link.href = URL.createObjectURL(blob)
        link.download = `${monthNameOfSchedule.slice(0, 3)}-${this.year}-Schedule.xlsx`
        link.click()
    }

    /** Exports the given schedule in JSON format */
    public exportJSON(): void {
        let fileContent = 'data:application/jsoncharset=utf-8,' 
        fileContent += encodeURIComponent(JSON.stringify(this.scheduleToExport, null, 2))

        const link = document.createElement('a')
        link.setAttribute('href', fileContent)
        link.setAttribute('download', `${getMonthName(this.month).slice(0, 3)}-${this.year}-Schedule.json`)
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
    }

    /** Exports the given schedule as a downloadable CSV file */
    public exportCSV(): void { this.exportDelimited(',', 'csv') }

    /** Exports the given schedule as a downloadable TSV file */
    public exportTSV(): void { this.exportDelimited('\t', 'tsv') }

    /**
     * Generic function to export the given schedule in a delimited format
     * @param delimiter - The delimiter for the format (e.g., ',' for CSV, '\t' for TSV)
     * @param extension - The file extension (e.g., 'csv', 'tsv')
     */
    private exportDelimited(delimiter: string, extension: SupportedExportFormat): void {
        const columnHeaders = ['Day', 'Shift', 'Employee Name', 'Employee ID']
        let fileContent = 'data:text/plaincharset=utf-8,'
        // Adds the column headers as the first row
        fileContent += [
            columnHeaders.join(delimiter),
            ...this.scheduleToExport.map((day, dayI) =>
                day.map((shift, shiftI) =>
                    shift.map(emp => `${dayI + 1}${delimiter}${this.shifts[shiftI].name}${delimiter}${emp.name}${delimiter}${emp.id}`).join('\n')
                ).join('\n')
            )
        ].join('\n')

        const encodedUri = encodeURI(fileContent)

        const link = document.createElement('a')
        link.setAttribute('href', encodedUri)
        link.setAttribute('download', `${getMonthName(this.month).slice(0, 3)}-${this.year}-Schedule.${extension}`)
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
    }
}