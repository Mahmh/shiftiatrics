from fastapi.testclient import TestClient
from src.server.main import app
from tests.utils import ctxtest, signup, create_employee, delete_employee

# Init
client = TestClient(app)

@ctxtest()
def setup_and_teardown():
    account_id = signup(client).json()['account']['account_id']
    employee_id = create_employee(client, account_id).json()['employee_id']
    yield account_id, employee_id


# Tests
def test_read_employees(setup_and_teardown):
    account_id, _ = setup_and_teardown
    response = client.get(f'/accounts/{account_id}/employees')
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_new_employee(setup_and_teardown):
    account_id, _ = setup_and_teardown
    new_emp = {'employee_name': 'Jane Smith'}
    response = create_employee(client, account_id, new_emp)
    assert response.status_code == 200

    response_data = response.json()
    assert response_data['employee_name'] == new_emp['employee_name']
    delete_employee(client, response_data['employee_id'])


def test_update_existing_employee(setup_and_teardown):
    _, employee_id = setup_and_teardown
    updates = {'employee_name': 'Senior Developer'}
    response = client.patch(f'/employees/{employee_id}', json=updates)
    assert response.status_code == 200
    assert response.json()['employee_name'] == updates['employee_name']


def test_delete_existing_employee(setup_and_teardown):
    _, employee_id = setup_and_teardown
    response = delete_employee(client, employee_id)
    assert response.status_code == 200
    assert response.json()['detail'] == 'Employee deleted successfully'