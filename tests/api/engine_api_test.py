import pytest, jpype
from fastapi.testclient import TestClient
from src.server.main import app
from src.server.lib.constants import locate

# Init
client = TestClient(app)

@pytest.fixture(scope='function', autouse=True)
def setup_and_teardown():
    # Setup: Start JVM & create account
    if not jpype.isJVMStarted():
        jpype.startJVM(classpath=locate('../engine/bin/'))
    CRED = {'username': 'testuser2', 'password': 'testpass2'}
    account_id = client.post('/accounts/signup', json=CRED).json()['account_id']
    yield account_id
    # Teardown: Stop JVM & delete account
    client.request('DELETE', '/accounts', json=CRED)


# Tests
def test_generate_schedule(setup_and_teardown):
    account_id = setup_and_teardown
    response = client.post(f'/engine/generate_schedule?account_id={account_id}&num_shifts_per_day=2&num_days=31')
    assert response.status_code == 200
    assert isinstance(response.json(), list)