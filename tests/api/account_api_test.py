from fastapi.testclient import TestClient
from src.server.main import app
from tests.utils import ctxtest

# Init
client = TestClient(app)
CRED = {'email': 'testuser@gmail.com', 'password': 'testpass'}
create_account = lambda cred: client.post('/accounts/signup', json=cred)
login_account = lambda cred: client.post('/auth/login', json=cred)

@ctxtest()
def setup_and_teardown():
    create_account(CRED)
    yield


# Tests
def test_login_account():
    response = login_account(CRED)
    assert response.status_code == 200
    assert response.cookies.get('account_id') == '1'
    assert response.cookies.get('auth_token') != None
    assert response.json()['email'] == CRED['email']


def test_create_new_account():
    new_cred = {'email': 'newuser@gmail.com', 'password': 'newpass123'}
    response = create_account(new_cred)
    assert response.status_code == 200
    assert response.cookies.get('account_id') == '2'
    assert response.cookies.get('auth_token') != None
    assert response.json()['email'] == new_cred['email']


def test_update_email():
    payload = {'email': 'newuser@outlook.com'}
    response = client.patch('/accounts/email', json=payload)
    assert response.status_code == 200
    assert response.json()['email'] == payload['email']


def test_update_password():
    account = login_account(CRED).json()
    old_password_hash = account['hashed_password']

    payload = {'current_password': CRED['password'], 'new_password': 'thenewpass'}
    response = client.patch('/accounts/password', json=payload)
    assert response.status_code == 200
    assert response.json()['hashed_password'] != old_password_hash


def test_update_password_wrong_current():
    payload = {'current_password': 'anypassword', 'new_password': 'thenewpass'}
    response = client.patch('/accounts/password', json=payload)
    assert response.status_code == 200
    assert 'error' in response.json()
    assert 'Incorrect current password' in response.json()['error']


def test_set_password_without_oauth():
    payload = {'new_password': 'thenewpass'}
    response = client.patch('/accounts/password', json=payload)
    assert response.status_code == 200
    assert 'error' in response.json()
    assert 'already have a password' in response.json()['error']


def test_delete_existing_account():
    response = client.request('DELETE', '/accounts')
    assert response.status_code == 200
    assert response.cookies.get('account_id') == None
    assert response.cookies.get('auth_token') == None
    assert response.json()['detail'] == 'Account deleted successfully'