import pytest
from src.server.lib.models import Credentials
from src.server.lib.types import WeekendDaysEnum, IntervalEnum
from src.server.db import (
    Settings, create_account,
    get_settings_of_account, toggle_dark_theme, toggle_min_max_work_hours, 
    toggle_multi_emps_in_shift, toggle_multi_shifts_one_emp, update_weekend_days, update_max_emps_in_shift,
    toggle_email_ntf, update_email_ntf_interval
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
    assert settings.min_max_work_hours_enabled is (False if all_false else True)
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
    update_weekend_days(ACCOUNT_ID, WeekendDaysEnum.FRI_SAT.value)
    settings = get_settings_of_account(ACCOUNT_ID)
    _assert_all_default(settings)
    assert settings.weekend_days == WeekendDaysEnum.FRI_SAT


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


def test_enable_email_ntf():
    toggle_email_ntf(ACCOUNT_ID)
    settings = get_settings_of_account(ACCOUNT_ID)
    _assert_one_true('email_ntf_enabled', settings)


def test_disable_email_ntf():
    toggle_email_ntf(ACCOUNT_ID)
    toggle_email_ntf(ACCOUNT_ID)
    settings = get_settings_of_account(ACCOUNT_ID)
    _assert_all_default(settings)


def test_update_email_ntf_interval():
    toggle_email_ntf(ACCOUNT_ID)

    s1 = get_settings_of_account(ACCOUNT_ID)
    _assert_all_default(s1)
    assert s1.email_ntf_interval == IntervalEnum.MONTHLY

    update_email_ntf_interval(ACCOUNT_ID, IntervalEnum.DAILY.value)

    s2 = get_settings_of_account(ACCOUNT_ID)
    assert s2.email_ntf_interval == IntervalEnum.DAILY
    _assert_all_default(s2)