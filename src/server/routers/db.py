from typing import Literal, Optional
from fastapi import APIRouter, Request, Response, Body
from src.server.rate_limit import limiter
from src.server.lib.constants import DEFAULT_RATE_LIMIT
from src.server.lib.models import Credentials, Cookies, EmployeeInfo, ShiftInfo, ScheduleInfo, HolidayInfo, SubscriptionInfo
from src.server.lib.api import endpoint, get_cookies, store_cookies, clear_cookies
from src.server.lib.types import WeekendDays, Interval
from src.server.lib.utils import todict
from src.server.db import (
    create_account, change_email, change_password, set_password, delete_account,
    get_all_employees_of_account, create_employee, update_employee, delete_employee,
    get_all_shifts_of_account, create_shift, update_shift, delete_shift,
    get_all_schedules_of_account, create_schedule, update_schedule, delete_schedule,
    get_settings_of_account, toggle_dark_theme, toggle_min_max_work_hours,
    get_all_holidays_of_account, create_holiday, update_holiday, delete_holiday,
    toggle_multi_emps_in_shift, toggle_multi_shifts_one_emp, update_weekend_days, update_max_emps_in_shift,
    toggle_email_ntf, update_email_ntf_interval,
    get_num_schedule_requests
)

# Init
account_router = APIRouter()
employee_router = APIRouter()
shift_router = APIRouter()
schedule_router = APIRouter()
holiday_router = APIRouter()
settings_router = APIRouter()
sub_router = APIRouter()


# Endpoints
## Account
@account_router.post('/accounts/signup')
@limiter.limit('10/minute')
@endpoint(auth=False)
async def create_new_account(cred: Credentials, sub_info: SubscriptionInfo, response: Response, request: Request) -> dict:
    account, sub, token = create_account(cred, sub_info)
    store_cookies(Cookies(account_id=account.account_id, token=token), response)
    return {'account': todict(account), 'subscription': todict(sub)}


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
    res = get_settings_of_account(account_id=account_id)
    return res if res is not None else {'detail': res}


@settings_router.get('/accounts/{account_id}/settings/toggle_dark_theme')
@limiter.limit(DEFAULT_RATE_LIMIT)
@endpoint()
async def toggle_dark_theme_(account_id: int, request: Request) -> dict:
    return {'detail': toggle_dark_theme(account_id=account_id)}


@settings_router.get('/accounts/{account_id}/settings/toggle_min_max_work_hours')
@limiter.limit(DEFAULT_RATE_LIMIT)
@endpoint()
async def toggle_min_max_work_hours_(account_id: int, request: Request) -> dict:
    return {'detail': toggle_min_max_work_hours(account_id=account_id)}


@settings_router.get('/accounts/{account_id}/settings/toggle_multi_emps_in_shift')
@limiter.limit(DEFAULT_RATE_LIMIT)
@endpoint()
async def toggle_multi_emps_in_shift_(account_id: int, request: Request) -> dict:
    return {'detail': toggle_multi_emps_in_shift(account_id=account_id)}


@settings_router.get('/accounts/{account_id}/settings/toggle_multi_shifts_one_emp')
@limiter.limit(DEFAULT_RATE_LIMIT)
@endpoint()
async def toggle_multi_shifts_one_emp_(account_id: int, request: Request) -> dict:
    return {'detail': toggle_multi_shifts_one_emp(account_id=account_id)}


@settings_router.patch('/accounts/{account_id}/settings/update_weekend_days')
@limiter.limit(DEFAULT_RATE_LIMIT)
@endpoint()
async def update_weekend_days_(account_id: int, info: dict[Literal['weekend_days'], WeekendDays], request: Request) -> dict:
    return {'detail': update_weekend_days(account_id=account_id, weekend_days=info['weekend_days'])}


@settings_router.patch('/accounts/{account_id}/settings/max_emps_in_shift')
@limiter.limit(DEFAULT_RATE_LIMIT)
@endpoint()
async def update_max_emps_in_shift_(account_id: int, info: dict[Literal['max_emps_in_shift'], int], request: Request) -> dict:
    return {'detail': update_max_emps_in_shift(account_id=account_id, max_emps_in_shift=info['max_emps_in_shift'])}


@settings_router.get('/accounts/{account_id}/settings/toggle_email_ntf')
@limiter.limit(DEFAULT_RATE_LIMIT)
@endpoint()
async def toggle_email_ntf_(account_id: int, request: Request) -> dict:
    return {'detail': toggle_email_ntf(account_id=account_id)}


@settings_router.patch('/accounts/{account_id}/settings/update_email_ntf_interval')
@limiter.limit(DEFAULT_RATE_LIMIT)
@endpoint()
async def update_email_ntf_interval_(account_id: int, info: dict[Literal['email_ntf_interval'], Interval], request: Request) -> dict:
    return {'detail': update_email_ntf_interval(account_id=account_id, interval=info['email_ntf_interval'])}



## Subscription
@sub_router.get('/sub/{account_id}/schedule_requests')
@limiter.limit(DEFAULT_RATE_LIMIT)
@endpoint()
async def get_schedule_requests_(account_id: int, request: Request) -> dict:
    return {'num_requests': get_num_schedule_requests(account_id)}