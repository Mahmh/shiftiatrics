import pytest
from src.server.lib.models import Credentials, Cookies
from src.server.lib.exceptions import EmailTaken
from src.server.db import create_account, log_in_account, change_email, change_password, _verify_password
from tests.utils import ctxtest, CRED

# Init
CRED2 = Credentials(email='existinguser@gmail.com', password='anotherpass123')

@ctxtest()
def setup_and_teardown():
    account, token = create_account(CRED)
    create_account(CRED2)
    yield Cookies(account_id=account.account_id, token=token)


# Tests
def test_create_account():
    # The account is created during setup
    account, sub, _ = log_in_account(CRED)
    assert account.email == CRED.email
    assert sub is None


def test_create_account_email_taken():
    with pytest.raises(EmailTaken):
        create_account(CRED)


def test_change_email(setup_and_teardown):
    """Tests updating the email of an account."""
    cookies = setup_and_teardown
    new_email = 'newuser@outlook.com'
    modified_account = change_email(cookies, new_email)
    assert modified_account.email == new_email


def test_change_email_invalid(setup_and_teardown):
    cookies = setup_and_teardown
    existing_email = 'existinguser@gmail.com'  # Assume this email is already taken

    with pytest.raises(EmailTaken, match=f'Email "{existing_email}" is already registered'):
        change_email(cookies, existing_email)


def test_change_password(setup_and_teardown):
    """Tests updating the password of an account."""
    cookies = setup_and_teardown
    current_password = CRED.password
    new_password = 'NewPass!456'
    modified_account = change_password(cookies, new_password, current_password)

    assert not _verify_password(current_password, modified_account.hashed_password)
    assert _verify_password(new_password, modified_account.hashed_password)


def test_change_password_invalid_current(setup_and_teardown):
    cookies = setup_and_teardown
    incorrect_current = 'WrongPass!'
    new_password = 'NewPass!456'

    with pytest.raises(ValueError, match='Incorrect current password'):
        change_password(cookies, new_password, incorrect_current)


def test_two_users_have_different_emails_and_no_subs():
    account1, sub1, _ = log_in_account(CRED)
    account2, sub2, _ = log_in_account(CRED2)
    assert account1.email != account2.email
    assert sub1 == sub2 == None