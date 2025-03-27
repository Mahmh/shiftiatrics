import pytest
from src.server.lib.models import Credentials, Cookies
from src.server.lib.exceptions import EmailTaken, NonExistent
from src.server.db import (
    Session,
    log_in_with_google,
    create_account,
    log_in_account,
    delete_account,
    change_email,
    change_password,
    set_password,
    _verify_password,
    _validate_cookies,
    _generate_new_token
)
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


def test_delete_account(setup_and_teardown):
    cookies = setup_and_teardown
    delete_account(cookies)
    with pytest.raises(NonExistent):
        log_in_account(CRED)


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
    modified_account = change_password(cookies, current_password, new_password)

    assert not _verify_password(current_password, modified_account.hashed_password)
    assert _verify_password(new_password, modified_account.hashed_password)


def test_change_password_invalid_current(setup_and_teardown):
    cookies = setup_and_teardown
    incorrect_password = 'WrongPass!'
    new_password = 'NewPass!456'

    with pytest.raises(ValueError, match='Incorrect current password'):
        change_password(cookies, incorrect_password, new_password)


def test_change_password_with_oauth():
    # Mock an OAuth-only user (who has no password set) by creating an OAuth account
    account, sub, token = log_in_with_google(
        email='oauthuser@gmail.com',
        access_token=_generate_new_token('auth')['token'],
        oauth_id='google-123456'
    )
    cookies = Cookies(account_id=account.account_id, token=token)
    password = 'OldPass!456'
    new_password = '!456NewPass'

    assert account.hashed_password is None
    account = set_password(cookies, password)
    assert account.hashed_password is not None
    account = change_password(cookies, password, new_password)
    assert _verify_password(new_password, account.hashed_password)
    assert sub is None


def test_set_password_with_oauth():
    # Mock an OAuth-only user
    account, sub, token = log_in_with_google(
        email='oauthuser@gmail.com',
        access_token=_generate_new_token('auth')['token'],
        oauth_id='google-123456'
    )
    cookies = Cookies(account_id=account.account_id, token=token)
    password = 'NewPass!456'

    assert account.hashed_password is None
    account = set_password(cookies, password)
    assert account.hashed_password is not None
    assert _verify_password(password, account.hashed_password)
    assert sub is None


def test_set_password_already_has_password(setup_and_teardown):
    """Tests that users who already have a password cannot use `set_password()`."""
    cookies = setup_and_teardown
    with pytest.raises(ValueError, match='already have a password'):
        set_password(cookies, 'AnotherPass123')


def test_set_password_non_oauth_user(setup_and_teardown):
    """Tests that non-OAuth users cannot use `set_password()`."""
    cookies = setup_and_teardown

    # Simulate a non-OAuth user by setting `hashed_password` & `oauth_email` to None
    with Session() as session:
        account = _validate_cookies(cookies, session=session)
        account.hashed_password = None
        account.oauth_email = None
        session.commit()
    
    with pytest.raises(ValueError, match='Only OAuth users'):
        set_password(cookies, 'NewPass!456')


def test_two_users_have_different_emails_and_no_subs():
    account1, sub1, _ = log_in_account(CRED)
    account2, sub2, _ = log_in_account(CRED2)
    assert account1.email != account2.email
    assert sub1 == sub2 == None