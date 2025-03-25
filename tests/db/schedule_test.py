import pytest
from src.server.lib.constants import FREE_TIER_DETAILS
from src.server.db import (
    Session,
    create_account,
    create_schedule,
    delete_schedule,
    get_all_schedules_of_account,
    update_schedule,
    get_num_schedule_requests,
    _check_schedule_requests,
)
from tests.utils import ctxtest, CRED

# Init
SCHEDULE = {'schedule': [[1, 2], [3, 4]], 'month': 11, 'year': 2024}

@ctxtest()
def setup_and_teardown():
    account_id = create_account(CRED)[0].account_id
    schedule_id = create_schedule(account_id, **SCHEDULE).schedule_id
    yield account_id, schedule_id


def _check_valid_schedule_requests(account_id: int):
    with Session() as session:
        _check_schedule_requests(account_id, session=session)


# Tests
def test_create_schedule(setup_and_teardown):
    account_id, _ = setup_and_teardown
    schedule = create_schedule(account_id, **SCHEDULE)
    _check_valid_schedule_requests(account_id)
    assert get_num_schedule_requests(account_id) == 2
    assert schedule.schedule == SCHEDULE['schedule']


def test_get_all_schedules(setup_and_teardown):
    account_id, _ = setup_and_teardown
    schedules = get_all_schedules_of_account(account_id)
    assert get_num_schedule_requests(account_id) == 1
    assert len(schedules) == 1
    assert schedules[0].schedule == SCHEDULE['schedule']


def test_update_schedule(setup_and_teardown):
    account_id, schedule_id = setup_and_teardown
    updates = {'schedule': [[5, 6], [7, 8]]}
    updated_schedule = update_schedule(schedule_id, updates)
    _check_valid_schedule_requests(account_id)
    assert get_num_schedule_requests(account_id) == 2
    assert updated_schedule.schedule == updates['schedule']


def test_delete_schedule(setup_and_teardown):
    account_id, schedule_id = setup_and_teardown
    delete_schedule(schedule_id)
    schedules = get_all_schedules_of_account(account_id)
    _check_valid_schedule_requests(account_id)
    assert get_num_schedule_requests(account_id) == 2
    assert len(schedules) == 0


def test_invalid_schedule_requests_in_free_tier(setup_and_teardown):
    account_id, _ = setup_and_teardown
    with pytest.raises(ValueError):
        for i in range(1, FREE_TIER_DETAILS.max_num_schedule_requests):
            schedule_id = create_schedule(account_id, **SCHEDULE).schedule_id
            update_schedule(schedule_id, {'schedule': SCHEDULE['schedule'] if i%2 == 0 else [[5, 6], [7, 8]]})
            delete_schedule(schedule_id)
            assert get_num_schedule_requests(account_id) == 3*i + 1
        _check_valid_schedule_requests(account_id)