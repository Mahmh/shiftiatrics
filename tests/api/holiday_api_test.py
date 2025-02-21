from fastapi.testclient import TestClient
from src.server.main import app
from tests.utils import ctxtest

# Init
client = TestClient(app)
CRED = {'email': 'testuser123@outlook.com', 'password': 'testpass'}
create_account = lambda cred: client.post('/accounts/signup', json=cred)

create_employee = lambda account_id, employee: client.post(f'/accounts/{account_id}/employees', json=employee)

HOLIDAY = {'holiday_name': 'Christmas', 'assigned_to': [2, 1], 'start_date': '2023-12-25', 'end_date': '2023-12-26'}
create_holiday = lambda account_id, holiday: client.post(f'/accounts/{account_id}/holidays', json=holiday)
delete_holiday = lambda holiday_id: client.request('DELETE', f'/holidays/{holiday_id}')

@ctxtest()
def setup_and_teardown():
    account_id = create_account(CRED).json()['account_id']
    create_employee(account_id, {'employee_name': 'testemp1'}).json()['employee_id']
    create_employee(account_id, {'employee_name': 'testemp2'}).json()['employee_id']
    holiday_id = create_holiday(account_id, HOLIDAY).json()['holiday_id']
    yield account_id, holiday_id


# Tests
def test_read_holidays(setup_and_teardown):
    account_id, _ = setup_and_teardown
    response = client.get(f'/accounts/{account_id}/holidays')
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_new_holiday(setup_and_teardown):
    account_id, _ = setup_and_teardown
    new_holiday = {'holiday_name': 'Holiday Name', 'assigned_to': [1], 'start_date': '2023-12-31', 'end_date': '2024-01-01'}
    response = create_holiday(account_id, new_holiday)
    assert response.status_code == 200

    response_data = response.json()
    assert response_data['assigned_to'] == new_holiday['assigned_to']
    delete_holiday(response_data['holiday_id'])


def test_update_existing_holiday(setup_and_teardown):
    _, holiday_id = setup_and_teardown
    updates = {'assigned_to': [2], 'start_date': '2024-12-24', 'end_date': '2024-12-25', 'holiday_name': 'Thanksgiving'}
    response = client.patch(f'/holidays/{holiday_id}', json=updates)
    assert response.status_code == 200
    assert response.json()['start_date'] == updates['start_date']


def test_delete_existing_holiday(setup_and_teardown):
    _, holiday_id = setup_and_teardown
    response = delete_holiday(holiday_id)
    assert response.status_code == 200
    assert response.json()['detail'] == 'Holiday deleted successfully'