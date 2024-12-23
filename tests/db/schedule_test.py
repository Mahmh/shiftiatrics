from sqlalchemy import text
import pytest
from src.server.lib.db import Session, create_account, delete_account, create_schedule, delete_schedule, get_all_schedules_of_account, update_schedule
from src.server.lib.models import Credentials
from src.server.lib.exceptions import UsernameTaken, NonExistent
from src.server.lib.utils import parse_schedule

ACCOUNT_ID = 1
SCHEDULE_ID = 1
CRED = Credentials(username='testuser', password='testpass')
SCHEDULE = [[1, 2], [3, 4]]

@pytest.fixture(scope='function', autouse=True)
def setup_and_teardown():
    # Setup: Create a schedule
    try:
        create_account(CRED)
        create_schedule(ACCOUNT_ID, SCHEDULE)
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
    schedule = create_schedule(ACCOUNT_ID, SCHEDULE)
    assert parse_schedule(schedule.schedule) == SCHEDULE


def test_get_all_schedules():
    schedules = get_all_schedules_of_account(ACCOUNT_ID)
    assert len(schedules) == 1
    assert parse_schedule(schedules[0].schedule) == SCHEDULE


def test_update_schedule():
    schedule = create_schedule(ACCOUNT_ID, SCHEDULE)
    updates = {'schedule': [[5, 6], [7, 8]]}
    updated_schedule = update_schedule(schedule.schedule_id, updates)
    assert parse_schedule(updated_schedule.schedule) == updates['schedule']


def test_delete_schedule():
    schedule = create_schedule(ACCOUNT_ID, SCHEDULE)
    delete_schedule(schedule.schedule_id)
    delete_schedule(SCHEDULE_ID)
    schedules = get_all_schedules_of_account(ACCOUNT_ID)
    assert len(schedules) == 0