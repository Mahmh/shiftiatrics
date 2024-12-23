from functools import wraps
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, Session as SessionType
from src.server.lib.constants import ENGINE_URL
from src.server.lib.logger import log, err_log
from src.server.lib.models import Credentials
from src.server.lib.exceptions import UsernameTaken, AccountDoesNotExist, InvalidCredentials

# Init
engine = create_engine(ENGINE_URL)
Session = sessionmaker(bind=engine)
Base = declarative_base()

def dbsession(*, commit=False):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            session = Session()
            try:
                result = func(*args, session=session, **kwargs)
                if commit: session.commit()
                log(f'[{func.__name__}] args={args}\tkwargs={kwargs}\t{result}', 'db', 'DEBUG')
                return result
            except Exception as e:
                session.rollback()
                is_auth = type(e) in (UsernameTaken, AccountDoesNotExist, InvalidCredentials)
                err_log(func.__name__, e, 'auth' if is_auth else 'db')
                raise e
            finally:
                session.close()
        return wrapper
    return decorator



# Tables
class Account(Base):
    __tablename__ = 'accounts'
    account_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False)
    password = Column(String(50), nullable=False)
    __repr__ = lambda self: f'Account({self.account_id})'

class Employee(Base):
    __tablename__ = 'employees'
    account_id = Column(Integer, ForeignKey('accounts.account_id'), nullable=False)
    employee_id = Column(Integer, primary_key=True, autoincrement=True)
    employee_name = Column(String(100), nullable=False)
    __repr__ = lambda self: f'Employee({self.employee_id})'

class Shift(Base):
    __tablename__ = 'shifts'
    account_id = Column(Integer, ForeignKey('accounts.account_id'), nullable=False)
    shift_id = Column(Integer, primary_key=True, autoincrement=True)
    shift_name = Column(String(100), nullable=False)
    time_range = Column(String(50), nullable=False)
    __repr__ = lambda self: f'Employee({self.shift_id})'

class Schedule(Base):
    __tablename__ = 'schedules'
    account_id = Column(Integer, ForeignKey('accounts.account_id'), nullable=False)
    schedule_id = Column(Integer, primary_key=True, autoincrement=True)
    schedule = Column(Text, nullable=False)
    __repr__ = lambda self: f'Schedule({self.schedule_id})'



# Utils
def _validate_credentials(cred: Credentials, *, session: SessionType) -> Account:
    """Validates credentials to ensure the account exists and is authenticated."""
    account = session.query(Account).filter_by(username=cred.username).first()
    if not account: raise AccountDoesNotExist(cred.username)
    if cred.password != account.password: raise InvalidCredentials(cred)
    return account



# Functional
@dbsession()
def get_all_accounts(*, session: SessionType) -> list[Account]:
    """Returns all accounts in the DB."""
    return session.query(Account).all()


@dbsession()
def log_in_account(cred: Credentials, *, session: SessionType) -> Account:
    """Authenticate an account based on the provided credentials."""
    account = _validate_credentials(cred, session=session)
    log(f'Successful login for username: {cred.username}', 'auth', 'INFO')
    return account


@dbsession(commit=True)
def create_account(cred: Credentials, *, session: SessionType) -> Account:
    """Creates an account with the provided credentials"""
    username_is_unique = not session.query(Account).filter_by(username=cred.username).first()
    if not username_is_unique: raise UsernameTaken(cred.username)
    account = Account(username=cred.username, password=cred.password)
    session.add(account)
    return account


@dbsession(commit=True)
def delete_account(cred: Credentials, *, session: SessionType) -> None:
    """Deletes an account based on the provided credentials."""
    account = _validate_credentials(cred, session=session)
    session.delete(account)
    log(f'Deleted account: {account}', 'auth', 'INFO')


@dbsession(commit=True)
def modify_account(cred: Credentials, updates: dict, *, session: SessionType) -> Account:
    """Modifies an account's attributes based on the provided credentials and updates."""
    account = _validate_credentials(cred, session=session)

    # Update the account attributes
    ALLOWED_FIELDS = {'username', 'password'}
    for key, value in updates.items():
        if key not in ALLOWED_FIELDS:
            raise ValueError(f'"{key}" is not a valid attribute to modify.')
        setattr(account, key, value)

    log(f'Modified account: {account}, updates: {updates}', 'auth', 'INFO')
    return account
