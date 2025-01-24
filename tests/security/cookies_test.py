import pytest
from fastapi.testclient import TestClient
from src.server.main import app
from src.server.lib.db import reset_whole_db

# Init
client = TestClient(app)
CRED = {'username': 'testuser', 'password': 'testpass'}
create_account = lambda: client.post('/accounts/signup', json=CRED)
login = lambda: client.post('/accounts/login', json=CRED)

@pytest.fixture(scope='function', autouse=True)
def setup_and_teardown():
    reset_whole_db()
    create_account()
    yield
    reset_whole_db()


# Tests
def test_store_cookies():
    response = login()
    assert response.status_code == 200
    assert 'account_id' in response.cookies
    assert 'auth_token' in response.cookies


def test_retrieve_cookies():
    response = login()
    assert response.status_code == 200
    cookies = response.cookies
    response = client.get('/accounts/log_in_account_with_cookies', cookies=cookies)
    assert response.status_code == 200
    assert response.json().get('account_id') == 1


def test_clear_cookies():
    response = login()
    assert response.status_code == 200
    cookies = response.cookies
    response = client.get('/accounts/logout', cookies=cookies)
    assert response.status_code == 200
    assert response.cookies.get('account_id') == 'None'
    assert response.cookies.get('auth_token') == 'None'


def test_invalid_cookies():
    response = client.get('/accounts/log_in_account_with_cookies', cookies={'account_id': 'invalid', 'auth_token': 'invalid'})
    assert response.status_code == 200
    assert response.json().get('error') == 'Account ID is either invalid or not found'