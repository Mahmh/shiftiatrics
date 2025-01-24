import pytest
from src.server.lib.db import reset_whole_db, create_account, log_in_account, delete_account, update_account, get_all_accounts
from src.server.lib.models import Credentials, Cookies
from src.server.lib.exceptions import UsernameTaken, InvalidCredentials, NonExistent

# Init
CRED = Credentials(username='testuser', password='testpass')

@pytest.fixture(scope='function', autouse=True)
def setup_and_teardown():
    reset_whole_db()
    account, token = create_account(CRED)
    yield Cookies(account_id=account.account_id, token=token)
    reset_whole_db()


# Tests
def test_create_account():
    # The account is created during setup
    account = log_in_account(CRED)[0]
    assert account.username == CRED.username


def test_create_account_username_taken():
    with pytest.raises(UsernameTaken):
        create_account(CRED)


def test_log_in_account():
    account = log_in_account(CRED)[0]
    assert account.username == CRED.username


def test_log_in_account_invalid_credentials():
    invalid_credentials = Credentials(username='testuser', password='wrongpass')
    with pytest.raises(InvalidCredentials):
        log_in_account(invalid_credentials)


def test_log_in_account_nonexistent_user():
    nonexistent_credentials = Credentials(username='nonexistent', password='!#nopass##')
    with pytest.raises(NonExistent):
        log_in_account(nonexistent_credentials)


def test_delete_account(setup_and_teardown):
    cookies = setup_and_teardown
    delete_account(cookies)
    with pytest.raises(NonExistent):
        log_in_account(CRED)


def test_update_account(setup_and_teardown):
    cookies = setup_and_teardown
    updates = {'username': 'newuser'}
    modified_account = update_account(cookies, updates)
    assert modified_account.username == updates['username']


def test_update_account_invalid_field(setup_and_teardown):
    cookies = setup_and_teardown
    updates = {'invalid_field': 'value'}
    with pytest.raises(ValueError):
        update_account(cookies, updates)


def test_get_all_accounts():
    accounts = get_all_accounts()
    assert len(accounts) == 1
    assert accounts[0].username == CRED.username