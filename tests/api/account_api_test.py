from fastapi.testclient import TestClient
from src.server.main import app
from tests.utils import ctxtest

# Init
client = TestClient(app)
CRED = {'email': 'testuser@gmail.com', 'password': 'testpass'}
create_account = lambda cred: client.post('/accounts/signup', json=cred)

@ctxtest()
def setup_and_teardown():
    create_account(CRED)
    yield


# Tests
def test_login_account():
    response = client.post('/auth/login', json=CRED)
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


def test_update_existing_account():
    updates = {'email': 'newuser@outlook.com'}
    response = client.patch('/accounts', json={'email': updates['email']})
    assert response.status_code == 200
    assert response.json()['email'] == updates['email']


def test_delete_existing_account():
    response = client.request('DELETE', '/accounts')
    assert response.status_code == 200
    assert response.cookies.get('account_id') == None
    assert response.cookies.get('auth_token') == None
    assert response.json()['detail'] == 'Account deleted successfully'