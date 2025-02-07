import pytest
from src.server.lib.constants import LIST_OF_WEEKEND_DAYS
from src.server.lib.models import Credentials
from src.server.lib.db import (
    Settings, create_account,
    get_settings_of_account, toggle_dark_theme, toggle_min_max_work_hours, 
    toggle_multi_emps_in_shift, toggle_multi_shifts_one_emp, update_weekend_days, update_max_emps_in_shift
)
from tests.utils import ctxtest

# Init
CRED = Credentials(email='testuser@gmail.com', password='testpass')
ACCOUNT_ID = 1

@ctxtest()
def setup_and_teardown():
    create_account(CRED)
    yield


def _assert_all_default(settings: Settings, all_false: bool = False):
    assert isinstance(settings, Settings)
    assert settings.account_id == ACCOUNT_ID
    assert settings.dark_theme_enabled is False
    assert settings.min_max_work_hours_enabled is (True if not all_false else False)
    assert settings.multi_emps_in_shift_enabled is False
    assert settings.multi_shifts_one_emp_enabled is False


def _assert_one_true(setting: str, settings: Settings):
    assert isinstance(settings, Settings)
    assert settings.account_id == ACCOUNT_ID

    all_settings = {setting, 'dark_theme_enabled', 'min_max_work_hours_enabled', 'multi_emps_in_shift_enabled', 'multi_shifts_one_emp_enabled'}
    for s in all_settings:
        assert getattr(settings, s) is (True if s in {setting, 'min_max_work_hours_enabled'} else False)


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
    _assert_all_default(settings)


def test_enable_min_max_work_hours():
    toggle_min_max_work_hours(ACCOUNT_ID)
    toggle_min_max_work_hours(ACCOUNT_ID)
    settings = get_settings_of_account(ACCOUNT_ID)
    _assert_one_true('min_max_work_hours_enabled', settings)


def test_disable_min_max_work_hours():
    toggle_min_max_work_hours(ACCOUNT_ID)
    settings = get_settings_of_account(ACCOUNT_ID)
    _assert_all_default(settings, all_false=True)


def test_enable_multi_emps_in_shift():
    toggle_multi_emps_in_shift(ACCOUNT_ID)
    settings = get_settings_of_account(ACCOUNT_ID)
    _assert_one_true('multi_emps_in_shift_enabled', settings)


def test_disable_multi_emps_in_shift():
    toggle_multi_emps_in_shift(ACCOUNT_ID)
    toggle_multi_emps_in_shift(ACCOUNT_ID)
    settings = get_settings_of_account(ACCOUNT_ID)
    _assert_all_default(settings)


def test_enable_multi_shifts_one_emp():
    toggle_multi_shifts_one_emp(ACCOUNT_ID)
    settings = get_settings_of_account(ACCOUNT_ID)
    _assert_one_true('multi_shifts_one_emp_enabled', settings)


def test_disable_multi_shifts_one_emp():
    toggle_multi_shifts_one_emp(ACCOUNT_ID)
    toggle_multi_shifts_one_emp(ACCOUNT_ID)
    settings = get_settings_of_account(ACCOUNT_ID)
    _assert_all_default(settings)


def test_update_weekend_days():
    update_weekend_days(ACCOUNT_ID, LIST_OF_WEEKEND_DAYS[1])
    settings = get_settings_of_account(ACCOUNT_ID)
    _assert_all_default(settings)
    assert settings.weekend_days == LIST_OF_WEEKEND_DAYS[1]


def test_update_max_emps_in_shift():
    toggle_multi_emps_in_shift(ACCOUNT_ID)
    update_max_emps_in_shift(ACCOUNT_ID, 5)
    settings = get_settings_of_account(ACCOUNT_ID)
    _assert_one_true('multi_emps_in_shift_enabled', settings)
    assert settings.max_emps_in_shift == 5


def test_update_max_emps_in_shift_without_enabling_multi_emps():
    with pytest.raises(ValueError, match='multi_emps_in_shift_enabled must be True first before updating max_emps_in_shift'):
        update_max_emps_in_shift(ACCOUNT_ID, 5)


def test_update_max_emps_in_shift_invalid_value():
    toggle_multi_emps_in_shift(ACCOUNT_ID)
    with pytest.raises(ValueError, match='max_emps_in_shift must be in the range \[1, 10\]'):
        update_max_emps_in_shift(ACCOUNT_ID, 0)
    with pytest.raises(ValueError, match='max_emps_in_shift must be in the range \[1, 10\]'):
        update_max_emps_in_shift(ACCOUNT_ID, 11)