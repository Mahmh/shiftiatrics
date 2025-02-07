import pytest
from fastapi.testclient import TestClient
from src.server.main import app
from tests.utils import ctxtest

# Init
client = TestClient(app)
CRED = {'email': 'testuser@gmail.com', 'password': 'testpass'}
CRED2 = {'email': 'testuser2@gmail.com', 'password': 'testpass2'}
create_account = lambda cred: client.post('/accounts/signup', json=cred)
login = lambda: client.post('/accounts/login', json=CRED)

@ctxtest()
def setup_and_teardown():
    create_account(CRED2)
    create_account(CRED)
    yield


# Tests
def test_store_cookies():
    response = login()
    assert response.status_code == 200
    assert 'account_id' in response.cookies
    assert 'auth_token' in response.cookies


def test_retrieve_cookies():
    response = login()
    assert response.status_code == 200
    client.cookies.set('account_id', response.cookies.get('account_id'))
    client.cookies.set('auth_token', response.cookies.get('auth_token'))
    response = client.get('/accounts/log_in_account_with_cookies')
    assert response.status_code == 200
    assert response.json().get('account_id') == 2


def test_clear_cookies():
    response = login()
    assert response.status_code == 200
    client.cookies.set('account_id', response.cookies.get('account_id'))
    client.cookies.set('auth_token', response.cookies.get('auth_token'))
    response = client.get('/accounts/logout')
    assert response.status_code == 200
    assert response.cookies.get('account_id') == None
    assert response.cookies.get('auth_token') == None


def test_invalid_cookies():
    client.cookies.set('account_id', 'invalid')
    client.cookies.set('auth_token', 'invalid')
    response = client.get('/accounts/log_in_account_with_cookies')
    assert response.status_code == 200
    assert response.json()['error'] == 'Account ID is either invalid or not found'


def test_unauthorized_access_to_account_endpoints():
    endpoints = [
        '/accounts/2/employees',
        '/accounts/2/shifts',
        '/accounts/2/schedules',
        '/accounts/2/holidays',
        '/accounts/2/settings'
    ]
    for endpoint in endpoints:
        response = client.get(endpoint)
        assert response.status_code == 200
        assert response.json()['error'] == 'Authentication required'


def test_unauthorized_access_to_engine_endpoints():
    endpoints = [
        '/engine/generate_schedule',
        '/engine/get_shift_counts_of_employees',
        '/engine/get_work_hours_of_employees'
    ]
    for endpoint in endpoints:
        response = client.get(endpoint, params={'account_id': 1, 'num_days': 30, 'year': 2023, 'month': 5})
        assert response.status_code == 200
        assert response.json()['error'] == 'Authentication required'