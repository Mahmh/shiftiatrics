from sqlalchemy import text
import pytest
from src.server.lib.db import Session, create_account, delete_account, create_schedule, delete_schedule, get_all_schedules_of_account, update_schedule
from src.server.lib.models import Credentials
from src.server.lib.exceptions import UsernameTaken, NonExistent

ACCOUNT_ID = 1
SCHEDULE_ID = 1
CRED = Credentials(username='testuser', password='testpass')
SCHEDULE_DATA = {'schedule': [[1, 2], [3, 4]], 'month': 11, 'year': 2024}

@pytest.fixture(scope='function', autouse=True)
def setup_and_teardown():
    # Setup: Create a schedule
    try:
        create_account(CRED)
        create_schedule(ACCOUNT_ID, **SCHEDULE_DATA)
    except UsernameTaken: pass
    yield  # Run the test
    # Teardown: Delete the schedule & reset the schedule_id serial sequence
    try:
        delete_account(CRED)
        delete_schedule(SCHEDULE_ID)
    except NonExistent: pass
    with Session() as session:
        session.execute(text('ALTER SEQUENCE accounts_account_id_seq RESTART WITH 1;'))
        session.execute(text('ALTER SEQUENCE schedules_schedule_id_seq RESTART WITH 1;'))
        session.commit()


# Tests
def test_create_schedule():
    schedule = create_schedule(ACCOUNT_ID, **SCHEDULE_DATA)
    assert schedule.schedule == SCHEDULE_DATA['schedule']


def test_get_all_schedules():
    schedules = get_all_schedules_of_account(ACCOUNT_ID)
    assert len(schedules) == 1
    assert schedules[0].schedule == SCHEDULE_DATA['schedule']


def test_update_schedule():
    schedule = create_schedule(ACCOUNT_ID, **SCHEDULE_DATA)
    updates = {'schedule': [[5, 6], [7, 8]]}
    updated_schedule = update_schedule(schedule.schedule_id, updates)
    assert updated_schedule.schedule == updates['schedule']


def test_delete_schedule():
    schedule = create_schedule(ACCOUNT_ID, **SCHEDULE_DATA)
    delete_schedule(schedule.schedule_id)
    delete_schedule(SCHEDULE_ID)
    schedules = get_all_schedules_of_account(ACCOUNT_ID)
    assert len(schedules) == 0