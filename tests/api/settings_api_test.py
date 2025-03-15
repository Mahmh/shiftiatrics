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


# Tests
def test_read_settings(setup_and_teardown):
    account_id = setup_and_teardown
    response = client.get(f'/accounts/{account_id}/settings')
    assert response.status_code == 200
    assert response.json()['detail'] is None


def test_enable_dark_theme(setup_and_teardown):
    account_id = setup_and_teardown
    response = client.get(f'/accounts/{account_id}/settings/toggle_dark_theme')
    assert response.status_code == 200
    assert response.json()['detail'] is True


def test_disable_dark_theme(setup_and_teardown):
    account_id = setup_and_teardown
    response1 = client.get(f'/accounts/{account_id}/settings/toggle_dark_theme')
    response2 = client.get(f'/accounts/{account_id}/settings/toggle_dark_theme')
    assert response1.status_code == response2.status_code == 200
    assert response2.json()['detail'] is False


def test_enable_min_max_work_hours(setup_and_teardown):
    account_id = setup_and_teardown
    response1 = client.get(f'/accounts/{account_id}/settings/toggle_min_max_work_hours')
    response2 = client.get(f'/accounts/{account_id}/settings/toggle_min_max_work_hours')
    assert response1.status_code == response2.status_code == 200
    assert response2.json()['detail'] is True


def test_disable_min_max_work_hours(setup_and_teardown):
    account_id = setup_and_teardown
    response = client.get(f'/accounts/{account_id}/settings/toggle_min_max_work_hours')
    assert response.status_code == 200
    assert response.json()['detail'] is False


def test_enable_multi_emps_in_shift(setup_and_teardown):
    account_id = setup_and_teardown
    response = client.get(f'/accounts/{account_id}/settings/toggle_multi_emps_in_shift')
    assert response.status_code == 200
    assert response.json()['detail'] is True


def test_disable_multi_emps_in_shift(setup_and_teardown):
    account_id = setup_and_teardown
    response1 = client.get(f'/accounts/{account_id}/settings/toggle_multi_emps_in_shift')
    response2 = client.get(f'/accounts/{account_id}/settings/toggle_multi_emps_in_shift')
    assert response1.status_code == response2.status_code == 200
    assert response2.json()['detail'] is False


def test_enable_multi_shifts_one_emp(setup_and_teardown):
    account_id = setup_and_teardown
    response = client.get(f'/accounts/{account_id}/settings/toggle_multi_shifts_one_emp')
    assert response.status_code == 200
    assert response.json()['detail'] is True


def test_disable_multi_shifts_one_emp(setup_and_teardown):
    account_id = setup_and_teardown
    response1 = client.get(f'/accounts/{account_id}/settings/toggle_multi_shifts_one_emp')
    response2 = client.get(f'/accounts/{account_id}/settings/toggle_multi_shifts_one_emp')
    assert response1.status_code == response2.status_code == 200
    assert response2.json()['detail'] is False


def test_update_weekend_days(setup_and_teardown):
    account_id = setup_and_teardown
    response = client.patch(f'/accounts/{account_id}/settings/update_weekend_days', json={'weekend_days': WeekendDaysEnum.FRI_SAT.value})
    assert response.status_code == 200
    assert response.json()['detail'] == WeekendDaysEnum.FRI_SAT.value


def test_update_max_emps_in_shift(setup_and_teardown):
    account_id = setup_and_teardown
    client.get(f'/accounts/{account_id}/settings/toggle_multi_emps_in_shift')
    response = client.patch(f'/accounts/{account_id}/settings/max_emps_in_shift', json={'max_emps_in_shift': 5})
    assert response.status_code == 200
    assert response.json()['detail'] == 5


def test_update_max_emps_in_shift_invalid_value(setup_and_teardown):
    account_id = setup_and_teardown
    client.get(f'/accounts/{account_id}/settings/toggle_multi_emps_in_shift')
    response = client.patch(f'/accounts/{account_id}/settings/max_emps_in_shift', json={'max_emps_in_shift': -1})
    assert 'must be in the range [1, 10]' in response.json()['error']


def test_enable_email_ntf(setup_and_teardown):
    account_id = setup_and_teardown
    response = client.get(f'/accounts/{account_id}/settings/toggle_email_ntf')
    assert response.status_code == 200
    assert response.json()['detail'] is True


def test_disable_email_ntf(setup_and_teardown):
    account_id = setup_and_teardown
    response1 = client.get(f'/accounts/{account_id}/settings/toggle_email_ntf')
    response2 = client.get(f'/accounts/{account_id}/settings/toggle_email_ntf')
    assert response1.status_code == response2.status_code == 200
    assert response2.json()['detail'] is False


def test_update_email_ntf_interval(setup_and_teardown):
    account_id = setup_and_teardown
    response = client.patch(f'/accounts/{account_id}/settings/update_email_ntf_interval', json={'email_ntf_interval': IntervalEnum.WEEKLY.value})
    assert response.status_code == 200
    assert response.json()['detail'] == IntervalEnum.WEEKLY.value