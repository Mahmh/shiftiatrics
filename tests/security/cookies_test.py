from fastapi.testclient import TestClient
from src.server.main import app
from src.server.lib.models import Credentials
from tests.utils import ctxtest, login, signup, CRED

# Init
client = TestClient(app)
CRED2 = Credentials(email='testuser2@gmail.com', password='testpass2')

@ctxtest()
def setup_and_teardown():
    signup(client, CRED2)
    signup(client, CRED)
    yield


# Tests
def test_store_cookies():
    response = login(client)
    assert response.status_code == 200
    assert 'account_id' in response.cookies
    assert 'auth_token' in response.cookies


def test_retrieve_cookies():
    response = login(client)
    assert response.status_code == 200
    client.cookies.set('account_id', response.cookies.get('account_id'))
    client.cookies.set('auth_token', response.cookies.get('auth_token'))
    response = client.get('/auth/log_in_account_with_cookies')
    assert response.status_code == 200
    assert response.json()['account']['account_id'] == 2


def test_clear_cookies():
    response = login(client)
    assert response.status_code == 200
    client.cookies.set('account_id', response.cookies.get('account_id'))
    client.cookies.set('auth_token', response.cookies.get('auth_token'))
    response = client.get('/auth/logout')
    assert response.status_code == 200
    assert response.cookies.get('account_id') == None
    assert response.cookies.get('auth_token') == None


def test_invalid_cookies():
    client.cookies.set('account_id', 'invalid')
    client.cookies.set('auth_token', 'invalid')
    response = client.get('/auth/log_in_account_with_cookies')
    assert response.status_code == 200
    assert response.json()['error'] == 'Account ID is either invalid or not found'


def test_unauthorized_access_to_account_endpoints():
    endpoints = ('/employees/2', '/shifts/2', '/schedules/2', '/holidays/2', '/settings/2')
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