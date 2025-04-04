from src.server.db import create_account, create_schedule, delete_schedule, get_schedules, update_schedule
from tests.utils import ctxtest, CRED

# Init
SCHEDULE = {'schedule': [[1, 2], [3, 4]], 'month': 11, 'year': 2024}

@ctxtest()
def setup_and_teardown():
    account_id = create_account(CRED)[0].account_id
    schedule_id = create_schedule(account_id, **SCHEDULE).schedule_id
    yield account_id, schedule_id


# Tests
def test_create_schedule(setup_and_teardown):
    account_id, _ = setup_and_teardown
    schedule = create_schedule(account_id, **SCHEDULE)
    assert schedule.schedule == SCHEDULE['schedule']


def test_get_schedules(setup_and_teardown):
    account_id, _ = setup_and_teardown
    schedules = get_schedules(account_id)
    assert len(schedules) == 1
    assert schedules[0].schedule == SCHEDULE['schedule']


def test_update_schedule(setup_and_teardown):
    _, schedule_id = setup_and_teardown
    updates = {'schedule': [[5, 6], [7, 8]]}
    updated_schedule = update_schedule(schedule_id, updates)
    assert updated_schedule.schedule == updates['schedule']


def test_delete_schedule(setup_and_teardown):
    account_id, schedule_id = setup_and_teardown
    delete_schedule(schedule_id)
    schedules = get_schedules(account_id)
    assert len(schedules) == 0