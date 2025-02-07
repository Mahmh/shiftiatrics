import pytest, bcrypt
from src.server.lib.models import Credentials
from src.server.lib.db import Session, Account, _sanitize_email, _sanitize_password, _sanitize_credentials, _hash_password, _authenticate_credentials
from src.server.lib.exceptions import NonExistent, InvalidCredentials
from tests.utils import ctxtest

# Init
@ctxtest()

def setup_and_teardown():
    yield


# Tests
def test_sanitize_email():
    assert _sanitize_email('  user@gmail.com  ') == 'user@gmail.com'
    assert _sanitize_email('user.name@gmail.com') == 'user.name@gmail.com'
    with pytest.raises(ValueError, match='Email format is invalid.'):
        _sanitize_email('invalid email!')


def test_sanitize_password():
    assert _sanitize_password('password123') == 'password123'
    with pytest.raises(ValueError): _sanitize_password('short')
    with pytest.raises(ValueError): _sanitize_password('  pass  ') == 'pass'


def test_sanitize_credentials():
    cred = Credentials(email='  user@outlook.com  ', password='  password  ')
    sanitized_cred = _sanitize_credentials(cred)
    assert sanitized_cred.email == 'user@outlook.com'
    assert sanitized_cred.password == 'password'


def test_hash_password():
    password = 'securepassword'
    hashed_password = _hash_password(password)
    assert hashed_password != password
    assert bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))


def test_authenticate_credentials_valid():
    cred = Credentials(email='validuser@hotmail.com', password='validpassword')
    hashed_password = _hash_password(cred.password)
    account = Account(email=cred.email, hashed_password=hashed_password)
    
    with Session() as session:
        session.add(account)
        session.commit()
    
    authenticated_account = _authenticate_credentials(cred, session=session)
    assert authenticated_account.email == cred.email


def test_authenticate_credentials_invalid_email():
    cred = Credentials(email='invaliduser@gmail.com', password='validpassword')
    
    with pytest.raises(NonExistent):
        with Session() as session:
            _authenticate_credentials(cred, session=session)


def test_authenticate_credentials_invalid_password():
    cred = Credentials(email='validuser@gmail.com', password='invalidpassword')
    hashed_password = _hash_password('validpassword')
    account = Account(email=cred.email, hashed_password=hashed_password)
    
    with Session() as session:
        session.add(account)
        session.commit()
    
    with pytest.raises(InvalidCredentials):
        _authenticate_credentials(cred, session=session)