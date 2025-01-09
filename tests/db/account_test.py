import pytest
from src.server.lib.db import reset_serial_sequence, create_account, log_in_account, delete_account, update_account, get_all_accounts
from src.server.lib.models import Credentials
from src.server.lib.exceptions import UsernameTaken, InvalidCredentials, NonExistent

CRED = Credentials(username='testuser', password='testpass')

@pytest.fixture(scope='function', autouse=True)
def setup_and_teardown():
    # Setup: Create the account
    try: create_account(CRED)
    except UsernameTaken: pass
    yield  # Run the test
    # Teardown: Delete the account & reset the account_id serial sequence
    try: delete_account(CRED)
    except NonExistent: pass
    reset_serial_sequence()


# Tests
def test_create_account():
    # The account is created during setup
    account = log_in_account(CRED)
    assert account.username == CRED.username
    assert account.password == CRED.password


def test_create_account_username_taken():
    with pytest.raises(UsernameTaken):
        create_account(CRED)


def test_log_in_account():
    account = log_in_account(CRED)
    assert account.username == CRED.username


def test_log_in_account_invalid_credentials():
    invalid_credentials = Credentials(username='testuser', password='wrongpass')
    with pytest.raises(InvalidCredentials):
        log_in_account(invalid_credentials)


def test_log_in_account_nonexistent_user():
    nonexistent_credentials = Credentials(username='nonexistent', password='nopass')
    with pytest.raises(NonExistent):
        log_in_account(nonexistent_credentials)


def test_delete_account():
    delete_account(CRED)
    with pytest.raises(NonExistent):
        log_in_account(CRED)


def test_update_account():
    updates = {'username': 'newuser', 'password': 'newpass'}
    modified_account = update_account(CRED, updates)
    assert modified_account.username == 'newuser'
    assert modified_account.password == 'newpass'

    # Teardown for modified account
    modified_cred = Credentials(username='newuser', password='newpass')
    delete_account(modified_cred)


def test_update_account_invalid_field():
    updates = {'invalid_field': 'value'}
    with pytest.raises(ValueError):
        update_account(CRED, updates)


def test_get_all_accounts():
    accounts = get_all_accounts()
    assert len(accounts) == 1
    assert accounts[0].username == CRED.username