from functools import wraps
from fastapi import APIRouter
from jpype import java
from src.server.lib.db import get_all_employees_of_account
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
@engine_router.get('/engine/current_month_days')
@endpoint
def get_current_month_days() -> list | dict:
    return list(Engine().ShiftScheduler.getCurrentMonthDays())


@engine_router.post('/engine/generate_schedule')
@endpoint
def generate_schedule(account_id: int, num_shifts_per_day: int) -> list | dict:
    employees = get_all_employees_of_account(account_id)
    engine = Engine()

    # Create a list of Employee objects
    employee_list = [engine.Employee(i, e.employee_name) for i, e in enumerate(employees, 1)]

    # Convert the Python list into a Java ArrayList
    java_employee_list = java.util.ArrayList()
    for employee in employee_list: java_employee_list.add(employee)

    # Call the Java method with the correct argument types
    raw_schedule = engine.ShiftScheduler.generateSchedule(java_employee_list, num_shifts_per_day)

    # Convert the Java 2D array into a Python-native structure
    schedule = []
    for day_schedule in raw_schedule:
        daily_shifts = []
        for employee in day_schedule:
            if employee:
                daily_shifts.append(str(employee.name))
            else:
                log(f'{employee} is None', 'engine', 'DEBUG')
        schedule.append(daily_shifts)
    return schedule