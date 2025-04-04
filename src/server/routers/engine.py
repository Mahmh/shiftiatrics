from fastapi import APIRouter, Request
from src.server.engine import Engine
from src.server.rate_limit import limiter
from src.server.lib.constants import DEFAULT_RATE_LIMIT
from src.server.lib.models import ScheduleType
from src.server.lib.api import endpoint
from src.server.db import get_employees, get_shifts, get_schedules, get_holidays

engine_router = APIRouter(prefix='/engine')

@engine_router.get('/generate_schedule')
@limiter.limit(DEFAULT_RATE_LIMIT)
@endpoint()
async def generate_schedule(account_id: int, num_days: int, year: int, month: int, request: Request) -> ScheduleType | dict[str, str]:
    # month is in range [0, 11]
    employees = get_employees(account_id)
    shifts = get_shifts(account_id)
    holidays = get_holidays(account_id)
    if not employees: raise ValueError('No employees registered by the account.')
    if not shifts: raise ValueError('No shifts registered by the account.')
    return Engine(account_id).generate(employees, shifts, holidays, num_days, year, month)


@engine_router.get('/get_shift_counts_of_employees')
@limiter.limit(DEFAULT_RATE_LIMIT)
@endpoint()
async def get_shift_counts_of_employees(account_id: int, year: int, month: int, request: Request) -> dict[int, int] | dict[str, str]:
    # Fetch the schedule for the given account, year, and month
    schedule_data = get_schedules(account_id, year=year, month=month)
    if not schedule_data: raise ValueError("No schedule found for the given account, year, and month.")
    schedule = schedule_data[0].schedule  # Extract the schedule
    return Engine(account_id).get_shift_counts_of_employees(schedule)


@engine_router.get('/get_work_hours_of_employees')
@limiter.limit(DEFAULT_RATE_LIMIT)
@endpoint()
async def get_work_hours_of_employees(account_id: int, year: int, month: int, request: Request) -> dict[int, int] | dict[str, str]:
    # Fetch the schedule and shifts for the given account, year, and month
    schedule = get_schedules(account_id, year=year, month=month)[0].schedule
    shifts = get_shifts(account_id)  # list of unique shifts per day
    if not schedule: raise ValueError("No schedule found for the given account, year, and month.")
    if not shifts: raise ValueError("No shifts found for the given account, year, and month.")
    return Engine(account_id).get_work_hours_of_employees(schedule, shifts)