from functools import wraps
from fastapi import APIRouter
from src.server.lib.models import Credentials, EmployeeInfo, ShiftInfo, ScheduleInfo
from src.server.lib.utils import todict, todicts
from src.server.lib.db import (
    Account, Employee, Shift, Schedule,
    get_all_accounts, log_in_account, create_account, update_account, delete_account,
    get_all_employees_of_account, create_employee, update_employee, delete_employee,
    get_all_shifts_of_account, create_shift, update_shift, delete_shift,
    get_all_schedules_of_account, create_schedule, update_schedule, delete_schedule
)

# Init
account_router = APIRouter()
employee_router = APIRouter()
shift_router = APIRouter()
schedule_router = APIRouter()

def endpoint(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            if type(result) in (Account, Employee, Shift, Schedule):
                return todict(result)
            elif type(result) is list:
                try: return todicts(result)
                except: return result
            return result 
        except Exception as e:
            return {'error': str(e)}
    return wrapper


# Endpoints
## Account
@account_router.get('/accounts')
@endpoint
def read_accounts() -> list[dict] | dict:
    return get_all_accounts()


@account_router.post('/accounts/login')
@endpoint
def login_account(cred: Credentials) -> dict:
    return log_in_account(cred)


@account_router.post('/accounts/signup')
@endpoint
def create_new_account(cred: Credentials) -> dict:
    return create_account(cred)


@account_router.patch('/accounts')
@endpoint
def update_existing_account(cred: Credentials, updates: dict) -> dict:
    return update_account(cred, updates)


@account_router.delete('/accounts')
@endpoint
def delete_existing_account(cred: Credentials) -> dict:
    delete_account(cred)
    return {'detail': 'Account deleted successfully'}


## Employee
@employee_router.get('/accounts/{account_id}/employees')
@endpoint
def read_employees(account_id: int) -> list[dict] | dict:
    return get_all_employees_of_account(account_id=account_id)


@employee_router.post('/accounts/{account_id}/employees')
@endpoint
def create_new_employee(account_id: int, info: EmployeeInfo) -> dict:
    return create_employee(account_id=account_id, employee_name=info.employee_name)


@employee_router.patch('/employees/{employee_id}')
@endpoint
def update_existing_employee(employee_id: int, updates: dict) -> dict:
    return update_employee(employee_id=employee_id, updates=updates)


@employee_router.delete('/employees/{employee_id}')
@endpoint
def delete_existing_employee(employee_id: int) -> dict:
    delete_employee(employee_id=employee_id)
    return {'detail': 'Employee deleted successfully'}


## Shift
@shift_router.get('/accounts/{account_id}/shifts')
@endpoint
def read_shifts(account_id: int) -> list[dict] | dict:
    return get_all_shifts_of_account(account_id=account_id)


@shift_router.post('/accounts/{account_id}/shifts')
@endpoint
def create_new_shift(account_id: int, info: ShiftInfo) -> dict:
    return create_shift(account_id=account_id, shift_name=info.shift_name, start_time=info.start_time, end_time=info.end_time)


@shift_router.patch('/shifts/{shift_id}')
@endpoint
def update_existing_shift(shift_id: int, updates: dict) -> dict:
    return update_shift(shift_id=shift_id, updates=updates)


@shift_router.delete('/shifts/{shift_id}')
@endpoint
def delete_existing_shift(shift_id: int) -> dict:
    delete_shift(shift_id=shift_id)
    return {'detail': 'Shift deleted successfully'}


## Schedule
@schedule_router.get('/accounts/{account_id}/schedules')
@endpoint
def read_schedules(account_id: int) -> list[dict] | dict:
    return get_all_schedules_of_account(account_id=account_id)


@schedule_router.post('/accounts/{account_id}/schedules')
@endpoint
def create_new_schedule(account_id: int, info: ScheduleInfo) -> dict:
    return create_schedule(account_id=account_id, schedule=info.schedule)


@schedule_router.patch('/schedules/{schedule_id}')
@endpoint
def update_existing_schedule(schedule_id: int, updates: dict) -> dict:
    return update_schedule(schedule_id=schedule_id, updates=updates)


@schedule_router.delete('/schedules/{schedule_id}')
@endpoint
def delete_existing_schedule(schedule_id: int) -> dict:
    delete_schedule(schedule_id=schedule_id)
    return {'detail': 'Schedule deleted successfully'}