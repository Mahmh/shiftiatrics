import pytest
from src.server.db import create_account, log_in_account, delete_account, update_account
from src.server.lib.models import Credentials, Cookies
from src.server.lib.exceptions import EmailTaken, InvalidCredentials, NonExistent
from tests.utils import ctxtest

# Init
CRED = Credentials(email='testuser@gmail.com', password='testpass')

@ctxtest()
def setup_and_teardown():
    account, token = create_account(CRED)
    yield Cookies(account_id=account.account_id, token=token)


# Tests
def test_create_account():
    # The account is created during setup
    account = log_in_account(CRED)[0]
    assert account.email == CRED.email


def test_create_account_email_taken():
    with pytest.raises(EmailTaken):
        create_account(CRED)


def test_log_in_account():
    account = log_in_account(CRED)[0]
    assert account.email == CRED.email


def test_log_in_account_invalid_credentials():
    invalid_credentials = Credentials(email='testuser@gmail.com', password='wrongpass')
    with pytest.raises(InvalidCredentials):
        log_in_account(invalid_credentials)


def test_log_in_account_nonexistent_user():
    nonexistent_credentials = Credentials(email='nonexistent@hotmail.com', password='!#nopass##')
    with pytest.raises(NonExistent):
        log_in_account(nonexistent_credentials)


def test_delete_account(setup_and_teardown):
    cookies = setup_and_teardown
    delete_account(cookies)
    with pytest.raises(NonExistent):
        log_in_account(CRED)


def test_update_account(setup_and_teardown):
    cookies = setup_and_teardown
    updates = {'email': 'newuser@outlook.com'}
    modified_account = update_account(cookies, updates)
    assert modified_account.email == updates['email']


def test_update_account_invalid_field(setup_and_teardown):
    cookies = setup_and_teardown
    updates = {'invalid_field': 'value'}
    with pytest.raises(ValueError):
        update_account(cookies, updates)