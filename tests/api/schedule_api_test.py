import pytest
from fastapi.testclient import TestClient
from src.server.main import app
# Init
client = TestClient(app)
CRED = {'username': 'testuser2', 'password': 'testpass'}
create_account = lambda cred: client.post('/accounts/signup', json=cred)
delete_account = lambda cred: client.request('DELETE', '/accounts', json=cred)

SCHEDULE_DATA = {'schedule': [[[1, 2], [3, 4]]], 'month': 11, 'year': 2024}
create_schedule = lambda account_id, schedule_data: client.post(f'/accounts/{account_id}/schedules', json=schedule_data)
delete_schedule = lambda schedule_id: client.request('DELETE', f'/schedules/{schedule_id}')

@pytest.fixture(scope='function', autouse=True)
def setup_and_teardown():
    # Setup: Create the account & schedule
    account_id = create_account(CRED).json()['account_id']
    schedule_id = create_schedule(account_id, SCHEDULE_DATA).json()['schedule_id']
    yield account_id, schedule_id
    # Teardown: Delete both
    delete_schedule(schedule_id)
    delete_account(CRED)


# Tests
def test_read_schedules(setup_and_teardown):
    account_id, _ = setup_and_teardown
    response = client.get(f'/accounts/{account_id}/schedules')
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_new_schedule(setup_and_teardown):
    account_id, _ = setup_and_teardown
    new_schedule_data = {'schedule': [[[5, 6], [7]]], 'month': 7, 'year': 2025}
    response = create_schedule(account_id, new_schedule_data)
    assert response.status_code == 200

    response_data = response.json()
    assert response_data['schedule'] == new_schedule_data['schedule']
    assert response_data['month'] == new_schedule_data['month']
    assert response_data['year'] == new_schedule_data['year']
    delete_schedule(response_data['schedule_id'])


def test_update_existing_schedule(setup_and_teardown):
    _, schedule_id = setup_and_teardown
    updates = {'schedule': [[[9], [11, 12]]]}
    response = client.patch(f'/schedules/{schedule_id}', json=updates)
    assert response.status_code == 200
    assert response.json()['schedule'] == updates['schedule']


def test_delete_existing_schedule(setup_and_teardown):
    _, schedule_id = setup_and_teardown
    response = delete_schedule(schedule_id)
    assert response.status_code == 200
    assert response.json()['detail'] == 'Schedule deleted successfully'