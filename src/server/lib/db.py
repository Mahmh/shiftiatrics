from typing import Any, Optional
from datetime import time
from functools import wraps
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Time, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import sessionmaker, declarative_base, Session as SessionType
from src.server.lib.constants import ENGINE_URL
from src.server.lib.utils import log, err_log, parse_time
from src.server.lib.models import Credentials, ScheduleType
from src.server.lib.exceptions import UsernameTaken, NonExistent, InvalidCredentials

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
                is_auth = (type(e) in (UsernameTaken, InvalidCredentials)) or (type(e) is NonExistent and e.entity == 'account')
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
    account_id = Column(Integer, ForeignKey('accounts.account_id', ondelete='CASCADE'), nullable=False)
    employee_id = Column(Integer, primary_key=True, autoincrement=True)
    employee_name = Column(String(100), nullable=False)
    min_work_hours = Column(Integer, nullable=True)
    max_work_hours = Column(Integer, nullable=True)
    __repr__ = lambda self: f'Employee({self.employee_id})'

class Shift(Base):
    __tablename__ = 'shifts'
    account_id = Column(Integer, ForeignKey('accounts.account_id', ondelete='CASCADE'), nullable=False)
    shift_id = Column(Integer, primary_key=True, autoincrement=True)
    shift_name = Column(String(100), nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    __repr__ = lambda self: f'Employee({self.shift_id})'

class Schedule(Base):
    __tablename__ = 'schedules'
    account_id = Column(Integer, ForeignKey('accounts.account_id', ondelete='CASCADE'), nullable=False)
    schedule_id = Column(Integer, primary_key=True, autoincrement=True)
    schedule = Column(JSONB, nullable=False)
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    __repr__ = lambda self: f'Schedule({self.schedule_id})'

class Settings(Base):
    __tablename__ = 'settings'
    account_id = Column(Integer, ForeignKey('accounts.account_id', ondelete='CASCADE'), nullable=False, primary_key=True)
    dark_theme_enabled = Column(Boolean, nullable=False)
    min_max_work_hours_enabled = Column(Boolean, nullable=False)
    multi_emps_in_shift_enabled = Column(Boolean, nullable=False)
    __repr__ = lambda self: f'Settings({self.account_id})'


# Utils not meant to be called directly
def _check_username_is_unique(username: str, *, session: SessionType) -> bool:
    """Raises an exception if the provided username is already registered."""
    if session.query(Account).filter_by(username=username).first():
        raise UsernameTaken(username)


def _validate_credentials(cred: Credentials, *, session: SessionType) -> Account:
    """Validates credentials to ensure the account exists and is authenticated."""
    account = session.query(Account).filter_by(username=cred.username).first()
    if not account: raise NonExistent('account', cred.username)
    if cred.password != account.password: raise InvalidCredentials(cred)
    return account


def _check_account(account_id: int, *, session: SessionType) -> Account:
    """Returns an account if it exists using its ID."""
    account = session.query(Account).filter_by(account_id=account_id).first()
    if not account: raise NonExistent('account', account_id)
    return account


def _check_employee(employee_id: int, *, session: SessionType) -> Employee:
    """Returns an employee if it exists using its ID."""
    employee = session.query(Employee).filter_by(employee_id=employee_id).first()
    if not employee: raise NonExistent('employee', employee_id)
    return employee


def _check_work_hours(min_work_hours: Optional[int] = None, max_work_hours: Optional[int] = None) -> tuple[Optional[int], Optional[int]]:
    """Checks & returns valid work hours."""
    if (not (min_work_hours and max_work_hours)) or (min_work_hours <= 0) or (max_work_hours <= 0): return None, None
    assert (min_work_hours > 0) and (max_work_hours > 0)
    return min_work_hours, max_work_hours


def _check_shift(shift_id: int, *, session: SessionType) -> Shift:
    """Returns a shift if it exists using its ID."""
    shift = session.query(Shift).filter_by(shift_id=shift_id).first()
    if not shift: raise NonExistent('shift', shift_id)
    return shift


def _check_schedule(schedule_id: int, *, session: SessionType) -> Schedule:
    """Returns an schedule if it exists using its ID."""
    schedule = session.query(Schedule).filter_by(schedule_id=schedule_id).first()
    if not schedule: raise NonExistent('schedule', schedule_id)
    return schedule


def _check_month_and_year(month: int, year: int) -> None:
    """Checks if a given month & year are valid."""
    assert 0 <= month <= 11, 'Invalid month'
    assert 1970 <= year <= 9999, 'Invalid year'


# Functional
## Account
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
    _check_username_is_unique(cred.username, session=session)
    account = Account(username=cred.username, password=cred.password)
    session.add(account)
    return account


@dbsession(commit=True)
def update_account(cred: Credentials, updates: dict, *, session: SessionType) -> Account:
    """Modifies an account's attributes based on the provided credentials and updates."""
    account = _validate_credentials(cred, session=session)

    # Update the account attributes
    ALLOWED_FIELDS = {'username', 'password'}
    for key, value in updates.items():
        if key not in ALLOWED_FIELDS: raise ValueError(f'"{key}" is not a valid attribute to modify.')
        if key == 'username': _check_username_is_unique(value, session=session)
        setattr(account, key, value)

    log(f'Modified account: {account}, updates: {updates}', 'auth', 'INFO')
    return account


@dbsession(commit=True)
def delete_account(cred: Credentials, *, session: SessionType) -> None:
    """Deletes an account and all its employees based on the provided credentials."""
    account = _validate_credentials(cred, session=session)
    session.delete(account)
    log(f'Deleted account: {account}', 'auth', 'INFO')



## Emoloyee
@dbsession()
def get_all_employees_of_account(account_id: int, *, session: SessionType) -> list[Employee]:
    """Returns all employees in the database."""
    _check_account(account_id, session=session)
    return session.query(Employee).filter_by(account_id=account_id).all()


@dbsession(commit=True)
def create_employee(
        account_id: int, 
        employee_name: str, 
        min_work_hours: Optional[int] = None,
        max_work_hours: Optional[int] = None,
        *,
        session: SessionType
    ) -> Employee:
    """Creates an employee for the given account ID."""
    _check_account(account_id, session=session)
    min_work_hours, max_work_hours = _check_work_hours(min_work_hours, max_work_hours)
    employee = Employee(account_id=account_id, employee_name=employee_name, min_work_hours=min_work_hours, max_work_hours=max_work_hours)
    session.add(employee)
    log(f'Created employee: {employee}', 'db', 'INFO')
    return employee


@dbsession(commit=True)
def update_employee(employee_id: int, updates: dict, *, session: SessionType) -> Employee:
    """Updates an employee's attributes based on their ID and the updates."""
    employee = _check_employee(employee_id, session=session)

    ALLOWED_FIELDS = {'employee_name', 'min_work_hours', 'max_work_hours'}
    for key, value in updates.items():
        if key not in ALLOWED_FIELDS: raise ValueError(f'"{key}" is not a valid attribute to modify.')
        if key in ['min_work_hours', 'max_work_hours']: assert value > 0, 'Non-positive value for work hours was given'
        setattr(employee, key, value)

    log(f'Updated employee: {employee}, updates: {updates}', 'db', 'INFO')
    return employee


@dbsession(commit=True)
def delete_employee(employee_id: int, *, session: SessionType) -> None:
    """Deletes an employee by their ID."""
    employee = _check_employee(employee_id, session=session)
    session.delete(employee)
    log(f'Deleted employee: {employee}', 'db', 'INFO')



## Shift
@dbsession()
def get_all_shifts_of_account(account_id: int, *, session: SessionType) -> list[Shift]:
    """Returns all shifts associated with the given account ID."""
    _check_account(account_id, session=session)
    return session.query(Shift).filter_by(account_id=account_id).all()


@dbsession(commit=True)
def create_shift(account_id: int, shift_name: str, start_time: str|time, end_time: str|time, *, session: SessionType) -> Shift:
    """Creates a shift for the given account ID."""
    _check_account(account_id, session=session)
    if type(start_time) is str: start_time = parse_time(start_time)
    if type(end_time) is str: end_time = parse_time(end_time)
    shift = Shift(account_id=account_id, shift_name=shift_name, start_time=start_time, end_time=end_time)
    session.add(shift)
    log(f'Created shift: {shift}', 'db', 'INFO')
    return shift


@dbsession(commit=True)
def update_shift(shift_id: int, updates: dict, *, session: SessionType) -> Shift:
    """Updates a shift's attributes based on the given shift ID and updates."""
    shift = _check_shift(shift_id, session=session)

    ALLOWED_FIELDS = {'shift_name', 'start_time', 'end_time'}
    for key, value in updates.items():
        if key not in ALLOWED_FIELDS: raise ValueError(f'"{key}" is not a valid attribute to modify.')
        setattr(shift, key, value)

    log(f'Updated shift: {shift}, updates: {updates}', 'db', 'INFO')
    return shift


@dbsession(commit=True)
def delete_shift(shift_id: int, *, session: SessionType) -> None:
    """Deletes a shift by its ID."""
    shift = _check_shift(shift_id, session=session)
    session.delete(shift)
    log(f'Deleted shift: {shift}', 'db', 'INFO')



## Schedule
@dbsession()
def get_all_schedules_of_account(account_id: int, *, session: SessionType, **filter_kwargs) -> list[Schedule]:
    """Returns all schedules associated with the given account ID."""
    _check_account(account_id, session=session)
    return session.query(Schedule).filter_by(account_id=account_id, **filter_kwargs).all()


@dbsession(commit=True)
def create_schedule(account_id: int, schedule: ScheduleType, month: int, year: int, *, session: SessionType) -> Schedule:
    """Creates a schedule for the given account ID."""
    _check_month_and_year(month, year)
    _check_account(account_id, session=session)
    schedule = Schedule(account_id=account_id, schedule=schedule, month=month, year=year)
    session.add(schedule)
    log(f'Created schedule: {schedule}', 'db', 'INFO')
    return schedule


@dbsession(commit=True)
def update_schedule(schedule_id: int, updates: dict[str, Any], *, session: SessionType) -> Schedule:
    """Updates a schedule's attributes based on the given schedule ID and updates."""
    schedule = _check_schedule(schedule_id, session=session)

    ALLOWED_FIELDS = {'schedule'}
    for key, value in updates.items():
        if key not in ALLOWED_FIELDS: raise ValueError(f'"{key}" is not a valid attribute to modify.')
        setattr(schedule, key, value)

    log(f'Updated schedule: {schedule}, updates: {updates}', 'db', 'INFO')
    return schedule


@dbsession(commit=True)
def delete_schedule(schedule_id: int, *, session: SessionType) -> None:
    """Deletes a schedule by its ID."""
    schedule = _check_schedule(schedule_id, session=session)
    session.delete(schedule)
    log(f'Deleted schedule: {schedule}', 'db', 'INFO')


## Settings
@dbsession()
def get_settings_of_account(account_id: int, *, session: SessionType) -> Settings | None:
    """Returns all settings of an account."""
    return session.query(Settings).filter_by(account_id=account_id).first()


@dbsession(commit=True)
def toggle_dark_theme(account_id: int, *, session: SessionType) -> bool:
    """Switches between light & dark themes of an account."""
    _check_account(account_id, session=session)
    settings = session.query(Settings).filter_by(account_id=account_id).first()
    if settings is None:
        session.add(Settings(
            account_id=account_id,
            dark_theme_enabled=True,
            min_max_work_hours_enabled=False,
            multi_emps_in_shift_enabled=False
        ))
        return True
    else:
        settings.dark_theme_enabled = not settings.dark_theme_enabled
        return settings.dark_theme_enabled


@dbsession(commit=True)
def toggle_min_max_work_hours(account_id: int, *, session: SessionType) -> bool:
    """Switches between light & dark themes of an account."""
    _check_account(account_id, session=session)
    settings = session.query(Settings).filter_by(account_id=account_id).first()
    if settings is None:
        session.add(Settings(
            account_id=account_id,
            dark_theme_enabled=False,
            min_max_work_hours_enabled=True,
            multi_emps_in_shift_enabled=False
        ))
        return True
    else:
        settings.min_max_work_hours_enabled = not settings.min_max_work_hours_enabled
        return settings.min_max_work_hours_enabled


@dbsession(commit=True)
def toggle_multi_emps_in_shift(account_id: int, *, session: SessionType) -> bool:
    """Toggles whether multiple employees can be assigned to a single shift."""
    _check_account(account_id, session=session)
    settings = session.query(Settings).filter_by(account_id=account_id).first()
    if settings is None:
        session.add(Settings(
            account_id=account_id,
            dark_theme_enabled=False,
            min_max_work_hours_enabled=False,
            multi_emps_in_shift_enabled=True
        ))
        return True
    else:
        settings.multi_emps_in_shift_enabled = not settings.multi_emps_in_shift_enabled
        return settings.multi_emps_in_shift_enabled
