from datetime import datetime, timedelta
import pytest
from src.server.lib.utils import utcnow
from src.server.lib.models import Cookies
from src.server.lib.exceptions import InvalidCookies, NonExistent
from src.server.db import Session, create_account, _renew_token, _generate_new_token, _get_token_from_account, _validate_cookies
from tests.utils import ctxtest, CRED

# Init
@ctxtest()
def setup_and_teardown():
    account, token = create_account(CRED)
    yield account.account_id, token


# Tests
def test_create_new_token(setup_and_teardown):
    account_id, token = setup_and_teardown
    assert account_id == 1
    assert token is not None
    assert len(token) > 0


def test_renew_token(setup_and_teardown):
    account_id, old_token = setup_and_teardown
    with Session() as session:
        new_token = _renew_token(account_id, session=session)
        assert new_token is not None
        assert new_token != old_token


def test_get_token_from_account(setup_and_teardown):
    account_id, _ = setup_and_teardown
    with Session() as session:
        token_obj = _get_token_from_account(account_id, 'auth', session=session)
        assert token_obj is not None
        assert len(token_obj.token)
        assert token_obj.account_id == account_id


def test_validate_cookies(setup_and_teardown):
    account_id, _ = setup_and_teardown
    with Session() as session:
        token_obj = _get_token_from_account(account_id, 'auth', session=session)
        cookies = Cookies(account_id=account_id, token=token_obj.token)
        account = _validate_cookies(cookies, session=session)
        assert account is not None
        assert account.account_id == account_id


def test_invalidate_expired_cookies(setup_and_teardown):
    account_id, _ = setup_and_teardown
    with Session() as session:
        token_obj = _get_token_from_account(account_id, 'auth', session=session)
        cookies = Cookies(account_id=account_id, token=token_obj.token)
        # Simulate token expiry
        token_obj.expires_at = utcnow() - timedelta(days=1)
        session.commit()
        with pytest.raises(InvalidCookies):
            _validate_cookies(cookies, session=session)


def test_renew_expired_token(setup_and_teardown):
    account_id, old_token = setup_and_teardown
    with Session() as session:
        token_obj = _get_token_from_account(account_id, 'auth', session=session)
        # Simulate token expiry
        token_obj.expires_at = utcnow() - timedelta(days=1)
        session.commit()
        # Renew the expired token
        new_token = _renew_token(account_id, session=session)
        assert new_token is not None
        assert new_token != old_token


def test_validate_cookies_with_invalid_token(setup_and_teardown):
    account_id, _ = setup_and_teardown
    with Session() as session:
        cookies = Cookies(account_id=account_id, token='invalidtoken')
        with pytest.raises(InvalidCookies):
            _validate_cookies(cookies, session=session)


def test_validate_cookies_with_nonexistent_account():
    with Session() as session:
        cookies = Cookies(account_id=999, token='sometoken')
        with pytest.raises(NonExistent):
            _validate_cookies(cookies, session=session)


def test_generate_new_token():
    token_data = _generate_new_token()
    assert 'token' in token_data
    assert 'expires_at' in token_data
    assert isinstance(token_data['token'], str)
    assert isinstance(token_data['expires_at'], datetime)
    assert utcnow() < token_data['expires_at']