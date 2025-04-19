from fastapi import APIRouter, Request
from src.server.engine import Engine
from src.server.rate_limit import limiter
from src.server.lib.constants import DEFAULT_RATE_LIMIT
from src.server.lib.utils import todicts, log
from src.server.lib.api import endpoint
from src.server.lib.exceptions import NotFoundForEngineInput
from src.server.db import get_employees_of_team, get_teams, get_shifts, get_schedules, get_holidays, get_schedules, create_schedule, update_schedule

engine_router = APIRouter(prefix='/engine')

@engine_router.get('/generate_schedule')
@limiter.limit(DEFAULT_RATE_LIMIT)
@endpoint()
async def generate_schedule(account_id: int, num_days: int, year: int, month: int, request: Request) -> list[dict] | dict[str, str]:
    # month is in range [0, 11]
    teams = get_teams(account_id)
    result = []

    for team in teams:
        team_id = team.team_id
        employees = get_employees_of_team(team_id)
        shifts = get_shifts(account_id)
        holidays = get_holidays(account_id)
        if not employees: raise ValueError('No employees registered by the account.')
        if not shifts: raise ValueError('No shifts registered by the account.')

        engine = Engine(account_id, team_id)
        schedule_of_ids = engine.generate(employees, shifts, holidays, num_days, year, month)
        existing_schedule = get_schedules(account_id, year=year, month=month, team_id=team_id)

        if existing_schedule:
            schedule = update_schedule(existing_schedule[0].schedule_id, {'schedule': schedule_of_ids})
        else:
            schedule = create_schedule(account_id, schedule_of_ids, team_id, year, month)

        result.append(schedule)

    return todicts(result)


@engine_router.get('/get_shift_counts_of_employees')
@limiter.limit(DEFAULT_RATE_LIMIT)
@endpoint()
async def get_shift_counts_of_employees(account_id: int, team_id: int, year: int, month: int, request: Request) -> dict[int, int] | dict[str, str]:
    # Fetch the schedule for the given account, year, and month
    schedule_data = get_schedules(account_id, year=year, month=month, team_id=team_id)
    if not schedule_data: raise NotFoundForEngineInput('schedule', account_id, team_id, year, month)
    schedule = schedule_data[0].schedule  # Extract the schedule
    return Engine(account_id, team_id).get_shift_counts_of_employees(schedule)


@engine_router.get('/get_work_hours_of_employees')
@limiter.limit(DEFAULT_RATE_LIMIT)
@endpoint()
async def get_work_hours_of_employees(account_id: int, team_id: int, year: int, month: int, request: Request) -> dict[int, int] | dict[str, str]:
    # Fetch the schedule and shifts for the given account, year, and month
    schedule = get_schedules(account_id, year=year, month=month, team_id=team_id)[0].schedule
    shifts = get_shifts(account_id)  # list of unique shifts per day
    if not schedule: raise NotFoundForEngineInput('schedule', account_id, team_id, year, month)
    if not shifts: raise NotFoundForEngineInput('shift', account_id, team_id, year, month)
    return Engine(account_id, team_id).get_work_hours_of_employees(schedule, shifts)