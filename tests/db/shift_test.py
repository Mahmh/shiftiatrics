import pytest
from src.server.lib.utils import parse_time
from src.server.db import create_account, create_shift, delete_shift, get_all_shifts_of_account, update_shift
from tests.utils import ctxtest, CRED

# Init
SHIFT = {'shift_name': 'Morning', 'start_time': '08:00', 'end_time': '16:00'}
SHIFT2 = {'shift_name': 'Evening', 'start_time': '16:00', 'end_time': '00:00'}
SHIFT3 = {'shift_name': 'Night', 'start_time': '00:00', 'end_time': '08:00'}

@ctxtest()
def setup_and_teardown():
    account_id = create_account(CRED)[0].account_id
    shift_id = create_shift(account_id, **SHIFT).shift_id
    yield account_id, shift_id


# Tests
def test_create_shift(setup_and_teardown):
    account_id, _ = setup_and_teardown
    shift = create_shift(account_id, **SHIFT2)
    assert shift.shift_name == SHIFT2['shift_name']
    assert shift.start_time == parse_time(SHIFT2['start_time'])
    assert shift.end_time == parse_time(SHIFT2['end_time'])


def test_get_all_shifts(setup_and_teardown):
    account_id, _ = setup_and_teardown
    shifts = get_all_shifts_of_account(account_id)
    assert len(shifts) == 1
    assert shifts[0].shift_name == SHIFT['shift_name']


def test_update_shift(setup_and_teardown):
    account_id, _ = setup_and_teardown
    shift = create_shift(account_id, **SHIFT2)
    updates = {'shift_name': 'New Shift', 'start_time': '04:00', 'end_time': '08:00'}
    updated_shift = update_shift(shift.shift_id, updates)
    assert updated_shift.shift_name == updates['shift_name']
    assert updated_shift.start_time == parse_time(updates['start_time'])
    assert updated_shift.end_time == parse_time(updates['end_time'])


def test_delete_shift(setup_and_teardown):
    account_id, shift_id = setup_and_teardown
    shift = create_shift(account_id, **SHIFT2)
    delete_shift(shift.shift_id)
    delete_shift(shift_id)
    shifts = get_all_shifts_of_account(account_id)
    assert len(shifts) == 0


def test_exceed_max_num_shifts_in_free_tier(setup_and_teardown):
    account_id, _ = setup_and_teardown
    create_shift(account_id, **SHIFT2)
    with pytest.raises(ValueError, match='maximum number of shift types'):
        create_shift(account_id, **SHIFT3)