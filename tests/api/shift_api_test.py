from fastapi.testclient import TestClient
from src.server.main import app
from src.server.db import create_shift
from tests.utils import ctxtest, signup

# Init
client = TestClient(app)
SHIFT = {'shift_name': 'Morning', 'start_time': '08:00', 'end_time': '16:00'}

@ctxtest()
def setup_and_teardown():
    account_id = signup(client).json()['account']['account_id']
    create_shift(account_id, **SHIFT)
    yield account_id


# Tests
def test_read_shifts(setup_and_teardown):
    account_id = setup_and_teardown
    response = client.get(f'/shifts/{account_id}')
    assert response.status_code == 200
    assert isinstance(response.json(), list)