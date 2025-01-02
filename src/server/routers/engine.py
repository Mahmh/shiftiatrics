from functools import wraps
from fastapi import APIRouter
from jpype import java, JArray, JInt, JString
from src.server.lib.db import get_all_employees_of_account, get_all_shifts_of_account, get_settings_of_account, get_all_schedules_of_account
from src.server.lib.utils import err_log, log
from src.server.lib.models import ScheduleType
from src.server.engine import Engine

# Init
engine_router = APIRouter()

def endpoint(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            err_log(func.__name__, e, 'engine')
            return {'error': str(e)}
    return wrapper


# Endpoints
@engine_router.get('/engine/generate_schedule')
@endpoint
def generate_schedule(account_id: int, num_days: int) -> ScheduleType | dict[str, str]:
    employees = get_all_employees_of_account(account_id)
    shifts = get_all_shifts_of_account(account_id)
    settings = get_settings_of_account(account_id)
    if not employees or not shifts: raise ValueError("No employees or shifts found for the account.")

    if settings is None:
        min_max_work_hours_enabled = False
        multi_emps_in_shift_enabled = False
        multi_shifts_one_emp_enabled = False
    else:
        min_max_work_hours_enabled = settings.min_max_work_hours_enabled
        multi_emps_in_shift_enabled = settings.multi_emps_in_shift_enabled
        multi_shifts_one_emp_enabled = settings.multi_shifts_one_emp_enabled

    engine = Engine()

    # Create a list of Employee objects
    employee_list = [
        engine.Employee(e.employee_id, JString(e.employee_name), e.min_work_hours, e.max_work_hours)
        if e.min_work_hours and e.max_work_hours
        else engine.Employee(e.employee_id, JString(e.employee_name))
        for e in employees
    ]

    # Convert Python list to Java ArrayList
    java_employee_list = java.util.ArrayList()
    for employee in employee_list:
        java_employee_list.add(employee)

    # Create a list of Shift objects, converting time to string format
    shift_list = [
        engine.Shift(shift.start_time.strftime("%H:%M"), shift.end_time.strftime("%H:%M"))
        for shift in shifts
    ]

    # Convert Python list to Java ArrayList
    java_shift_list = java.util.ArrayList()
    for shift in shift_list:
        java_shift_list.add(shift)

    # Generate the schedule using the Java Engine
    raw_schedule = engine.ShiftScheduler.generateSchedule(
        java_employee_list, java_shift_list, num_days,
        min_max_work_hours_enabled, multi_emps_in_shift_enabled, multi_shifts_one_emp_enabled
    )

    # Convert the Java 3D array into a Python-native structure
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
@endpoint
def get_shift_counts_of_employees(account_id: int, year: int, month: int) -> dict[int, int] | dict[str, str]:
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
@endpoint
def get_work_hours_of_employees(account_id: int, year: int, month: int) -> dict[int, int] | dict[str, str]:
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