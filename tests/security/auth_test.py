from fastapi.testclient import TestClient
import pytest
from src.server.main import app
from src.server.lib.models import Credentials
from src.server.lib.exceptions import InvalidCredentials, NonExistent
from src.server.db.functions import log_in_account
from src.server.db.tables import Session, Token
from tests.utils import ctxtest

# Init
client = TestClient(app)
CRED = {'email': 'testuser@gmail.com', 'password': 'testpass'}
create_account = lambda: client.post('/accounts/signup', json=CRED)
request_reset_password = lambda: client.post('/auth/request_reset_password', json={'email': CRED['email']})

@ctxtest()
def setup_and_teardown():
    account_id = create_account().json()['account_id']
    yield account_id


def _get_reset_token(account_id: int) -> Token:
    session = Session()
    try:
        reset_token = session.query(Token).filter(Token.account_id == account_id, Token.token_type == 'reset').first()
    finally:
        session.close()
    return reset_token


# Tests
def test_log_in_account():
    cred = Credentials(**CRED)
    account = log_in_account(cred)[0]
    assert account.email == cred.email


def test_log_in_account_invalid_credentials():
    invalid_credentials = Credentials(email='testuser@gmail.com', password='wrongpass')
    with pytest.raises(InvalidCredentials):
        log_in_account(invalid_credentials)


def test_log_in_account_nonexistent_user():
    nonexistent_credentials = Credentials(email='nonexistent@hotmail.com', password='!#nopass##')
    with pytest.raises(NonExistent):
        log_in_account(nonexistent_credentials)


def test_request_reset_password(setup_and_teardown):
    account_id = setup_and_teardown
    response = request_reset_password()
    assert response.status_code == 200
    assert 'reset link will be sent' in response.json()['detail']
    assert _get_reset_token(account_id) is not None


def test_reset_password(setup_and_teardown):
    account_id = setup_and_teardown
    new_password = 'newtestpass'
    request_reset_password()
    reset_token = _get_reset_token(account_id).token

    response = client.put('/auth/reset_password', json={'new_password': new_password, 'reset_token': reset_token})
    assert response.status_code == 200
    assert 'success' in response.json()['detail']

    account = log_in_account(Credentials(email=CRED['email'], password=new_password))[0]
    assert account.email == CRED['email']