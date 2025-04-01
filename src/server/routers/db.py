from typing import Literal, Optional
from fastapi import APIRouter, Request, Response, Body
from src.server.rate_limit import limiter
from src.server.lib.constants import DEFAULT_RATE_LIMIT
from src.server.lib.models import Credentials, Cookies, EmployeeInfo, ShiftInfo, ScheduleInfo, HolidayInfo
from src.server.lib.api import endpoint, get_cookies, store_cookies, clear_cookies, return_account_and_sub
from src.server.lib.types import SettingValue
from src.server.db import (
    create_account, change_email, change_password, set_password, delete_account,
    get_all_employees_of_account, create_employee, update_employee, delete_employee,
    get_all_shifts_of_account, create_shift, update_shift, delete_shift,
    get_all_schedules_of_account, create_schedule, update_schedule, delete_schedule,
    get_settings_of_account, update_setting,
    get_all_holidays_of_account, create_holiday, update_holiday, delete_holiday
)

# Init
account_router = APIRouter()
employee_router = APIRouter()
shift_router = APIRouter()
schedule_router = APIRouter()
holiday_router = APIRouter()
settings_router = APIRouter()


# Endpoints
## Account
@account_router.post('/accounts/signup')
@limiter.limit('10/minute')
@endpoint(auth=False)
async def create_new_account(cred: Credentials, response: Response, request: Request) -> dict:
    account, token = create_account(cred)
    store_cookies(Cookies(account_id=account.account_id, token=token), response)
    return return_account_and_sub(account)


@account_router.patch('/accounts/email')
@limiter.limit(DEFAULT_RATE_LIMIT)
@endpoint()
async def change_email_endpoint(request: Request, email: str = Body(..., embed=True)) -> dict:
    return change_email(get_cookies(request), email)


@account_router.patch('/accounts/password')
@limiter.limit(DEFAULT_RATE_LIMIT)
@endpoint()
async def change_password_endpoint(request: Request, current_password: Optional[str] = Body(None, embed=True), new_password: str = Body(..., embed=True)) -> dict:
    if current_password:
        return change_password(get_cookies(request), current_password, new_password)
    else:
        return set_password(get_cookies(request), new_password)


@account_router.delete('/accounts')
@limiter.limit(DEFAULT_RATE_LIMIT)
@endpoint()
async def delete_existing_account(request: Request, response: Response) -> dict:
    delete_account(get_cookies(request))
    clear_cookies(response)
    return {'detail': 'Account deleted successfully'}



## Employee
@employee_router.get('/accounts/{account_id}/employees')
@limiter.limit(DEFAULT_RATE_LIMIT)
@endpoint()
async def read_employees(account_id: int, request: Request) -> list[dict] | dict:
    return get_all_employees_of_account(account_id=account_id)


@employee_router.post('/accounts/{account_id}/employees')
@limiter.limit(DEFAULT_RATE_LIMIT)
@endpoint()
async def create_new_employee(account_id: int, info: EmployeeInfo, request: Request) -> dict:
    return create_employee(account_id=account_id, employee_name=info.employee_name, min_work_hours=info.min_work_hours, max_work_hours=info.max_work_hours)


@employee_router.patch('/employees/{employee_id}')
@limiter.limit(DEFAULT_RATE_LIMIT)
@endpoint()
async def update_existing_employee(employee_id: int, updates: dict, request: Request) -> dict:
    return update_employee(employee_id=employee_id, updates=updates)


@employee_router.delete('/employees/{employee_id}')
@limiter.limit(DEFAULT_RATE_LIMIT)
@endpoint()
async def delete_existing_employee(employee_id: int, request: Request) -> dict:
    delete_employee(employee_id=employee_id)
    return {'detail': 'Employee deleted successfully'}



## Shift
@shift_router.get('/accounts/{account_id}/shifts')
@limiter.limit(DEFAULT_RATE_LIMIT)
@endpoint()
async def read_shifts(account_id: int, request: Request) -> list[dict] | dict:
    return get_all_shifts_of_account(account_id=account_id)


@shift_router.post('/accounts/{account_id}/shifts')
@limiter.limit(DEFAULT_RATE_LIMIT)
@endpoint()
async def create_new_shift(account_id: int, info: ShiftInfo, request: Request) -> dict:
    return create_shift(account_id=account_id, shift_name=info.shift_name, start_time=info.start_time, end_time=info.end_time)


@shift_router.patch('/shifts/{shift_id}')
@limiter.limit(DEFAULT_RATE_LIMIT)
@endpoint()
async def update_existing_shift(shift_id: int, updates: dict, request: Request) -> dict:
    return update_shift(shift_id=shift_id, updates=updates)


@shift_router.delete('/shifts/{shift_id}')
@limiter.limit(DEFAULT_RATE_LIMIT)
@endpoint()
async def delete_existing_shift(shift_id: int, request: Request) -> dict:
    delete_shift(shift_id=shift_id)
    return {'detail': 'Shift deleted successfully'}



## Schedule
@schedule_router.get('/accounts/{account_id}/schedules')
@limiter.limit(DEFAULT_RATE_LIMIT)
@endpoint()
async def read_schedules(account_id: int, request: Request) -> list[dict] | dict:
    return get_all_schedules_of_account(account_id=account_id)


@schedule_router.post('/accounts/{account_id}/schedules')
@limiter.limit(DEFAULT_RATE_LIMIT)
@endpoint()
async def create_new_schedule(account_id: int, info: ScheduleInfo, request: Request) -> dict:
    return create_schedule(account_id=account_id, schedule=info.schedule, month=info.month, year=info.year)


@schedule_router.patch('/schedules/{schedule_id}')
@limiter.limit(DEFAULT_RATE_LIMIT)
@endpoint()
async def update_existing_schedule(schedule_id: int, updates: dict, request: Request) -> dict:
    return update_schedule(schedule_id=schedule_id, updates=updates)


@schedule_router.delete('/schedules/{schedule_id}')
@limiter.limit(DEFAULT_RATE_LIMIT)
@endpoint()
async def delete_existing_schedule(schedule_id: int, request: Request) -> dict:
    delete_schedule(schedule_id=schedule_id)
    return {'detail': 'Schedule deleted successfully'}



## Holiday
@holiday_router.get('/accounts/{account_id}/holidays')
@limiter.limit(DEFAULT_RATE_LIMIT)
@endpoint()
async def read_holidays(account_id: int, request: Request) -> list[dict] | dict:
    return get_all_holidays_of_account(account_id=account_id)


@holiday_router.post('/accounts/{account_id}/holidays')
@limiter.limit(DEFAULT_RATE_LIMIT)
@endpoint()
async def create_new_holiday(account_id: int, info: HolidayInfo, request: Request) -> dict:
    return create_holiday(account_id=account_id, holiday_name=info.holiday_name, assigned_to=info.assigned_to, start_date=info.start_date, end_date=info.end_date)


@holiday_router.patch('/holidays/{holiday_id}')
@limiter.limit(DEFAULT_RATE_LIMIT)
@endpoint()
async def update_existing_holiday(holiday_id: int, updates: dict, request: Request) -> dict:
    return update_holiday(holiday_id=holiday_id, updates=updates)


@holiday_router.delete('/holidays/{holiday_id}')
@limiter.limit(DEFAULT_RATE_LIMIT)
@endpoint()
async def delete_existing_holiday(holiday_id: int, request: Request) -> dict:
    delete_holiday(holiday_id=holiday_id)
    return {'detail': 'Holiday deleted successfully'}



## Settings
@settings_router.get('/accounts/{account_id}/settings')
@limiter.limit(DEFAULT_RATE_LIMIT)
@endpoint()
async def read_settings(account_id: int, request: Request) -> dict:
    return get_settings_of_account(account_id=account_id)


@settings_router.patch('/accounts/{account_id}/settings')
@limiter.limit(DEFAULT_RATE_LIMIT)
@endpoint()
async def update_one_setting(account_id: int, request: Request, setting: str = Body(..., embed=True), new_value: SettingValue = Body(..., embed=True)) -> dict:
    return update_setting(account_id, setting, new_value)