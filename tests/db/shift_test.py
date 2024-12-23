from sqlalchemy import text
import pytest
from src.server.lib.db import Session, create_account, delete_account, create_shift, delete_shift, get_all_shifts_of_account, update_shift
from src.server.lib.models import Credentials
from src.server.lib.exceptions import UsernameTaken, NonExistent
from src.server.lib.utils import parse_time

ACCOUNT_ID = 1
SHIFT_ID = 1
CRED = Credentials(username='testuser', password='testpass')
SHIFT_DETAILS = {'shift_name': 'Morning Shift', 'start_time': '08:00', 'end_time': '16:00'}

@pytest.fixture(scope="function", autouse=True)
def setup_and_teardown():
    # Setup: Create a shift
    try:
        create_account(CRED)
        create_shift(ACCOUNT_ID, **SHIFT_DETAILS)
    except UsernameTaken: pass
    yield  # Run the test
    # Teardown: Delete the shift & reset the shift_id serial sequence
    try:
        delete_account(CRED)
        delete_shift(SHIFT_ID)
    except NonExistent: pass
    with Session() as session:
        session.execute(text('ALTER SEQUENCE accounts_account_id_seq RESTART WITH 1;'))
        session.execute(text('ALTER SEQUENCE shifts_shift_id_seq RESTART WITH 1;'))
        session.commit()


# Tests
def test_create_shift():
    shift = create_shift(ACCOUNT_ID, **SHIFT_DETAILS)
    assert shift.shift_name == SHIFT_DETAILS['shift_name']
    assert shift.start_time == parse_time(SHIFT_DETAILS['start_time'])
    assert shift.end_time == parse_time(SHIFT_DETAILS['end_time'])


def test_get_all_shifts():
    shifts = get_all_shifts_of_account(ACCOUNT_ID)
    assert len(shifts) == 1
    assert shifts[0].shift_name == SHIFT_DETAILS['shift_name']


def test_update_shift():
    shift = create_shift(ACCOUNT_ID, **SHIFT_DETAILS)
    updates = {'shift_name': 'Evening Shift', 'start_time': '16:00', 'end_time': '00:00'}
    updated_shift = update_shift(shift.shift_id, updates)
    assert updated_shift.shift_name == 'Evening Shift'
    assert updated_shift.start_time == parse_time('16:00')
    assert updated_shift.end_time == parse_time('00:00')


def test_delete_shift():
    shift = create_shift(ACCOUNT_ID, **SHIFT_DETAILS)
    delete_shift(shift.shift_id)
    delete_shift(SHIFT_ID)
    shifts = get_all_shifts_of_account(ACCOUNT_ID)
    assert len(shifts) == 0