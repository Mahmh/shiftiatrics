from src.server.db import create_account, create_schedule, delete_schedule, get_all_schedules_of_account, update_schedule
from tests.utils import ctxtest, CRED, SUB_INFO

# Init
SCHEDULE = {'schedule': [[1, 2], [3, 4]], 'month': 11, 'year': 2024}

@ctxtest()
def setup_and_teardown():
    account_id = create_account(CRED, SUB_INFO)[0].account_id
    schedule_id = create_schedule(account_id, **SCHEDULE).schedule_id
    yield account_id, schedule_id


# Tests
def test_create_schedule(setup_and_teardown):
    account_id, _ = setup_and_teardown
    schedule = create_schedule(account_id, **SCHEDULE)
    assert schedule.schedule == SCHEDULE['schedule']


def test_get_all_schedules(setup_and_teardown):
    account_id, _ = setup_and_teardown
    schedules = get_all_schedules_of_account(account_id)
    assert len(schedules) == 1
    assert schedules[0].schedule == SCHEDULE['schedule']


def test_update_schedule(setup_and_teardown):
    account_id, _ = setup_and_teardown
    schedule = create_schedule(account_id, **SCHEDULE)
    updates = {'schedule': [[5, 6], [7, 8]]}
    updated_schedule = update_schedule(schedule.schedule_id, updates)
    assert updated_schedule.schedule == updates['schedule']


def test_delete_schedule(setup_and_teardown):
    account_id, schedule_id = setup_and_teardown
    schedule = create_schedule(account_id, **SCHEDULE)
    delete_schedule(schedule.schedule_id)
    delete_schedule(schedule_id)
    schedules = get_all_schedules_of_account(account_id)
    assert len(schedules) == 0