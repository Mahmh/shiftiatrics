from fastapi import APIRouter, Request, Response, Body
from src.server.rate_limit import limiter
from src.server.lib.constants import DEFAULT_RATE_LIMIT
from src.server.lib.models import Credentials, Cookies, HolidayInfo
from src.server.lib.api import endpoint, get_cookies, store_cookies, clear_cookies, return_account_and_sub, check_legal_agree
from src.server.lib.types import SettingValue
from src.server.db import (
    create_account, change_email, change_password, request_delete_account, get_account_data,
    get_teams, get_employees, get_shifts, get_schedules, delete_schedule, get_settings, 
    update_setting, get_holidays, create_holiday, update_holiday, delete_holiday, create_sub
)

# Init
account_router = APIRouter(prefix='/accounts')
team_router = APIRouter(prefix='/teams')
employee_router = APIRouter(prefix='/employees')
shift_router = APIRouter(prefix='/shifts')
schedule_router = APIRouter(prefix='/schedules')
holiday_router = APIRouter(prefix='/holidays')
settings_router = APIRouter(prefix='/settings')
sub_router = APIRouter(prefix='/sub')


# Endpoints
## Account
@account_router.post('/signup')
@limiter.limit('10/minute')
@endpoint(auth=False)
async def create_new_account(cred: Credentials, response: Response, request: Request, legal_agree: bool = Body(..., embed=True)) -> dict:
    check_legal_agree(legal_agree)
    account, token = create_account(cred)
    store_cookies(Cookies(account_id=account.account_id, token=token), response)
    return return_account_and_sub(account)


@account_router.patch('/email')
@limiter.limit(DEFAULT_RATE_LIMIT)
@endpoint()
async def change_email_endpoint(request: Request, email: str = Body(..., embed=True)) -> dict:
    return change_email(get_cookies(request), email)


@account_router.patch('/password')
@limiter.limit(DEFAULT_RATE_LIMIT)
@endpoint()
async def change_password_endpoint(request: Request, current_password: str = Body(None, embed=True), new_password: str = Body(..., embed=True)) -> dict:
    return change_password(get_cookies(request), new_password, current_password)


@account_router.patch('/password_upon_signup')
@limiter.limit(DEFAULT_RATE_LIMIT)
@endpoint()
async def change_password_upon_signup(request: Request, new_password: str = Body(..., embed=True), legal_agree: bool = Body(..., embed=True)) -> dict:
    check_legal_agree(legal_agree)
    return change_password(get_cookies(request), new_password, require_current=False)


@account_router.delete('')
@limiter.limit(DEFAULT_RATE_LIMIT)
@endpoint()
async def delete_existing_account(request: Request, response: Response) -> dict:
    await request_delete_account(get_cookies(request))
    clear_cookies(response)
    return {'detail': 'Account deletion request sent'}


@account_router.get('/data')
@limiter.limit(DEFAULT_RATE_LIMIT)
@endpoint()
async def get_all_data_of_account(request: Request) -> dict:
    return get_account_data(get_cookies(request))



## Team
@team_router.get('/{account_id}')
@limiter.limit(DEFAULT_RATE_LIMIT)
@endpoint()
async def read_teams(account_id: int, request: Request) -> list[dict] | dict:
    return get_teams(account_id)



## Employee
@employee_router.get('/{account_id}')
@limiter.limit(DEFAULT_RATE_LIMIT)
@endpoint()
async def read_employees(account_id: int, request: Request) -> list[dict] | dict:
    return get_employees(account_id)



## Shift
@shift_router.get('/{account_id}')
@limiter.limit(DEFAULT_RATE_LIMIT)
@endpoint()
async def read_shifts(account_id: int, request: Request) -> list[dict] | dict:
    return get_shifts(account_id)



## Schedule
@schedule_router.get('/{account_id}')
@limiter.limit(DEFAULT_RATE_LIMIT)
@endpoint()
async def read_schedules(account_id: int, request: Request) -> list[dict] | dict:
    return get_schedules(account_id)


@schedule_router.delete('/{schedule_id}')
@limiter.limit(DEFAULT_RATE_LIMIT)
@endpoint()
async def delete_existing_schedule(schedule_id: int, request: Request) -> dict:
    delete_schedule(schedule_id)
    return {'detail': 'Schedule deleted successfully'}



## Holiday
@holiday_router.get('/{account_id}')
@limiter.limit(DEFAULT_RATE_LIMIT)
@endpoint()
async def read_holidays(account_id: int, request: Request) -> list[dict] | dict:
    return get_holidays(account_id)


@holiday_router.post('/{account_id}')
@limiter.limit(DEFAULT_RATE_LIMIT)
@endpoint()
async def create_new_holiday(account_id: int, info: HolidayInfo, request: Request) -> dict:
    return create_holiday(account_id, info.holiday_name, info.assigned_to, info.start_date, info.end_date)


@holiday_router.patch('/{holiday_id}')
@limiter.limit(DEFAULT_RATE_LIMIT)
@endpoint()
async def update_existing_holiday(holiday_id: int, updates: dict, request: Request) -> dict:
    return update_holiday(holiday_id, updates)


@holiday_router.delete('/{holiday_id}')
@limiter.limit(DEFAULT_RATE_LIMIT)
@endpoint()
async def delete_existing_holiday(holiday_id: int, request: Request) -> dict:
    delete_holiday(holiday_id)
    return {'detail': 'Holiday deleted successfully'}



## Settings
@settings_router.get('/{account_id}')
@limiter.limit(DEFAULT_RATE_LIMIT)
@endpoint()
async def read_settings(account_id: int, request: Request) -> dict:
    return get_settings(account_id)


@settings_router.patch('/{account_id}')
@limiter.limit(DEFAULT_RATE_LIMIT)
@endpoint()
async def update_one_setting(account_id: int, request: Request, setting: str = Body(..., embed=True), new_value: SettingValue = Body(..., embed=True)) -> dict:
    return update_setting(account_id, setting, new_value)



## Subscription
@sub_router.post('/create/{account_id}')
@limiter.limit('10/minute')
@endpoint()
async def create_subscription(account_id: int, request: Request, chkout_session_id: str = Body(..., embed=True)) -> dict:
    return create_sub(account_id, chkout_session_id)[1]