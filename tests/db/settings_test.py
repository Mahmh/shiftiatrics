import pytest
from src.server.lib.types import WeekendDaysEnum, IntervalEnum
from src.server.db import Settings, create_account, get_settings_of_account, update_setting
from tests.utils import ctxtest, CRED

# Init
@ctxtest()
def setup_and_teardown():
    account_id = create_account(CRED)[0].account_id
    yield account_id


# Tests
def test_get_settings(setup_and_teardown):
    account_id = setup_and_teardown
    assert isinstance(get_settings_of_account(account_id), Settings)


def test_update_valid_setting(setup_and_teardown):
    account_id = setup_and_teardown

    # Enable dark theme
    updated = update_setting(account_id, 'dark_theme_enabled', True)
    assert updated.dark_theme_enabled is True

    # Change enum
    updated = update_setting(account_id, 'weekend_days', WeekendDaysEnum.FRI_SAT.value)
    assert updated.weekend_days.value == WeekendDaysEnum.FRI_SAT.value

    # Change email notification interval
    updated = update_setting(account_id, 'email_ntf_interval', IntervalEnum.WEEKLY.value)
    assert updated.email_ntf_interval.value == IntervalEnum.WEEKLY.value

    # Update array
    updated = update_setting(account_id, 'rotation_pattern', ['D', 'E', None])
    assert updated.rotation_pattern == ['D', 'E', None]


def test_invalid_setting_name(setup_and_teardown):
    account_id = setup_and_teardown
    with pytest.raises(ValueError, match='Unsupported setting'):
        update_setting(account_id, 'nonexistent_field', True)


def test_setting_non_nullable_to_none(setup_and_teardown):
    account_id = setup_and_teardown
    with pytest.raises(ValueError, match='cannot be None'):
        update_setting(account_id, 'max_emps_in_shift', None)


def test_type_casting(setup_and_teardown):
    account_id = setup_and_teardown

    # Boolean as string
    updated = update_setting(account_id, 'email_ntf_enabled', 'true')
    assert updated.email_ntf_enabled is True

    # Integer as string
    updated = update_setting(account_id, 'max_shifts_per_week', '5')
    assert updated.max_shifts_per_week == 5

    # Enum validation
    with pytest.raises(ValueError, match='Must be one of'):
        update_setting(account_id, 'weekend_days', 'Blursday')

    # Array type validation
    with pytest.raises(ValueError, match='All array elements must be strings or null'):
        update_setting(account_id, 'rotation_pattern', ['D', 1, None])