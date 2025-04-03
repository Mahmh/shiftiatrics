import jpype
from fastapi.testclient import TestClient
from src.server.main import app
from src.server.lib.constants import SCHEDULE_ENGINE_PATH
from src.server.db import create_employee, create_shift
from tests.utils import ctxtest, signup, create_schedule, EMPLOYEE, SCHEDULE, SHIFT1, SHIFT2

# Init
client = TestClient(app)

@ctxtest()
def setup_and_teardown():
    if not jpype.isJVMStarted():
        jpype.startJVM(classpath=SCHEDULE_ENGINE_PATH)
    account_id = signup(client).json()['account']['account_id']
    create_employee(account_id, **EMPLOYEE)
    create_shift(account_id, **SHIFT1)
    create_shift(account_id, **SHIFT2)
    create_schedule(client, account_id)
    yield account_id


# Tests
def test_generate_schedule(setup_and_teardown):
    account_id = setup_and_teardown
    num_days = 10
    response = client.get(f'/engine/generate_schedule?account_id={account_id}&num_days={num_days}&year={SCHEDULE["year"]}&month={SCHEDULE["month"]+1}')
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_shift_counts(setup_and_teardown):
    account_id = setup_and_teardown
    response = client.get(f'/engine/get_shift_counts_of_employees?account_id={account_id}&year={SCHEDULE["year"]}&month={SCHEDULE["month"]}')
    assert response.status_code == 200

    response_data = response.json()
    assert response_data['1'] == 4
    assert response_data['2'] == 3
    assert response_data['3'] == 4


def test_get_work_hours(setup_and_teardown):
    account_id = setup_and_teardown 
    response = client.get(f'/engine/get_work_hours_of_employees?account_id={account_id}&year={SCHEDULE["year"]}&month={SCHEDULE["month"]}')
    assert response.status_code == 200

    response_data = response.json()
    assert response_data['1'] == 4+4+8+4
    assert response_data['2'] == 0+8+4+8
    assert response_data['3'] == 8+8+8+4