from fastapi.testclient import TestClient
from src.server.main import app
from tests.utils import ctxtest, signup, create_shift, delete_shift

# Init
client = TestClient(app)
SHIFT = {'shift_name': 'Morning', 'start_time': '08:00', 'end_time': '16:00'}

@ctxtest()
def setup_and_teardown():
    account_id = signup(client).json()['account']['account_id']
    shift_id = create_shift(client, account_id, SHIFT).json()['shift_id']
    yield account_id, shift_id


# Tests
def test_read_shifts(setup_and_teardown):
    account_id, _ = setup_and_teardown
    response = client.get(f'/accounts/{account_id}/shifts')
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_new_shift(setup_and_teardown):
    account_id, _ = setup_and_teardown
    new_shift = {'shift_name': 'Evening Shift', 'start_time': '16:00', 'end_time': '00:00'}
    response = create_shift(client, account_id, new_shift)
    assert response.status_code == 200

    response_data = response.json()
    assert response_data['shift_name'] == new_shift['shift_name']
    delete_shift(client, response_data['shift_id'])


def test_update_existing_shift(setup_and_teardown):
    _, shift_id = setup_and_teardown
    updates = {'shift_name': 'Night Shift', 'start_time': '00:00', 'end_time': '08:00'}
    response = client.patch(f'/shifts/{shift_id}', json=updates)
    assert response.status_code == 200
    assert response.json()['shift_name'] == updates['shift_name']


def test_delete_existing_shift(setup_and_teardown):
    _, shift_id = setup_and_teardown
    response = delete_shift(client, shift_id)
    assert response.status_code == 200
    assert response.json()['detail'] == 'Shift deleted successfully'