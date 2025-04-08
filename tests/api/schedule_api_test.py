from fastapi.testclient import TestClient
from src.server.main import app
from src.server.lib.models import Credentials
from src.server.db import create_employee, create_shift
from tests.utils import ctxtest, signup, create_schedule, delete_schedule

# Init
client = TestClient(app)
CRED2 = Credentials(email='abc@somemail.com', password='somepass')
SCHEDULE = {'schedule': [[[1, 2], [3, 4]]], 'month': 11, 'year': 2024}

@ctxtest()
def setup_and_teardown():
    account_id = signup(client).json()['account']['account_id']
    schedule_id = create_schedule(client, account_id, SCHEDULE).json()['schedule_id']
    create_employee(account_id, 'John')
    create_shift(account_id, 'Morning', '06:00', '12:00')
    yield account_id, schedule_id


# Tests
def test_read_schedules(setup_and_teardown):
    account_id, _ = setup_and_teardown
    response = client.get(f'/schedules/{account_id}')
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_new_schedule(setup_and_teardown):
    account_id, _ = setup_and_teardown
    new_schedule_data = {'schedule': [[[5, 6], [7]]], 'month': 7, 'year': 2025}
    response = create_schedule(client, account_id, new_schedule_data)
    assert response.status_code == 200

    response_data = response.json()
    assert response_data['schedule'] == new_schedule_data['schedule']
    assert response_data['month'] == new_schedule_data['month']
    assert response_data['year'] == new_schedule_data['year']
    delete_schedule(client, response_data['schedule_id'])


def test_update_existing_schedule(setup_and_teardown):
    _, schedule_id = setup_and_teardown
    updates = {'schedule': [[[9], [11, 12]]]}
    response = client.patch(f'/schedules/{schedule_id}', json=updates)
    assert response.status_code == 200
    assert response.json()['schedule'] == updates['schedule']


def test_delete_existing_schedule(setup_and_teardown):
    _, schedule_id = setup_and_teardown
    response = delete_schedule(client, schedule_id)
    assert response.status_code == 200
    assert response.json()['detail'] == 'Schedule deleted successfully'


def test_generate_schedule(setup_and_teardown):
    account_id, _ = setup_and_teardown
    response = client.get(f'/engine/generate_schedule?account_id={account_id}&num_days=30&year=2025&month=12')
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_unimplemented_algorithm_for_account():
    r1 = signup(client, CRED2)
    assert r1.status_code == 200
    new_account_id = r1.json()['account']['account_id']
    assert new_account_id == 2

    create_employee(new_account_id, 'John2')
    create_shift(new_account_id, 'Morning2', '06:00', '12:00')

    r2 = client.get(f'/engine/generate_schedule?account_id={new_account_id}&num_days=31&year=2024&month=7')
    assert r2.status_code == 200
    assert 'not yet implemented' in r2.json()['error']