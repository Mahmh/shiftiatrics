import pytest
from fastapi.testclient import TestClient
from src.server.main import app

# Init
client = TestClient(app)
CRED = {'username': 'testuser', 'password': 'testpass'}
create_account = lambda cred: client.post('/accounts/signup', json=cred)
delete_account = lambda cred: client.request('DELETE', '/accounts', json=cred)

@pytest.fixture(scope='function', autouse=True)
def setup_and_teardown():
    # Setup: Create the account
    account_id = create_account(CRED).json()['account_id']
    yield account_id
    # Teardown: Delete the account
    delete_account(CRED)

# Tests
def test_read_settings(setup_and_teardown):
    account_id = setup_and_teardown
    response = client.get(f'/accounts/{account_id}/settings')
    assert response.status_code == 200
    assert response.json()['detail'] is None


def test_enable_dark_theme(setup_and_teardown):
    account_id = setup_and_teardown
    response = client.get(f'/accounts/{account_id}/settings/toggle_dark_theme')
    assert response.status_code == 200
    assert response.json()['detail'] == True


def test_disable_dark_theme(setup_and_teardown):
    account_id = setup_and_teardown
    response1 = client.get(f'/accounts/{account_id}/settings/toggle_dark_theme')
    response2 = client.get(f'/accounts/{account_id}/settings/toggle_dark_theme')
    assert response1.status_code == response2.status_code == 200
    assert response2.json()['detail'] == False