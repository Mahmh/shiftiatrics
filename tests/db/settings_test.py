import pytest
from src.server.lib.types import WeekendDaysEnum
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


def test_invalid_setting_name(setup_and_teardown):
    account_id = setup_and_teardown
    with pytest.raises(ValueError, match='Unsupported setting'):
        update_setting(account_id, 'nonexistent_field', True)


def test_type_casting(setup_and_teardown):
    account_id = setup_and_teardown
    # Boolean as string
    updated = update_setting(account_id, 'dark_theme_enabled', 'true')
    assert updated.dark_theme_enabled is True
    # Enum validation
    with pytest.raises(ValueError, match='Must be one of'):
        update_setting(account_id, 'weekend_days', 'Blursday')