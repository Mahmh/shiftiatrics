from fastapi.testclient import TestClient
from src.server.main import app
from src.server.lib.models import Credentials
from src.server.db import log_in_account
from tests.utils import ctxtest, login, signup, CRED

# Init
client = TestClient(app)

@ctxtest()
def setup_and_teardown():
    signup(client)
    yield


# Tests
def test_login():
    response = login(client)
    assert response.status_code == 200
    assert response.cookies.get('account_id') == '1'
    assert response.cookies.get('auth_token') != None

    response_data = response.json()
    assert response_data['account']['email'] == CRED.email
    assert response_data['account']['sub_expired'] == False
    assert response_data['subscription'] == None


def test_create_new_account():
    new_cred = Credentials(email='newuser@gmail.com', password='newpass123')
    response = signup(client, new_cred)
    assert response.status_code == 200
    assert response.cookies.get('account_id') == '2'
    assert response.cookies.get('auth_token') != None

    response_data = response.json()
    assert response_data['account']['email'] == new_cred.email
    assert response_data['account']['sub_expired'] == False
    assert response_data['subscription'] == None


def test_update_email():
    payload = {'email': 'newuser@outlook.com'}
    response = client.patch('/accounts/email', json=payload)
    assert response.status_code == 200
    assert response.json()['email'] == payload['email']


def test_update_password():
    old_password_hash = log_in_account(CRED)[0].hashed_password
    payload = {'current_password': CRED.password, 'new_password': 'thenewpass'}
    response = client.patch('/accounts/password', json=payload)
    new_password_hash = log_in_account(Credentials(email=CRED.email, password=payload['new_password']))[0].hashed_password
    assert response.status_code == 200
    assert new_password_hash != old_password_hash


def test_update_password_wrong_current():
    payload = {'current_password': 'anypassword', 'new_password': 'thenewpass'}
    response = client.patch('/accounts/password', json=payload)
    assert response.status_code == 200
    assert 'error' in response.json()
    assert 'Incorrect current password' in response.json()['error']


def test_request_delete_account():
    response = client.request('DELETE', '/accounts')
    assert response.status_code == 200
    assert response.cookies.get('account_id') == None
    assert response.cookies.get('auth_token') == None
    assert response.json()['detail'] == 'Account deletion request sent'