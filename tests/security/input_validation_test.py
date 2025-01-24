import pytest, bcrypt
from src.server.lib.models import Credentials
from src.server.lib.db import Session, Account, reset_whole_db, _sanitize_username, _sanitize_password, _sanitize_credentials, _hash_password, _authenticate_credentials
from src.server.lib.exceptions import NonExistent, InvalidCredentials

# Init
@pytest.fixture(scope='function', autouse=True)
def setup_and_teardown():
    reset_whole_db()
    yield
    reset_whole_db()


# Tests
def test_sanitize_username():
    assert _sanitize_username('  user  ') == 'user'
    assert _sanitize_username('user.name') == 'user.name'
    with pytest.raises(ValueError):
        _sanitize_username('invalid username!')


def test_sanitize_password():
    assert _sanitize_password('password123') == 'password123'
    with pytest.raises(ValueError): _sanitize_password('short')
    with pytest.raises(ValueError): _sanitize_password('  pass  ') == 'pass'


def test_sanitize_credentials():
    cred = Credentials(username='  user  ', password='  password  ')
    sanitized_cred = _sanitize_credentials(cred)
    assert sanitized_cred.username == 'user'
    assert sanitized_cred.password == 'password'


def test_hash_password():
    password = 'securepassword'
    hashed_password = _hash_password(password)
    assert hashed_password != password
    assert bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))


def test_authenticate_credentials_valid():
    cred = Credentials(username='validuser', password='validpassword')
    hashed_password = _hash_password(cred.password)
    account = Account(username=cred.username, hashed_password=hashed_password)
    
    with Session() as session:
        session.add(account)
        session.commit()
    
    authenticated_account = _authenticate_credentials(cred, session=session)
    assert authenticated_account.username == cred.username


def test_authenticate_credentials_invalid_username():
    cred = Credentials(username='invaliduser', password='validpassword')
    
    with pytest.raises(NonExistent):
        with Session() as session:
            _authenticate_credentials(cred, session=session)


def test_authenticate_credentials_invalid_password():
    cred = Credentials(username='validuser', password='invalidpassword')
    hashed_password = _hash_password('validpassword')
    account = Account(username=cred.username, hashed_password=hashed_password)
    
    with Session() as session:
        session.add(account)
        session.commit()
    
    with pytest.raises(InvalidCredentials):
        _authenticate_credentials(cred, session=session)