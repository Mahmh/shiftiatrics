from typing import Literal
from functools import wraps
from fastapi import APIRouter, Request, Response
from src.server.lib.models import Credentials, Cookies, EmployeeInfo, ShiftInfo, ScheduleInfo, HolidayInfo
from src.server.lib.utils import log, todict, todicts
from src.server.lib.exceptions import CookiesUnavailable
from src.server.lib.db import (
    Account, Employee, Shift, Schedule, Holiday, Settings,
    get_all_accounts, log_in_account, log_in_account_with_cookies, create_account, update_account, delete_account,
    get_all_employees_of_account, create_employee, update_employee, delete_employee,
    get_all_shifts_of_account, create_shift, update_shift, delete_shift,
    get_all_schedules_of_account, create_schedule, update_schedule, delete_schedule,
    get_settings_of_account, toggle_dark_theme, toggle_min_max_work_hours,
    get_all_holidays_of_account, create_holiday, update_holiday, delete_holiday,
    toggle_multi_emps_in_shift, toggle_multi_shifts_one_emp, update_weekend_days, update_max_emps_in_shift
)

# Init
account_router = APIRouter()
employee_router = APIRouter()
shift_router = APIRouter()
schedule_router = APIRouter()
holiday_router = APIRouter()
settings_router = APIRouter()

def endpoint(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            if type(result) in (Account, Employee, Shift, Schedule, Holiday, Settings):
                return todict(result)
            elif type(result) is list:
                try: return todicts(result)
                except: return result
            return result
        except Exception as e:
            return {'error': str(e)}
    return wrapper


def _get_cookies(request: Request) -> Cookies:
    """Returns the username & authentication token stored in the client's cookies."""
    try:
        return Cookies(account_id=int(request.cookies.get('account_id')), token=request.cookies.get('auth_token'))
    except:
        return Cookies(account_id=None, token=request.cookies.get('token'))


def _set_cookie(key: str, value: str, response: Response) -> None:
    """Stores a cookie with a given value."""
    response.set_cookie(
        key=key,
        value=value,
        httponly=True,
        secure=False,
        samesite='strict',
        domain=None,
        path='/'
    )


def _store_cookies(cookies: Cookies, response: Response) -> None:
    """Stores the given username & authentication token as HttpOnly cookies in the client."""
    if not cookies.available(): raise CookiesUnavailable(cookies)
    log(f'Storing cookies: {cookies}', 'auth')
    _set_cookie('account_id', cookies.account_id, response)
    _set_cookie('auth_token', cookies.token, response)


def _clear_cookies(response: Response) -> None:
    """Sets the cookies to None, effectively clearing them."""
    _set_cookie('account_id', None, response)
    _set_cookie('auth_token', None, response)


# Endpoints
## Account
@account_router.get('/accounts')
@endpoint
def read_accounts() -> list[dict] | dict:
    return get_all_accounts()


@account_router.get('/accounts/log_in_account_with_cookies')
@endpoint
def log_in_account_with_cookies_(request: Request) -> dict:
    cookies = _get_cookies(request)
    if cookies.account_id is None: return {'error': 'Account ID is either invalid or not found'}
    elif cookies.token is None: return {'error': 'Token is either invalid or not found'}
    else: return log_in_account_with_cookies(cookies)


@account_router.post('/accounts/login')
@endpoint
def login_account(cred: Credentials, response: Response) -> dict:
    account, token = log_in_account(cred)
    _store_cookies(Cookies(account_id=account.account_id, token=token), response)
    return account


@account_router.get('/accounts/logout')
@endpoint
def logout_account(response: Response) -> dict:
    _clear_cookies(response)
    return {'detail': 'Logged out successfully'}


@account_router.post('/accounts/signup')
@endpoint
def create_new_account(cred: Credentials, response: Response) -> dict:
    account, token = create_account(cred)
    _store_cookies(Cookies(account_id=account.account_id, token=token), response)
    return account


@account_router.patch('/accounts')
@endpoint
def update_existing_account(updates: dict[Literal['username', 'new_password'], str], request: Request) -> dict:
    return update_account(_get_cookies(request), updates)


@account_router.delete('/accounts')
@endpoint
def delete_existing_account(request: Request, response: Response) -> dict:
    delete_account(_get_cookies(request))
    _clear_cookies(response)
    return {'detail': 'Account deleted successfully'}


## Employee
@employee_router.get('/accounts/{account_id}/employees')
@endpoint
def read_employees(account_id: int) -> list[dict] | dict:
    return get_all_employees_of_account(account_id=account_id)


@employee_router.post('/accounts/{account_id}/employees')
@endpoint
def create_new_employee(account_id: int, info: EmployeeInfo) -> dict:
    return create_employee(account_id=account_id, employee_name=info.employee_name, min_work_hours=info.min_work_hours, max_work_hours=info.max_work_hours)


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
    return create_schedule(account_id=account_id, schedule=info.schedule, month=info.month, year=info.year)


@schedule_router.patch('/schedules/{schedule_id}')
@endpoint
def update_existing_schedule(schedule_id: int, updates: dict) -> dict:
    return update_schedule(schedule_id=schedule_id, updates=updates)


@schedule_router.delete('/schedules/{schedule_id}')
@endpoint
def delete_existing_schedule(schedule_id: int) -> dict:
    delete_schedule(schedule_id=schedule_id)
    return {'detail': 'Schedule deleted successfully'}


## Holiday
@holiday_router.get('/accounts/{account_id}/holidays')
@endpoint
def read_holidays(account_id: int) -> list[dict] | dict:
    return get_all_holidays_of_account(account_id=account_id)


@holiday_router.post('/accounts/{account_id}/holidays')
@endpoint
def create_new_holiday(account_id: int, info: HolidayInfo) -> dict:
    return create_holiday(account_id=account_id, holiday_name=info.holiday_name, assigned_to=info.assigned_to, start_date=info.start_date, end_date=info.end_date)


@holiday_router.patch('/holidays/{holiday_id}')
@endpoint
def update_existing_holiday(holiday_id: int, updates: dict) -> dict:
    return update_holiday(holiday_id=holiday_id, updates=updates)


@holiday_router.delete('/holidays/{holiday_id}')
@endpoint
def delete_existing_holiday(holiday_id: int) -> dict:
    delete_holiday(holiday_id=holiday_id)
    return {'detail': 'Holiday deleted successfully'}


## Settings
@settings_router.get('/accounts/{account_id}/settings')
@endpoint
def read_settings(account_id: int) -> dict:
    res = get_settings_of_account(account_id=account_id)
    return res if res is not None else {'detail': res}


@settings_router.get('/accounts/{account_id}/settings/toggle_dark_theme')
@endpoint
def toggle_dark_theme_(account_id: int) -> dict:
    return {'detail': toggle_dark_theme(account_id=account_id)}


@settings_router.get('/accounts/{account_id}/settings/toggle_min_max_work_hours')
@endpoint
def toggle_min_max_work_hours_(account_id: int) -> dict:
    return {'detail': toggle_min_max_work_hours(account_id=account_id)}


@settings_router.get('/accounts/{account_id}/settings/toggle_multi_emps_in_shift')
@endpoint
def toggle_multi_emps_in_shift_(account_id: int) -> dict:
    return {'detail': toggle_multi_emps_in_shift(account_id=account_id)}


@settings_router.get('/accounts/{account_id}/settings/toggle_multi_shifts_one_emp')
@endpoint
def toggle_multi_shifts_one_emp_(account_id: int) -> dict:
    return {'detail': toggle_multi_shifts_one_emp(account_id=account_id)}


@settings_router.patch('/accounts/{account_id}/settings/update_weekend_days')
@endpoint
def update_weekend_days_(account_id: int, info: dict[Literal['weekend_days'], str]) -> dict:
    return {'detail': update_weekend_days(account_id=account_id, weekend_days=info['weekend_days'])}


@settings_router.patch('/accounts/{account_id}/settings/max_emps_in_shift')
@endpoint
def update_max_emps_in_shift_(account_id: int, info: dict[Literal['max_emps_in_shift'], int]) -> dict:
    return {'detail': update_max_emps_in_shift(account_id=account_id, max_emps_in_shift=info['max_emps_in_shift'])}