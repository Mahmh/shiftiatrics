from fastapi import APIRouter, Request
from jpype import java, JArray, JInt, JString
from src.server.engine import Engine
from src.server.rate_limit import limiter
from src.server.lib.constants import DEFAULT_RATE_LIMIT
from src.server.lib.utils import log
from src.server.lib.models import ScheduleType
from src.server.lib.api import endpoint
from src.server.db import (
    get_all_employees_of_account,
    get_all_shifts_of_account,
    get_settings_of_account,
    get_all_schedules_of_account,
    get_all_holidays_of_account
)

# Init
engine_router = APIRouter()

# Endpoints
@engine_router.get('/engine/generate_schedule')
@limiter.limit(DEFAULT_RATE_LIMIT)
@endpoint()
async def generate_schedule(account_id: int, num_days: int, year: int, month: int, request: Request) -> ScheduleType | dict[str, str]:
    # month is in range [0, 11]
    employees = get_all_employees_of_account(account_id)
    shifts = get_all_shifts_of_account(account_id)
    holidays = get_all_holidays_of_account(account_id)
    if not employees: raise ValueError('No employees registered by the account.')
    if not shifts: raise ValueError('No shifts registered by the account.')

    settings = get_settings_of_account(account_id)
    if settings is None:
        min_max_work_hours_enabled = False
        multi_emps_in_shift_enabled = False
        multi_shifts_one_emp_enabled = False
        max_emps_in_shift = 1
    else:
        min_max_work_hours_enabled = settings.min_max_work_hours_enabled
        multi_emps_in_shift_enabled = settings.multi_emps_in_shift_enabled
        multi_shifts_one_emp_enabled = settings.multi_shifts_one_emp_enabled
        max_emps_in_shift = settings.max_emps_in_shift if settings.multi_emps_in_shift_enabled else 1

    engine = Engine()

    # Create a list of Employee objects & convert it to Java ArrayList
    employee_list = [
        engine.Employee(e.employee_id, JString(e.employee_name), e.min_work_hours, e.max_work_hours)
        if e.min_work_hours and e.max_work_hours
        else engine.Employee(e.employee_id, JString(e.employee_name))
        for e in employees
    ]
    java_employee_list = java.util.ArrayList()
    for employee in employee_list: java_employee_list.add(employee)


    # Create a list of Shift objects, converting time to string format & convert it to Java ArrayList
    shift_list = [
        engine.Shift(shift.start_time.strftime("%H:%M"), shift.end_time.strftime("%H:%M"))
        for shift in shifts
    ]
    java_shift_list = java.util.ArrayList()
    for shift in shift_list: java_shift_list.add(shift)


    # Same for Holidays
    holiday_list = [
        engine.Holiday(
            JString(holiday.holiday_name),
            java.util.ArrayList([JInt(emp_id) for emp_id in holiday.assigned_to]),
            JString(holiday.start_date.strftime("%Y-%m-%d")),
            JString(holiday.end_date.strftime("%Y-%m-%d"))
        )
        for holiday in holidays
    ]
    java_holiday_list = java.util.ArrayList()
    for holiday in holiday_list: java_holiday_list.add(holiday)


    # Generate the schedule using the Java Engine & convert the Java 3D array into a Python-native structure
    raw_schedule = engine.ShiftScheduler.generateSchedule(
        java_employee_list, java_shift_list, java_holiday_list,
        num_days, year, month,
        min_max_work_hours_enabled, multi_emps_in_shift_enabled, multi_shifts_one_emp_enabled,
        max_emps_in_shift
    )

    schedule = []
    for day_schedule in raw_schedule:
        daily_shifts = []
        for shift_schedule in day_schedule:
            employee_ids = []
            for employee in shift_schedule:
                employee_ids.append(employee.getId())
            daily_shifts.append(employee_ids)
        schedule.append(daily_shifts)
    return schedule


@engine_router.get('/engine/get_shift_counts_of_employees')
@limiter.limit(DEFAULT_RATE_LIMIT)
@endpoint()
async def get_shift_counts_of_employees(account_id: int, year: int, month: int, request: Request) -> dict[int, int] | dict[str, str]:
    # Fetch the schedule for the given account, year, and month
    schedule_data = get_all_schedules_of_account(account_id, year=year, month=month)
    if not schedule_data: raise ValueError("No schedule found for the given account, year, and month.")
    schedule = schedule_data[0].schedule  # Extract the schedule

    # Convert Python ScheduleType to Java int[][][]
    java_schedule = JArray(JArray(JArray(JInt)))(len(schedule))  # Create the outermost array
    for day_index, day in enumerate(schedule):
        java_day = JArray(JArray(JInt))(len(day))  # Create the day's array
        for shift_index, shift in enumerate(day):
            if shift is not None:  # Handle non-empty shifts
                java_shift = JArray(JInt)(shift)  # Convert shift list to Java array
            else:
                java_shift = JArray(JInt)(0)  # Empty array for None
            java_day[shift_index] = java_shift
        java_schedule[day_index] = java_day

    # Call the Java method and convert the result (Java HashMap) to a Python dict
    engine = Engine()
    java_result = engine.ShiftScheduler.getShiftCountsOfEmployees(java_schedule)
    shift_counts = {key: java_result[key] for key in java_result.keySet()}
    return shift_counts


@engine_router.get('/engine/get_work_hours_of_employees')
@limiter.limit(DEFAULT_RATE_LIMIT)
@endpoint()
async def get_work_hours_of_employees(account_id: int, year: int, month: int, request: Request) -> dict[int, int] | dict[str, str]:
    # Fetch the schedule and shifts for the given account, year, and month
    schedule: list[ScheduleType] = get_all_schedules_of_account(account_id, year=year, month=month)[0].schedule
    shifts = get_all_shifts_of_account(account_id)  # list of unique shifts per day
    if not schedule: raise ValueError("No schedule found for the given account, year, and month.")
    if not shifts: raise ValueError("No shifts found for the given account, year, and month.")
    engine = Engine()

    # Convert shifts data to Java Shift objects
    shifts = [engine.Shift(JString(str(shift.start_time)), JString(str(shift.end_time))) for shift in shifts]

    # Convert the Python list to a java.util.ArrayList
    shifts_java = java.util.ArrayList()
    for shift in shifts: shifts_java.add(shift)
    log(f"shifts_java: {list(shifts_java)}", 'engine', 'DEBUG')

    # Convert schedule_data to a Java-compatible int[][][] array
    num_days = len(schedule)
    schedule_java = JArray(JArray(JArray(JInt)))(
        [[[JInt(emp_id) for emp_id in shift] for shift in day] for day in schedule]
    )
    log(f"schedule_java: {list(schedule_java)}", 'engine', 'DEBUG')

    # Calculate work hours using the Java method
    work_hours_java = engine.ShiftScheduler.getWorkHoursOfEmployees(schedule_java, shifts_java, num_days)
    log(f"work_hours_java: {work_hours_java}", 'engine', 'DEBUG')

    # Convert the resulting Java HashMap to a Python dictionary
    work_hours = {int(entry.getKey()): int(entry.getValue()) for entry in work_hours_java.entrySet()}
    log(f"work_hours: {work_hours}", 'engine', 'DEBUG')
    return work_hours