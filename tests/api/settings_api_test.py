from fastapi.testclient import TestClient
from src.server.main import app
from src.server.lib.types import WeekendDaysEnum, IntervalEnum
from tests.utils import ctxtest, signup

# Init
client = TestClient(app)

@ctxtest()
def setup_and_teardown():
    account_id = signup(client).json()['account']['account_id']
    yield account_id

def _patch_setting(account_id: int, setting: str, new_value):
    return client.patch(
        f'/accounts/{account_id}/settings',
        json={'setting': setting, 'new_value': new_value}
    )


# Tests
def test_read_settings(setup_and_teardown):
    account_id = setup_and_teardown
    response = client.get(f'/accounts/{account_id}/settings')
    assert response.status_code == 200
    assert response.json()['account_id'] == account_id


def test_dark_theme_toggle(setup_and_teardown):
    account_id = setup_and_teardown

    r1 = _patch_setting(account_id, 'dark_theme_enabled', True)
    assert r1.status_code == 200
    assert r1.json()['dark_theme_enabled'] is True

    r2 = _patch_setting(account_id, 'dark_theme_enabled', False)
    assert r2.status_code == 200
    assert r2.json()['dark_theme_enabled'] is False


def test_multi_shifts_one_emp_toggle(setup_and_teardown):
    account_id = setup_and_teardown

    r1 = _patch_setting(account_id, 'multi_shifts_one_emp', True)
    assert r1.status_code == 200
    assert r1.json()['multi_shifts_one_emp'] is True

    r2 = _patch_setting(account_id, 'multi_shifts_one_emp', False)
    assert r2.status_code == 200
    assert r2.json()['multi_shifts_one_emp'] is False


def test_email_notifications_toggle(setup_and_teardown):
    account_id = setup_and_teardown

    r1 = _patch_setting(account_id, 'email_ntf_enabled', True)
    assert r1.status_code == 200
    assert r1.json()['email_ntf_enabled'] is True

    r2 = _patch_setting(account_id, 'email_ntf_enabled', False)
    assert r2.status_code == 200
    assert r2.json()['email_ntf_enabled'] is False


def test_update_email_ntf_interval(setup_and_teardown):
    account_id = setup_and_teardown
    r = _patch_setting(account_id, 'email_ntf_interval', IntervalEnum.WEEKLY.value)
    assert r.status_code == 200
    assert r.json()['email_ntf_interval'] == IntervalEnum.WEEKLY.value


def test_update_weekend_days(setup_and_teardown):
    account_id = setup_and_teardown
    r = _patch_setting(account_id, 'weekend_days', WeekendDaysEnum.FRI_SAT.value)
    assert r.status_code == 200
    assert r.json()['weekend_days'] == WeekendDaysEnum.FRI_SAT.value


def test_update_max_emps_in_shift(setup_and_teardown):
    account_id = setup_and_teardown
    _patch_setting(account_id, 'multi_shifts_one_emp', True)

    r1 = _patch_setting(account_id, 'max_emps_in_shift', 5)
    assert r1.status_code == 200
    assert r1.json()['max_emps_in_shift'] == 5

    r2 = _patch_setting(account_id, 'max_emps_in_shift', 3)
    assert r2.status_code == 200
    assert r2.json()['max_emps_in_shift'] == 3


def test_update_max_emps_in_shift_invalid(setup_and_teardown):
    account_id = setup_and_teardown
    _patch_setting(account_id, 'multi_shifts_one_emp', True)

    r = _patch_setting(account_id, 'max_emps_in_shift', -1)
    assert r.status_code == 200
    assert 'Invalid value' in r.json()['error']


def test_update_rotation_pattern(setup_and_teardown):
    account_id = setup_and_teardown
    _patch_setting(account_id, 'use_rotation_pattern', True)

    pattern = ['D', 'E', None]
    r = _patch_setting(account_id, 'rotation_pattern', pattern)
    assert r.status_code == 200
    assert r.json()['rotation_pattern'] == pattern