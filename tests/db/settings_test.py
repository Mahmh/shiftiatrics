from sqlalchemy import text
import pytest
from src.server.lib.constants import LIST_OF_WEEKEND_DAYS
from src.server.lib.models import Credentials
from src.server.lib.exceptions import UsernameTaken, NonExistent
from src.server.lib.db import (
    Session, Settings,
    create_account, delete_account,
    get_settings_of_account, toggle_dark_theme, toggle_min_max_work_hours, 
    toggle_multi_emps_in_shift, toggle_multi_shifts_one_emp, update_weekend_days
)

CRED = Credentials(username='testuser', password='testpass')
ACCOUNT_ID = 1

@pytest.fixture(scope="function", autouse=True)
def setup_and_teardown():
    # Setup: Create the account
    try: create_account(CRED)
    except UsernameTaken: pass
    yield
    # Teardown: Delete the account & reset the account_id serial sequence
    try: delete_account(CRED)
    except NonExistent: pass
    with Session() as session:
        session.execute(text('ALTER SEQUENCE accounts_account_id_seq RESTART WITH 1;'))
        session.commit()


def _assert_all_false(settings: Settings):
    assert isinstance(settings, Settings)
    assert settings.account_id == ACCOUNT_ID
    assert settings.dark_theme_enabled is False
    assert settings.min_max_work_hours_enabled is False
    assert settings.multi_emps_in_shift_enabled is False
    assert settings.multi_shifts_one_emp_enabled is False


def _assert_one_true(setting: str, settings: Settings):
    assert isinstance(settings, Settings)
    assert settings.account_id == ACCOUNT_ID
    assert getattr(settings, setting) is True

    other_settings = {'dark_theme_enabled', 'min_max_work_hours_enabled', 'multi_emps_in_shift_enabled', 'multi_shifts_one_emp_enabled'} - {setting}
    for s in other_settings:
        if s != setting: assert getattr(settings, s) is False


# Tests
def test_no_settings():
    assert get_settings_of_account(ACCOUNT_ID) is None


def test_enable_dark_theme():
    toggle_dark_theme(ACCOUNT_ID)
    settings = get_settings_of_account(ACCOUNT_ID)
    _assert_one_true('dark_theme_enabled', settings)


def test_disable_dark_theme():
    toggle_dark_theme(ACCOUNT_ID)
    toggle_dark_theme(ACCOUNT_ID)
    settings = get_settings_of_account(ACCOUNT_ID)
    _assert_all_false(settings)


def test_enable_min_max_work_hours():
    toggle_min_max_work_hours(ACCOUNT_ID)
    settings = get_settings_of_account(ACCOUNT_ID)
    _assert_one_true('min_max_work_hours_enabled', settings)


def test_disable_min_max_work_hours():
    toggle_min_max_work_hours(ACCOUNT_ID)
    toggle_min_max_work_hours(ACCOUNT_ID)
    settings = get_settings_of_account(ACCOUNT_ID)
    _assert_all_false(settings)


def test_enable_multi_emps_in_shift():
    toggle_multi_emps_in_shift(ACCOUNT_ID)
    settings = get_settings_of_account(ACCOUNT_ID)
    _assert_one_true('multi_emps_in_shift_enabled', settings)


def test_disable_multi_emps_in_shift():
    toggle_multi_emps_in_shift(ACCOUNT_ID)
    toggle_multi_emps_in_shift(ACCOUNT_ID)
    settings = get_settings_of_account(ACCOUNT_ID)
    _assert_all_false(settings)


def test_enable_multi_shifts_one_emp():
    toggle_multi_shifts_one_emp(ACCOUNT_ID)
    settings = get_settings_of_account(ACCOUNT_ID)
    _assert_one_true('multi_shifts_one_emp_enabled', settings)


def test_disable_multi_shifts_one_emp():
    toggle_multi_shifts_one_emp(ACCOUNT_ID)
    toggle_multi_shifts_one_emp(ACCOUNT_ID)
    settings = get_settings_of_account(ACCOUNT_ID)
    _assert_all_false(settings)


def test_update_weekend_days():
    update_weekend_days(ACCOUNT_ID, LIST_OF_WEEKEND_DAYS[1])
    settings = get_settings_of_account(ACCOUNT_ID)
    _assert_all_false(settings)
    assert settings.weekend_days == LIST_OF_WEEKEND_DAYS[1]