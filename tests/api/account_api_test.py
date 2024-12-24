import pytest
from fastapi.testclient import TestClient
from src.server.main import app

# Init
client = TestClient(app)
CRED = {'username': 'testuser', 'password': 'testpass'}
create_account = lambda cred: client.post('/accounts/signup', json=cred)
delete_account = lambda cred: client.request('DELETE', '/accounts', json=cred)

@pytest.fixture(scope="function", autouse=True)
def setup_and_teardown():
    # Setup: Create the account
    create_account(CRED)
    yield
    # Teardown: Delete the account
    delete_account(CRED)

# Tests
def test_read_accounts():
    response = client.get('/accounts')
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_login_account():
    response = client.post('/accounts/login', json=CRED)
    assert response.status_code == 200

    response_data = response.json()
    assert response_data['username'] == CRED['username']
    assert response_data['password'] == CRED['password']


def test_create_new_account():
    new_cred = {'username': 'newuser', 'password': 'newpass'}
    response = create_account(new_cred)
    assert response.status_code == 200

    response_data = response.json()
    assert response_data['username'] == new_cred['username']
    assert response_data['password'] == new_cred['password']
    delete_account(new_cred)


def test_update_existing_account():
    updates = {'username': 'newuser'}
    response = client.patch('/accounts', json={'cred': CRED, 'updates': updates})
    assert response.status_code == 200
    assert response.json()['username'] == updates['username']
    delete_account({'username': updates['username'], 'password': CRED['password']})


def test_delete_existing_account():
    response = delete_account(CRED)
    assert response.status_code == 200
    assert response.json()['detail'] == 'Account deleted successfully'