import pytest
from src.server.lib.types import WeekendDaysEnum, IntervalEnum
from src.server.db import (
    Settings, create_account,
    get_settings_of_account, toggle_dark_theme, toggle_min_max_work_hours, 
    toggle_multi_emps_in_shift, toggle_multi_shifts_one_emp, update_weekend_days, update_max_emps_in_shift,
    toggle_email_ntf, update_email_ntf_interval
)
from tests.utils import ctxtest, CRED, SUB_INFO

# Init
@ctxtest()
def setup_and_teardown():
    account_id = create_account(CRED, SUB_INFO)[0].account_id
    yield account_id


def _assert_all_default(account_id, settings: Settings, all_false: bool = False):
    assert isinstance(settings, Settings)
    assert settings.account_id == account_id
    assert settings.dark_theme_enabled is False
    assert settings.min_max_work_hours_enabled is (False if all_false else True)
    assert settings.multi_emps_in_shift_enabled is False
    assert settings.multi_shifts_one_emp_enabled is False


def _assert_one_true(account_id, setting: str, settings: Settings):
    assert isinstance(settings, Settings)
    assert settings.account_id == account_id

    all_settings = {setting, 'dark_theme_enabled', 'min_max_work_hours_enabled', 'multi_emps_in_shift_enabled', 'multi_shifts_one_emp_enabled'}
    for s in all_settings:
        assert getattr(settings, s) is (True if s in {setting, 'min_max_work_hours_enabled'} else False)


# Tests
def test_no_settings(setup_and_teardown):
    account_id = setup_and_teardown
    assert get_settings_of_account(account_id) is None


def test_enable_dark_theme(setup_and_teardown):
    account_id = setup_and_teardown
    toggle_dark_theme(account_id)
    settings = get_settings_of_account(account_id)
    _assert_one_true(account_id, 'dark_theme_enabled', settings)


def test_disable_dark_theme(setup_and_teardown):
    account_id = setup_and_teardown
    toggle_dark_theme(account_id)
    toggle_dark_theme(account_id)
    settings = get_settings_of_account(account_id)
    _assert_all_default(account_id, settings)


def test_enable_min_max_work_hours(setup_and_teardown):
    account_id = setup_and_teardown
    toggle_min_max_work_hours(account_id)
    toggle_min_max_work_hours(account_id)
    settings = get_settings_of_account(account_id)
    _assert_one_true(account_id, 'min_max_work_hours_enabled', settings)


def test_disable_min_max_work_hours(setup_and_teardown):
    account_id = setup_and_teardown
    toggle_min_max_work_hours(account_id)
    settings = get_settings_of_account(account_id)
    _assert_all_default(account_id, settings, all_false=True)


def test_enable_multi_emps_in_shift(setup_and_teardown):
    account_id = setup_and_teardown
    toggle_multi_emps_in_shift(account_id)
    settings = get_settings_of_account(account_id)
    _assert_one_true(account_id, 'multi_emps_in_shift_enabled', settings)


def test_disable_multi_emps_in_shift(setup_and_teardown):
    account_id = setup_and_teardown
    toggle_multi_emps_in_shift(account_id)
    toggle_multi_emps_in_shift(account_id)
    settings = get_settings_of_account(account_id)
    _assert_all_default(account_id, settings)


def test_enable_multi_shifts_one_emp(setup_and_teardown):
    account_id = setup_and_teardown
    toggle_multi_shifts_one_emp(account_id)
    settings = get_settings_of_account(account_id)
    _assert_one_true(account_id, 'multi_shifts_one_emp_enabled', settings)


def test_disable_multi_shifts_one_emp(setup_and_teardown):
    account_id = setup_and_teardown
    toggle_multi_shifts_one_emp(account_id)
    toggle_multi_shifts_one_emp(account_id)
    settings = get_settings_of_account(account_id)
    _assert_all_default(account_id, settings)


def test_update_weekend_days(setup_and_teardown):
    account_id = setup_and_teardown
    update_weekend_days(account_id, WeekendDaysEnum.FRI_SAT.value)
    settings = get_settings_of_account(account_id)
    _assert_all_default(account_id, settings)
    assert settings.weekend_days == WeekendDaysEnum.FRI_SAT


def test_update_max_emps_in_shift(setup_and_teardown):
    account_id = setup_and_teardown
    toggle_multi_emps_in_shift(account_id)
    update_max_emps_in_shift(account_id, 5)
    settings = get_settings_of_account(account_id)
    _assert_one_true(account_id, 'multi_emps_in_shift_enabled', settings)
    assert settings.max_emps_in_shift == 5


def test_update_max_emps_in_shift_without_enabling_multi_emps(setup_and_teardown):
    account_id = setup_and_teardown
    with pytest.raises(ValueError, match='multi_emps_in_shift_enabled must be True first before updating max_emps_in_shift'):
        update_max_emps_in_shift(account_id, 5)


def test_update_max_emps_in_shift_invalid_value(setup_and_teardown):
    account_id = setup_and_teardown
    toggle_multi_emps_in_shift(account_id)
    with pytest.raises(ValueError, match='max_emps_in_shift must be in the range \[1, 10\]'):
        update_max_emps_in_shift(account_id, 0)
    with pytest.raises(ValueError, match='max_emps_in_shift must be in the range \[1, 10\]'):
        update_max_emps_in_shift(account_id, 11)


def test_enable_email_ntf(setup_and_teardown):
    account_id = setup_and_teardown
    toggle_email_ntf(account_id)
    settings = get_settings_of_account(account_id)
    _assert_one_true(account_id, 'email_ntf_enabled', settings)


def test_disable_email_ntf(setup_and_teardown):
    account_id = setup_and_teardown
    toggle_email_ntf(account_id)
    toggle_email_ntf(account_id)
    settings = get_settings_of_account(account_id)
    _assert_all_default(account_id, settings)


def test_update_email_ntf_interval(setup_and_teardown):
    account_id = setup_and_teardown
    toggle_email_ntf(account_id)

    s1 = get_settings_of_account(account_id)
    _assert_all_default(account_id, s1)
    assert s1.email_ntf_interval == IntervalEnum.MONTHLY

    update_email_ntf_interval(account_id, IntervalEnum.DAILY.value)

    s2 = get_settings_of_account(account_id)
    assert s2.email_ntf_interval == IntervalEnum.DAILY
    _assert_all_default(account_id, s2)