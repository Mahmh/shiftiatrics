import pytest
from fastapi.testclient import TestClient
from src.server.main import app
from src.server.lib.constants import LIST_OF_WEEKEND_DAYS

# Init
client = TestClient(app)
CRED = {'username': 'testuser', 'password': 'testpass'}
create_account = lambda cred: client.post('/accounts/signup', json=cred)
delete_account = lambda cred: client.request('DELETE', '/accounts', json=cred)

@pytest.fixture(scope='function', autouse=True)
def setup_and_teardown():
    # Setup: Create the account
    account_id = create_account(CRED).json()['account_id']
    yield account_id
    # Teardown: Delete the account
    delete_account(CRED)


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
    response = client.patch(f'/accounts/{account_id}/settings/update_weekend_days', json={'weekend_days': LIST_OF_WEEKEND_DAYS[1]})
    assert response.status_code == 200
    assert response.json()['detail'] == LIST_OF_WEEKEND_DAYS[1]