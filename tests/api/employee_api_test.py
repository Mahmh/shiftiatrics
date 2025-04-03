from fastapi.testclient import TestClient
from src.server.main import app
from src.server.db import create_employee
from tests.utils import ctxtest, signup, EMPLOYEE

# Init
client = TestClient(app)

@ctxtest()
def setup_and_teardown():
    account_id = signup(client).json()['account']['account_id']
    create_employee(account_id, **EMPLOYEE)
    yield account_id


# Tests
def test_read_employees(setup_and_teardown):
    account_id = setup_and_teardown
    response = client.get(f'/employees/{account_id}')
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert response.json()[0]['employee_name'] == EMPLOYEE['employee_name']