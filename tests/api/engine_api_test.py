import pytest, jpype
from fastapi.testclient import TestClient
from src.server.main import app
from src.server.lib.db import reset_whole_db
from src.server.lib.constants import locate

# Init
client = TestClient(app)
CRED = {'username': 'testuser4', 'password': 'testpass2'}
create_account = lambda cred: client.post('/accounts/signup', json=cred).json()['account_id']

EMPLOYEE = {'employee_name': 'John Doe'}
create_employee = lambda account_id, employee: client.post(f'/accounts/{account_id}/employees', json=employee).json()['employee_id']

SHIFT1 = {'shift_name': 'Morning', 'start_time': '08:00', 'end_time': '16:00'}
SHIFT2 = {'shift_name': 'Evening', 'start_time': '16:00', 'end_time': '20:00'}
create_shift = lambda account_id, shift: client.post(f'/accounts/{account_id}/shifts', json=shift).json()['shift_id']

SCHEDULE_DATA = {'schedule': [[[3], [1]], [[2, 3], [1]], [[3, 1], [2]], [[2], [1, 3]]], 'month': 11, 'year': 2024}
create_schedule = lambda account_id, schedule_data: client.post(f'/accounts/{account_id}/schedules', json=schedule_data)

@pytest.fixture(scope='function', autouse=True)
def setup_and_teardown():
    reset_whole_db()
    if not jpype.isJVMStarted():
        jpype.startJVM(classpath=locate('../engine/engine.jar'))
    account_id = create_account(CRED)
    create_employee(account_id, EMPLOYEE)
    create_shift(account_id, SHIFT1)
    create_shift(account_id, SHIFT2)
    create_schedule(account_id, SCHEDULE_DATA)
    yield account_id
    reset_whole_db()


# Tests
def test_generate_schedule(setup_and_teardown):
    account_id = setup_and_teardown
    num_days = 10
    response = client.get(f'/engine/generate_schedule?account_id={account_id}&num_days={num_days}&year={SCHEDULE_DATA["year"]}&month={SCHEDULE_DATA["month"]+1}')
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_shift_counts(setup_and_teardown):
    account_id = setup_and_teardown
    response = client.get(f'/engine/get_shift_counts_of_employees?account_id={account_id}&year={SCHEDULE_DATA["year"]}&month={SCHEDULE_DATA["month"]}')
    assert response.status_code == 200

    response_data = response.json()
    assert response_data['1'] == 4
    assert response_data['2'] == 3
    assert response_data['3'] == 4


def test_get_work_hours(setup_and_teardown):
    account_id = setup_and_teardown 
    response = client.get(f'/engine/get_work_hours_of_employees?account_id={account_id}&year={SCHEDULE_DATA["year"]}&month={SCHEDULE_DATA["month"]}')
    assert response.status_code == 200

    response_data = response.json()
    assert response_data['1'] == 4+4+8+4
    assert response_data['2'] == 0+8+4+8
    assert response_data['3'] == 8+8+8+4