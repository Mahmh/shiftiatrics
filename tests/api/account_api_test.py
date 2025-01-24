import pytest
from fastapi.testclient import TestClient
from src.server.main import app
from src.server.lib.db import reset_whole_db

# Init
client = TestClient(app)
CRED = {'username': 'testuser', 'password': 'testpass'}
create_account = lambda cred: client.post('/accounts/signup', json=cred)
delete_account = lambda: client.request('DELETE', '/accounts')

@pytest.fixture(scope='function', autouse=True)
def setup_and_teardown():
    reset_whole_db()
    create_account(CRED)
    yield
    reset_whole_db()


# Tests
def test_read_accounts():
    response = client.get('/accounts')
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_login_account():
    response = client.post('/accounts/login', json=CRED)
    assert response.status_code == 200
    assert response.cookies.get('account_id') == '1'
    assert response.cookies.get('auth_token') != 'None'
    assert response.json()['username'] == CRED['username']


def test_create_new_account():
    new_cred = {'username': 'newuser', 'password': 'newpass123'}
    response = create_account(new_cred)
    assert response.status_code == 200
    assert response.cookies.get('account_id') == '2'
    assert response.cookies.get('auth_token') != 'None'
    assert response.json()['username'] == new_cred['username']


def test_update_existing_account():
    updates = {'username': 'newuser'}
    response = client.patch('/accounts', json={'username': updates['username']})
    assert response.status_code == 200
    assert response.json()['username'] == updates['username']


def test_delete_existing_account():
    response = delete_account()
    assert response.status_code == 200
    assert response.cookies.get('account_id') == 'None'
    assert response.cookies.get('auth_token') == 'None'
    assert response.json()['detail'] == 'Account deleted successfully'