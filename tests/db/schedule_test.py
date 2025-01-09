from sqlalchemy import text
import pytest
from src.server.lib.db import reset_serial_sequence, create_account, delete_account, create_schedule, delete_schedule, get_all_schedules_of_account, update_schedule
from src.server.lib.models import Credentials
from src.server.lib.exceptions import UsernameTaken, NonExistent

CRED = Credentials(username='testuser', password='testpass')
SCHEDULE_DATA = {'schedule': [[1, 2], [3, 4]], 'month': 11, 'year': 2024}

@pytest.fixture(scope='function', autouse=True)
def setup_and_teardown():
    # Setup: Create a schedule
    try:
        account_id = create_account(CRED).account_id
        schedule_id = create_schedule(account_id, **SCHEDULE_DATA).schedule_id
        yield account_id, schedule_id
    except UsernameTaken:
        yield 1, 1
        pass
    # Teardown: Delete the schedule & reset the schedule_id serial sequence
    delete_account(CRED)
    try: delete_schedule(schedule_id)
    except NonExistent: pass
    except UnboundLocalError: delete_schedule(1)
    reset_serial_sequence()


# Tests
def test_create_schedule(setup_and_teardown):
    account_id, _ = setup_and_teardown
    schedule = create_schedule(account_id, **SCHEDULE_DATA)
    assert schedule.schedule == SCHEDULE_DATA['schedule']


def test_get_all_schedules(setup_and_teardown):
    account_id, _ = setup_and_teardown
    schedules = get_all_schedules_of_account(account_id)
    assert len(schedules) == 1
    assert schedules[0].schedule == SCHEDULE_DATA['schedule']


def test_update_schedule(setup_and_teardown):
    account_id, _ = setup_and_teardown
    schedule = create_schedule(account_id, **SCHEDULE_DATA)
    updates = {'schedule': [[5, 6], [7, 8]]}
    updated_schedule = update_schedule(schedule.schedule_id, updates)
    assert updated_schedule.schedule == updates['schedule']


def test_delete_schedule(setup_and_teardown):
    account_id, schedule_id = setup_and_teardown
    schedule = create_schedule(account_id, **SCHEDULE_DATA)
    delete_schedule(schedule.schedule_id)
    delete_schedule(schedule_id)
    schedules = get_all_schedules_of_account(account_id)
    assert len(schedules) == 0