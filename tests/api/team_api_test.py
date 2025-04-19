from fastapi.testclient import TestClient
from src.server.main import app
from src.server.db import create_team
from tests.utils import ctxtest, signup

# Init
client = TestClient(app)

@ctxtest()
def setup_and_teardown():
    account_id = signup(client).json()['account']['account_id']
    create_team(account_id, 'Test Team')
    yield account_id


# Tests
def test_read_teams(setup_and_teardown):
    account_id = setup_and_teardown
    response = client.get(f'/teams/{account_id}')
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert data[0]['team_name'] == 'Test Team'