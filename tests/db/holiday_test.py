import pytest
from src.server.lib.db import (
    reset_serial_sequence, 
    create_account, delete_account,
    create_employee, delete_employee,
    create_holiday, delete_holiday, get_all_holidays_of_account, update_holiday
)
from src.server.lib.models import Credentials
from src.server.lib.exceptions import UsernameTaken, NonExistent
from src.server.lib.utils import parse_date

ACCOUNT_ID = HOLIDAY_ID = 1
CRED = Credentials(username='testuser', password='testpass')
EMPLOYEE_DETAILS = {'employee_name': 'testemp'}
HOLIDAY_DETAILS = {'holiday_name': 'Holiday', 'assigned_to': [1, 2], 'start_date': '2023-12-25', 'end_date': '2023-12-26'}

@pytest.fixture(scope='function', autouse=True)
def setup_and_teardown():
    # Setup: Create a holiday
    try:
        create_account(CRED)
        create_employee(1, 'testemp1')
        create_employee(1, 'testemp2')
        create_holiday(ACCOUNT_ID, **HOLIDAY_DETAILS)
    except UsernameTaken: pass
    yield  # Run the test
    # Teardown: Delete the holiday & reset the holiday_id serial sequence
    try:
        delete_account(CRED)
        delete_employee(1)
        delete_employee(1, 'testemp2')
        delete_holiday(HOLIDAY_ID)
    except NonExistent: pass
    reset_serial_sequence()


# Tests
def test_create_holiday():
    holiday = create_holiday(ACCOUNT_ID, **HOLIDAY_DETAILS)
    assert holiday.assigned_to == HOLIDAY_DETAILS['assigned_to']
    assert holiday.start_date == parse_date(HOLIDAY_DETAILS['start_date'])
    assert holiday.end_date == parse_date(HOLIDAY_DETAILS['end_date'])


def test_get_all_holidays():
    holidays = get_all_holidays_of_account(ACCOUNT_ID)
    assert len(holidays) == 1
    assert holidays[0].assigned_to == HOLIDAY_DETAILS['assigned_to']


def test_update_holiday():
    holiday = create_holiday(ACCOUNT_ID, **HOLIDAY_DETAILS)
    updates = {'holiday_name': 'NewHoliday', 'assigned_to': [2], 'start_date': '2023-12-31', 'end_date': '2024-01-01'}
    updated_holiday = update_holiday(holiday.holiday_id, updates)
    assert updated_holiday.holiday_name == updates['holiday_name']
    assert updated_holiday.assigned_to == updates['assigned_to']
    assert updated_holiday.start_date == parse_date(updates['start_date'])
    assert updated_holiday.end_date == parse_date(updates['end_date'])


def test_delete_holiday():
    holiday = create_holiday(ACCOUNT_ID, **HOLIDAY_DETAILS)
    delete_holiday(holiday.holiday_id)
    delete_holiday(HOLIDAY_ID)
    holidays = get_all_holidays_of_account(ACCOUNT_ID)
    assert len(holidays) == 0


def test_removed_employee_not_in_holiday():
    holiday = create_holiday(ACCOUNT_ID, **HOLIDAY_DETAILS)
    delete_employee(1)
    holidays = get_all_holidays_of_account(ACCOUNT_ID)
    for holiday in holidays:
        assert 1 not in holiday.assigned_to


def test_holiday_deleted_if_only_employee_deleted():
    delete_employee(1)
    delete_employee(2)
    holidays = get_all_holidays_of_account(ACCOUNT_ID)
    assert len(holidays) == 0