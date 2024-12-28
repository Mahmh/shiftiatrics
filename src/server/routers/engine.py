from functools import wraps
from fastapi import APIRouter
from jpype import java, JArray, JInt
from src.server.lib.db import get_all_employees_of_account, get_all_schedules_of_account
from src.server.lib.utils import err_log, log
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
@engine_router.post('/engine/generate_schedule')
@endpoint
def generate_schedule(account_id: int, num_shifts_per_day: int, num_days: int) -> list[list[int]] | dict[str, str]:
    employees = get_all_employees_of_account(account_id)
    engine = Engine()

    # Create a list of Employee objects
    employee_list = [engine.Employee(e.employee_id, e.employee_name) for e in employees]

    # Convert the Python list into a Java ArrayList
    java_employee_list = java.util.ArrayList()
    for employee in employee_list: java_employee_list.add(employee)

    # Call the Java method with the correct argument types
    raw_schedule = engine.ShiftScheduler.generateSchedule(java_employee_list, num_shifts_per_day, num_days)

    # Convert the Java 2D array into a Python-native structure
    schedule = []
    for day_schedule in raw_schedule:
        daily_shifts = []
        for employee in day_schedule:
            if employee: daily_shifts.append(employee.getId())
            else: log(f'Employee is {employee}', 'engine', 'DEBUG')
        schedule.append(daily_shifts)
    return schedule


@engine_router.post('/engine/get_shift_counts_of_employees')
@endpoint
def get_shift_counts_of_employees(account_id: int, year: int, month: int) -> dict[int, int] | dict[str, str]:
    schedule = get_all_schedules_of_account(account_id, year=year, month=month)[0].schedule
    engine = Engine()

    # Convert Python list[list[int]] to Java int[][]
    java_schedule = JArray(JArray(JInt))(len(schedule))  # Create the outer array
    for i, day in enumerate(schedule):
        java_day = JArray(JInt)([x if x is not None else 0 for x in day])  # Handle None values as 0
        java_schedule[i] = java_day

    # Call the method & convert the result (Java HashMap) into a Python dict
    java_result = engine.ShiftScheduler.getShiftCountsOfEmployees(java_schedule)
    shift_counts = {key: java_result[key] for key in java_result.keySet()}
    return shift_counts