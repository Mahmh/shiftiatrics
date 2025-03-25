from src.server.lib.utils import parse_date
from src.server.db import (
    create_account,
    create_employee, delete_employee,
    create_holiday, delete_holiday, get_all_holidays_of_account, update_holiday
)
from tests.utils import ctxtest, CRED

# Init
HOLIDAY = {'holiday_name': 'Holiday', 'assigned_to': [1, 2], 'start_date': '2023-12-25', 'end_date': '2023-12-26'}

@ctxtest()
def setup_and_teardown():
    account_id = create_account(CRED)[0].account_id
    create_employee(account_id, 'testemp1')
    create_employee(account_id, 'testemp2')
    holiday_id = create_holiday(account_id, **HOLIDAY).holiday_id
    yield account_id, holiday_id


# Tests
def test_create_holiday(setup_and_teardown):
    account_id, _ = setup_and_teardown
    holiday = create_holiday(account_id, **HOLIDAY)
    assert holiday.assigned_to == HOLIDAY['assigned_to']
    assert holiday.start_date == parse_date(HOLIDAY['start_date'])
    assert holiday.end_date == parse_date(HOLIDAY['end_date'])


def test_get_all_holidays(setup_and_teardown):
    account_id, _ = setup_and_teardown
    holidays = get_all_holidays_of_account(account_id)
    assert len(holidays) == 1
    assert holidays[0].assigned_to == HOLIDAY['assigned_to']


def test_update_holiday(setup_and_teardown):
    account_id, _ = setup_and_teardown
    holiday = create_holiday(account_id, **HOLIDAY)
    updates = {'holiday_name': 'NewHoliday', 'assigned_to': [2], 'start_date': '2023-12-31', 'end_date': '2024-01-01'}
    updated_holiday = update_holiday(holiday.holiday_id, updates)
    assert updated_holiday.holiday_name == updates['holiday_name']
    assert updated_holiday.assigned_to == updates['assigned_to']
    assert updated_holiday.start_date == parse_date(updates['start_date'])
    assert updated_holiday.end_date == parse_date(updates['end_date'])


def test_delete_holiday(setup_and_teardown):
    account_id, holiday_id = setup_and_teardown
    holiday = create_holiday(account_id, **HOLIDAY)
    delete_holiday(holiday.holiday_id)
    delete_holiday(holiday_id)
    holidays = get_all_holidays_of_account(account_id)
    assert len(holidays) == 0


def test_removed_employee_not_in_holiday(setup_and_teardown):
    account_id, _ = setup_and_teardown
    holiday = create_holiday(account_id, **HOLIDAY)
    delete_employee(1)
    holidays = get_all_holidays_of_account(account_id)
    for holiday in holidays:
        assert 1 not in holiday.assigned_to


def test_holiday_deleted_if_only_employee_deleted(setup_and_teardown):
    account_id, _ = setup_and_teardown
    delete_employee(1)
    delete_employee(2)
    holidays = get_all_holidays_of_account(account_id)
    assert len(holidays) == 0