from sqlalchemy import text
import pytest
from src.server.lib.db import (
    Session, Settings,
    create_account, delete_account,
    get_settings_of_account, toggle_dark_theme, toggle_min_max_work_hours, toggle_multi_emps_in_shift
)
from src.server.lib.models import Credentials
from src.server.lib.exceptions import UsernameTaken, NonExistent

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


# Tests
def test_no_settings():
    assert get_settings_of_account(ACCOUNT_ID) is None


def test_enable_dark_theme():
    toggle_dark_theme(ACCOUNT_ID)
    settings = get_settings_of_account(ACCOUNT_ID)
    assert isinstance(settings, Settings)
    assert settings.account_id == ACCOUNT_ID
    assert settings.dark_theme_enabled == True
    assert settings.min_max_work_hours_enabled == False
    assert settings.multi_emps_in_shift_enabled == False


def test_disable_dark_theme():
    toggle_dark_theme(ACCOUNT_ID)
    toggle_dark_theme(ACCOUNT_ID)
    settings = get_settings_of_account(ACCOUNT_ID)
    assert isinstance(settings, Settings)
    assert settings.account_id == ACCOUNT_ID
    assert settings.dark_theme_enabled == False
    assert settings.min_max_work_hours_enabled == False
    assert settings.multi_emps_in_shift_enabled == False


def test_enable_min_max_work_hours():
    toggle_min_max_work_hours(ACCOUNT_ID)
    settings = get_settings_of_account(ACCOUNT_ID)
    assert isinstance(settings, Settings)
    assert settings.account_id == ACCOUNT_ID
    assert settings.dark_theme_enabled == False
    assert settings.min_max_work_hours_enabled == True
    assert settings.multi_emps_in_shift_enabled == False


def test_disable_min_max_work_hours():
    toggle_min_max_work_hours(ACCOUNT_ID)
    toggle_min_max_work_hours(ACCOUNT_ID)
    settings = get_settings_of_account(ACCOUNT_ID)
    assert isinstance(settings, Settings)
    assert settings.account_id == ACCOUNT_ID
    assert settings.dark_theme_enabled == False
    assert settings.min_max_work_hours_enabled == False
    assert settings.multi_emps_in_shift_enabled == False


def test_enable_min_max_work_hours():
    toggle_multi_emps_in_shift(ACCOUNT_ID)
    settings = get_settings_of_account(ACCOUNT_ID)
    assert isinstance(settings, Settings)
    assert settings.account_id == ACCOUNT_ID
    assert settings.dark_theme_enabled == False
    assert settings.min_max_work_hours_enabled == False
    assert settings.multi_emps_in_shift_enabled == True


def test_disable_min_max_work_hours():
    toggle_multi_emps_in_shift(ACCOUNT_ID)
    toggle_multi_emps_in_shift(ACCOUNT_ID)
    settings = get_settings_of_account(ACCOUNT_ID)
    assert isinstance(settings, Settings)
    assert settings.account_id == ACCOUNT_ID
    assert settings.dark_theme_enabled == False
    assert settings.min_max_work_hours_enabled == False
    assert settings.multi_emps_in_shift_enabled == False