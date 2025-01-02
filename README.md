# AutoShift: Automated Shift Scheduling for Businesses
<u>Problem statement:</u> Businesses take a lot of time and energy in scheduling shifts & designing agreed-upon rosters every month.

<u>Solution:</u> I built an automated scheduling website for businesses to use for automating this tedious task.

## Problem Analysis
Here are the challenges to keep track of:
- Businesses differ in scheduling shifts; for example, some designate employees for day and evening shifts without night ones. Others, such as emergency doctors, have day, evening, and night shifts as well.
- In addition, there is a variable number of employees to keep track of when designing the monthly schedule; that number may change per month.
- Employees can swap with other ones, thus modifying the schedule.

With all of that information, I can design an effective system for automating schedules (auto-scheduling engine).

## System Architecture & Plan
### File System
- `src` (Source code):
    - `client`: Code for the website.
    - `server`: Code for the auto-scheduling engine, back-end server, and utilities.
    - `db`: Data and schema for the database.
- `tests` (Automated tests for the whole app)

### Client-Server Connection
<img src='img/client_and_server.png' width=700>

### Tech Stack
- Frontend:
    - **Next.js & TypeScript** for website programming.
    - **SASS** for website styling.
- Backend:
    - **Java** for running the auto-scheduling engine while prioritizing performance and memory safety.
    - **Python** for running the back-end server, and for writing utilities as Python has a large number of useful libraries.
- Database:
    - **PostgreSQL** for running SQL queries and the database server.

    | Table Name  | Fields                                                                                   |
    |-------------|------------------------------------------------------------------------------------------|
    | Accounts    | Account ID, Username, Password                                                          |
    | Employees   | Account ID, Employee ID, Employee Name, Min Work Hours, Max Work Hours                  |
    | Shifts      | Account ID, Shift ID, Shift Name, Start Time, End Time                                  |
    | Schedules   | Account ID, Schedule ID, Schedule (JSONB), Month, Year                                  |
    | Settings    | Account ID, Dark Theme Enabled, Min Max Work Hours Enabled, Multi Emps in Shift Enabled, Multi Shifts One Emp Enabled |
