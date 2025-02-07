from typing import Any, Optional
from datetime import date, time, datetime, timedelta
from functools import wraps
from sqlalchemy import create_engine, text, Column, Integer, String, Boolean, ForeignKey, Date, Time
from sqlalchemy.dialects.postgresql import JSONB, ARRAY, array
from sqlalchemy.orm import sessionmaker, Session as _SessionType
from sqlalchemy.ext.declarative import declarative_base
import unicodedata, re, bcrypt, uuid
from src.server.lib.constants import ENGINE_URL, LIST_OF_WEEKEND_DAYS, MIN_EMAIL_LEN, MAX_EMAIL_LEN, MIN_PASSWORD_LEN, MAX_PASSWORD_LEN, TOKEN_EXPIRY_SECONDS
from src.server.lib.utils import log, errlog, parse_date, parse_time
from src.server.lib.models import Credentials, Cookies, ScheduleType
from src.server.lib.exceptions import EmailTaken, NonExistent, InvalidCredentials, CookiesUnavailable, InvalidCookies

# Init
engine = create_engine(ENGINE_URL)
Session = sessionmaker(bind=engine)
Base = declarative_base()

def dbsession(*, commit: bool = False):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            session = Session()
            try:
                # Sanitize credentials if the first parameter is of type `Credentials`
                if args and isinstance(args[0], Credentials):
                    args = ( _sanitize_credentials(args[0]), ) + args[1:]
                result = func(*args, session=session, **kwargs)
                if commit: session.commit()
                log(f'[{func.__name__}] args={args}\tkwargs={kwargs}\t{result}', 'db', 'DEBUG')
                return result
            except Exception as e:
                session.rollback()
                is_auth = (type(e) in (EmailTaken, InvalidCredentials)) or (type(e) is NonExistent and e.entity == 'account')
                errlog(func.__name__, e, 'auth' if is_auth else 'db')
                raise e
            finally:
                session.close()
        return wrapper
    return decorator


# Tables
class Account(Base):
    __tablename__ = 'accounts'
    account_id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(256), unique=True, nullable=False)
    hashed_password = Column(String(128), nullable=False)
    __repr__ = lambda self: f'Account({self.account_id})'


class Token(Base):
    __tablename__ = 'tokens'
    account_id = Column(Integer, ForeignKey('accounts.account_id', ondelete='CASCADE'), primary_key=True, nullable=False)
    token = Column(String(256), unique=True, nullable=False)
    created_at = Column(Date, default=text('CURRENT_TIMESTAMP'))
    expires_at = Column(Date, nullable=True)
    __repr__ = lambda self: f'Token({self.account_id})'


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


class Holiday(Base):
    __tablename__ = 'holidays'
    account_id = Column(Integer, ForeignKey('accounts.account_id', ondelete='CASCADE'), nullable=False)
    holiday_id = Column(Integer, primary_key=True, autoincrement=True)
    holiday_name = Column(String(100), nullable=False)
    assigned_to = Column(ARRAY(Integer, dimensions=1), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    __repr__ = lambda self: f'Holiday({self.holiday_id})'


class Settings(Base):
    __tablename__ = 'settings'
    account_id = Column(Integer, ForeignKey('accounts.account_id', ondelete='CASCADE'), nullable=False, primary_key=True)
    dark_theme_enabled = Column(Boolean, nullable=False)
    min_max_work_hours_enabled = Column(Boolean, nullable=False)
    multi_emps_in_shift_enabled = Column(Boolean, nullable=False)
    multi_shifts_one_emp_enabled = Column(Boolean, nullable=False)
    weekend_days = Column(String(17), nullable=False)
    max_emps_in_shift = Column(Integer, nullable=False)
    __repr__ = lambda self: f'Settings({self.account_id})'


# Utils not meant to be called directly
def _check_email_is_not_registered(sanitized_email: str, *, session: _SessionType) -> None:
    """Raises an exception if the provided email is already registered."""
    if session.query(Account).filter_by(email=sanitized_email).first():
        raise EmailTaken(sanitized_email)


def _check_account(account_id: int, *, session: _SessionType) -> Account:
    """Returns an account if it exists using its ID."""
    account = session.query(Account).filter_by(account_id=account_id).first()
    if not account: raise NonExistent('account', account_id)
    return account


def _check_employee(employee_id: int, *, session: _SessionType) -> Employee:
    """Returns an employee if it exists using its ID."""
    employee = session.query(Employee).filter_by(employee_id=employee_id).first()
    if not employee: raise NonExistent('employee', employee_id)
    return employee


def _check_work_hours(min_work_hours: Optional[int] = None, max_work_hours: Optional[int] = None) -> tuple[Optional[int], Optional[int]]:
    """Checks & returns valid work hours."""
    if (not (min_work_hours and max_work_hours)) or (min_work_hours <= 0) or (max_work_hours <= 0): return None, None
    assert (min_work_hours > 0) and (max_work_hours > 0), 'Invalid min & max work hours'
    return min_work_hours, max_work_hours


def _check_shift(shift_id: int, *, session: _SessionType) -> Shift:
    """Returns a shift if it exists using its ID."""
    shift = session.query(Shift).filter_by(shift_id=shift_id).first()
    if not shift: raise NonExistent('shift', shift_id)
    return shift


def _check_schedule(schedule_id: int, *, session: _SessionType) -> Schedule:
    """Returns an schedule if it exists using its ID."""
    schedule = session.query(Schedule).filter_by(schedule_id=schedule_id).first()
    if not schedule: raise NonExistent('schedule', schedule_id)
    return schedule


def _check_holiday(holiday_id: int, *, session: _SessionType) -> Schedule:
    """Returns an schedule if it exists using its ID."""
    holiday = session.query(Holiday).filter_by(holiday_id=holiday_id).first()
    if not holiday: raise NonExistent('holiday', holiday_id)
    assert holiday.start_date <= holiday.end_date, 'Invalid start & end dates'
    for emp_id in holiday.assigned_to: _check_employee(emp_id, session=session)
    return holiday


def _check_month_and_year(month: int, year: int) -> None:
    """Checks if a given month & year are valid."""
    assert 0 <= month <= 11, 'Invalid month'
    assert 1970 <= year <= 9999, 'Invalid year'


def _get_default_settings_kwargs(account_id: int, toggled_setting: str = '', value: bool|str = True) -> dict:
    """Returns initial settings."""
    assert type(toggled_setting) is str and type(value) in [bool, str], 'Invalid setting'
    kwargs = dict(
        account_id=account_id,
        dark_theme_enabled=False,
        min_max_work_hours_enabled=True,
        multi_emps_in_shift_enabled=False,
        multi_shifts_one_emp_enabled=False,
        weekend_days=LIST_OF_WEEKEND_DAYS[0],
        max_emps_in_shift=1
    )
    if toggled_setting: kwargs[toggled_setting] = value
    return kwargs


def _sanitize_email(email: str) -> str:
    """
    Sanitizes the email by trimming whitespace, normalizing unicode, validating format,
    and removing potentially harmful characters.
    Raises a `ValueError` if the email is invalid or fails sanitization checks.
    """
    # Ensure email is a string
    if not isinstance(email, str): raise ValueError("Email must be a string.")
    # Normalize Unicode to prevent homograph attacks
    email = unicodedata.normalize('NFKC', email)
    # Trim leading and trailing whitespace
    email = email.strip()

    # Enforce email constraints
    if not (MIN_EMAIL_LEN <= len(email) <= MAX_EMAIL_LEN):
        raise ValueError(f'Email must be between {MIN_EMAIL_LEN} and {MAX_EMAIL_LEN} characters long.')

    # Validate email format using a regular expression
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, email):
        raise ValueError('Email format is invalid.')

    return email


def _sanitize_password(password: str) -> str:
    """
    Sanitizes the password by trimming whitespace, normalizing unicode, validating format,
    and removing potentially harmful characters.
    Raises a `ValueError` if the password is invalid or fails sanitization checks.
    """
    # Ensure password is a string
    if not isinstance(password, str): raise ValueError("Password must be a string.")
    # Normalize Unicode to prevent homograph attacks
    password = unicodedata.normalize('NFKC', password)
    # Trim leading and trailing whitespace
    password = password.strip()

    # Enforce password constraints
    if not (MIN_PASSWORD_LEN <= len(password) <= MAX_PASSWORD_LEN):
        raise ValueError(f'Password must be between {MIN_PASSWORD_LEN} and {MAX_PASSWORD_LEN} characters long.')

    # Remove any non-printable or harmful characters. Allow only printable ASCII
    password = re.sub(r'[^\x20-\x7E]', '', password)

    # Additional checks for security
    if ";" in password or "'" in password:
        raise ValueError(f'Password contains potentially harmful characters.')

    return password


def _sanitize_credentials(cred: Credentials) -> Credentials:
    """
    Sanitizes credentials by trimming whitespace, normalizing unicode, validating format,
    and removing potentially harmful characters.
    Raises a `ValueError` if credentials are invalid or fail sanitization checks.
    """
    cred.email = _sanitize_email(cred.email)
    cred.password = _sanitize_password(cred.password)
    return cred


def _hash_password(sanitized_password: str) -> str:
    """Returns the string hash of a given sanitized password."""
    return bcrypt.hashpw(sanitized_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def _authenticate_credentials(cred: Credentials, *, session: _SessionType) -> Account:
    """
    Authenticates credentials to ensure the account exists and the password matches the stored hash.

    Args:
        cred (Credentials): The credentials provided by the user.
        session (_SessionType): The database session for querying the account.
    Returns:
        Account: The authenticated account object if authentication succeeds.
    Raises:
        NonExistent: If the account with the given email does not exist.
        InvalidCredentials: If the password does not match the stored hash.
    """
    # Sanitize the input credentials
    sanitized_cred = _sanitize_credentials(cred)

    # Fetch the account from the database using the sanitized email
    account = session.query(Account).filter_by(email=sanitized_cred.email).first()
    if not account:
        raise NonExistent('account', sanitized_cred.email)

    # Verify the provided password against the stored hashed password
    if not bcrypt.checkpw(sanitized_cred.password.encode('utf-8'), account.hashed_password.encode('utf-8')):
        raise InvalidCredentials(cred)

    return account


def _generate_new_token() -> dict[str, str | datetime]:
    """Generates & returns a new authentication token with an expiry date."""
    return {
        'token': str(uuid.uuid4()),
        'expires_at': datetime.now() + timedelta(seconds=TOKEN_EXPIRY_SECONDS)
    }


def _create_new_token(account_id: int, *, session: _SessionType) -> str:
    """Creates a new authentication token for the client."""
    token_obj = Token(account_id=account_id, **_generate_new_token())
    session.add(token_obj)
    session.commit()
    log(f'New token created for account ID {account_id}: {token_obj.token}', 'auth')
    return token_obj.token


def _get_token_from_account(account_id: int, *, session: _SessionType) -> Optional[Token]:
    """Attempts to retrieve an already created token from a given account ID."""
    return session.query(Token).filter_by(account_id=account_id).first()


def _renew_token(account_id: int, *, session: _SessionType) -> str:
    """Renews an existing token of an account by generating a new token and updating the expiry date."""
    token_obj = _get_token_from_account(account_id, session=session)
    if token_obj is None: raise NonExistent('token', account_id)
    new_token = _generate_new_token()
    token_obj.token = new_token['token']
    token_obj.expires_at = new_token['expires_at']
    session.commit()
    log(f'Renewed token for account ID {account_id}: {token_obj.token}', 'auth')
    return token_obj.token


def _validate_cookies(cookies: Cookies, *, session: _SessionType) -> Account:
    """Validates the given cookies. Renews the token if it has expired and `renew_expired_token` is True."""
    if not cookies.available(): raise CookiesUnavailable(cookies)
    _check_account(cookies.account_id, session=session)
    token_obj = session.query(Token).filter_by(account_id=cookies.account_id, token=cookies.token).first()

    if token_obj is None:
        raise InvalidCookies(cookies)
    elif datetime.now() > token_obj.expires_at:
        raise InvalidCookies(cookies)

    account = _check_account(token_obj.account_id, session=session)
    log(f'Validated cookies: {cookies}', 'auth')
    return account


# Functional
## Account
@dbsession()
def log_in_account(cred: Credentials, *, session: _SessionType) -> tuple[Account, str]:
    """
    Authenticate an account based on the provided credentials.
    Creates a new token if either no token is given in the cookies, or the cookies are invalid.
    """
    account = _authenticate_credentials(cred, session=session)
    retrieved_token_obj = _get_token_from_account(account.account_id, session=session)

    if retrieved_token_obj is None:
        token = _create_new_token(account.account_id, session=session)
    elif datetime.now() > retrieved_token_obj.expires_at:
        token = _renew_token(account.account_id, session=session)
    else:
        token = retrieved_token_obj.token
    log(f'Successful login for email: {cred.email}', 'auth')
    return account, token


@dbsession()
def log_in_account_with_cookies(cookies: Cookies, *, session: _SessionType) -> Account:
    """Authenticate an account based on the given cookies."""
    if not cookies.available(): raise CookiesUnavailable(cookies)
    account = _validate_cookies(cookies, session=session)
    log(f'Successful login with cookies for email: {account.email}', 'auth')
    return account


@dbsession(commit=True)
def create_account(cred: Credentials, *, session: _SessionType) -> tuple[Account, str]:
    """Creates an account with the provided credentials. Returns the account and a new or the given token."""
    _check_email_is_not_registered(_sanitize_email(cred.email), session=session)
    cred = _sanitize_credentials(cred)
    account = Account(email=cred.email, hashed_password=_hash_password(cred.password))
    session.add(account)
    session.commit()
    token = _create_new_token(account.account_id, session=session)
    log(f'Successful account creating for email: {account.email}', 'auth')
    return account, token


@dbsession(commit=True)
def update_account(cookies: Cookies, updates: dict, *, session: _SessionType) -> Account:
    """Modifies an account's attributes based on the provided updates."""
    account = _validate_cookies(cookies, session=session)

    # Update the account attributes
    ALLOWED_FIELDS = {'email', 'new_password'}
    for key, value in updates.items():
        if key not in ALLOWED_FIELDS:
            raise ValueError(f'"{key}" is not a valid attribute to modify.')
        if key == 'email':
            email = _sanitize_email(value)
            _check_email_is_not_registered(email, session=session)
            setattr(account, key, email)
        elif key == 'new_password':
            password = _sanitize_password(value)
            hashed_password = _hash_password(password)
            setattr(account, 'hashed_password', hashed_password)

    if 'email' in updates and 'new_password' in updates:
        log(f'Modified account: {account}; email has changed to {updates["email"]}, and password has changed', 'auth')
    elif 'new_password' in updates:
        log(f'Modified account: {account}; only the password has changed', 'auth')
    else:
        log(f'Modified account: {account}; updates: {updates}', 'auth')

    return account


@dbsession(commit=True)
def delete_account(cookies: Cookies, *, session: _SessionType) -> None:
    """Deletes an account and all of its associated objects."""
    account = _validate_cookies(cookies, session=session)
    session.delete(account)
    log(f'Deleted account: {account}', 'auth')



## Emoloyee
@dbsession()
def get_all_employees_of_account(account_id: int, *, session: _SessionType) -> list[Employee]:
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
        session: _SessionType
    ) -> Employee:
    """Creates an employee for the given account ID."""
    _check_account(account_id, session=session)
    min_work_hours, max_work_hours = _check_work_hours(min_work_hours, max_work_hours)
    employee = Employee(account_id=account_id, employee_name=employee_name, min_work_hours=min_work_hours, max_work_hours=max_work_hours)
    session.add(employee)
    log(f'Created employee: {employee}', 'db')
    return employee


@dbsession(commit=True)
def update_employee(employee_id: int, updates: dict, *, session: _SessionType) -> Employee:
    """Updates an employee's attributes based on their ID and the updates."""
    employee = _check_employee(employee_id, session=session)

    ALLOWED_FIELDS = {'employee_name', 'min_work_hours', 'max_work_hours'}
    for key, value in updates.items():
        if key not in ALLOWED_FIELDS: raise ValueError(f'"{key}" is not a valid attribute to modify.')
        if key in ['min_work_hours', 'max_work_hours']: assert value > 0, 'Non-positive value for work hours was given'
        setattr(employee, key, value)

    log(f'Updated employee: {employee}, updates: {updates}', 'db')
    return employee


@dbsession(commit=True)
def delete_employee(employee_id: int, *, session: _SessionType) -> None:
    """Deletes an employee by their ID. It also removes their ID from any holiday assigned to them, and removes holidays that only contain that ID."""
    employee = _check_employee(employee_id, session=session)
    holidays = session.query(Holiday).filter(Holiday.assigned_to.any(employee_id)).all()
    for holiday in holidays:
        holiday.assigned_to = array([id for id in holiday.assigned_to if id != employee_id])
        if len(holiday.assigned_to) == 0: session.delete(holiday)
    session.delete(employee)
    log(f'Deleted employee: {employee}', 'db')



## Shift
@dbsession()
def get_all_shifts_of_account(account_id: int, *, session: _SessionType) -> list[Shift]:
    """Returns all shifts associated with the given account ID."""
    _check_account(account_id, session=session)
    return session.query(Shift).filter_by(account_id=account_id).all()


@dbsession(commit=True)
def create_shift(account_id: int, shift_name: str, start_time: str|time, end_time: str|time, *, session: _SessionType) -> Shift:
    """Creates a shift for the given account ID."""
    _check_account(account_id, session=session)
    if type(start_time) is str: start_time = parse_time(start_time)
    if type(end_time) is str: end_time = parse_time(end_time)
    shift = Shift(account_id=account_id, shift_name=shift_name, start_time=start_time, end_time=end_time)
    session.add(shift)
    log(f'Created shift: {shift}', 'db')
    return shift


@dbsession(commit=True)
def update_shift(shift_id: int, updates: dict, *, session: _SessionType) -> Shift:
    """Updates a shift's attributes based on the given shift ID and updates."""
    shift = _check_shift(shift_id, session=session)

    ALLOWED_FIELDS = {'shift_name', 'start_time', 'end_time'}
    for key, value in updates.items():
        if key not in ALLOWED_FIELDS: raise ValueError(f'"{key}" is not a valid attribute to modify.')
        setattr(shift, key, value)

    log(f'Updated shift: {shift}, updates: {updates}', 'db')
    return shift


@dbsession(commit=True)
def delete_shift(shift_id: int, *, session: _SessionType) -> None:
    """Deletes a shift by its ID."""
    shift = _check_shift(shift_id, session=session)
    session.delete(shift)
    log(f'Deleted shift: {shift}', 'db')


## Schedule
@dbsession()
def get_all_schedules_of_account(account_id: int, *, session: _SessionType, **filter_kwargs) -> list[Schedule]:
    """Returns all schedules associated with the given account ID."""
    _check_account(account_id, session=session)
    return session.query(Schedule).filter_by(account_id=account_id, **filter_kwargs).all()


@dbsession(commit=True)
def create_schedule(account_id: int, schedule: ScheduleType, month: int, year: int, *, session: _SessionType) -> Schedule:
    """Creates a schedule for the given account ID."""
    _check_month_and_year(month, year)
    _check_account(account_id, session=session)
    schedule = Schedule(account_id=account_id, schedule=schedule, month=month, year=year)
    session.add(schedule)
    log(f'Created schedule: {schedule}', 'db')
    return schedule


@dbsession(commit=True)
def update_schedule(schedule_id: int, updates: dict[str, Any], *, session: _SessionType) -> Schedule:
    """Updates a schedule's attributes based on the given schedule ID and updates."""
    schedule = _check_schedule(schedule_id, session=session)

    ALLOWED_FIELDS = {'schedule'}
    for key, value in updates.items():
        if key not in ALLOWED_FIELDS: raise ValueError(f'"{key}" is not a valid attribute to modify.')
        setattr(schedule, key, value)

    log(f'Updated schedule: {schedule}, updates: {updates}', 'db')
    return schedule


@dbsession(commit=True)
def delete_schedule(schedule_id: int, *, session: _SessionType) -> None:
    """Deletes a schedule by its ID."""
    schedule = _check_schedule(schedule_id, session=session)
    session.delete(schedule)
    log(f'Deleted schedule: {schedule}', 'db')


## Holiday
@dbsession()
def get_all_holidays_of_account(account_id: int, *, session: _SessionType) -> list[Holiday]:
    """Returns all holidays associated with the given account ID."""
    _check_account(account_id, session=session)
    return session.query(Holiday).filter_by(account_id=account_id).all()


@dbsession(commit=True)
def create_holiday(account_id: int, holiday_name: str, assigned_to: list[int], start_date: str|date, end_date: str|date, *, session: _SessionType) -> Holiday:
    """Creates a holiday for the given account ID."""
    _check_account(account_id, session=session)
    if type(start_date) is str: start_date = parse_date(start_date)
    if type(end_date) is str: end_date = parse_date(end_date)
    holiday = Holiday(account_id=account_id, holiday_name=holiday_name, assigned_to=assigned_to, start_date=start_date, end_date=end_date)
    session.add(holiday)
    log(f'Created holiday: {holiday}', 'db')
    return holiday


@dbsession(commit=True)
def update_holiday(holiday_id: int, updates: dict[str, Any], *, session: _SessionType) -> Holiday:
    """Updates a holiday's attributes based on the given holiday ID and updates."""
    holiday = _check_holiday(holiday_id, session=session)

    ALLOWED_FIELDS = {'holiday_name', 'assigned_to', 'start_date', 'end_date'}
    for key, value in updates.items():
        if key not in ALLOWED_FIELDS: raise ValueError(f'"{key}" is not a valid attribute to modify.')
        setattr(holiday, key, value)

    log(f'Updated holiday: {holiday}, updates: {updates}', 'db')
    return holiday


@dbsession(commit=True)
def delete_holiday(holiday_id: int, *, session: _SessionType) -> None:
    """Deletes a holiday by its ID."""
    holiday = _check_holiday(holiday_id, session=session)
    session.delete(holiday)
    log(f'Deleted holiday: {holiday}', 'db')


## Settings
@dbsession()
def get_settings_of_account(account_id: int, *, session: _SessionType) -> Settings | None:
    """Returns all settings of an account."""
    return session.query(Settings).filter_by(account_id=account_id).first()


@dbsession(commit=True)
def toggle_dark_theme(account_id: int, *, session: _SessionType) -> bool:
    """Switches between light & dark themes of an account."""
    _check_account(account_id, session=session)
    settings = session.query(Settings).filter_by(account_id=account_id).first()
    if settings is None:
        settings = Settings(**_get_default_settings_kwargs(account_id, 'dark_theme_enabled'))
        session.add(settings)
    else:
        settings.dark_theme_enabled = not settings.dark_theme_enabled
    return settings.dark_theme_enabled


@dbsession(commit=True)
def toggle_min_max_work_hours(account_id: int, *, session: _SessionType) -> bool:
    """Switches between light & dark themes of an account."""
    _check_account(account_id, session=session)
    settings = session.query(Settings).filter_by(account_id=account_id).first()
    if settings is None:
        settings = Settings(**_get_default_settings_kwargs(account_id, 'min_max_work_hours_enabled', False))
        session.add(settings)
    else:
        settings.min_max_work_hours_enabled = not settings.min_max_work_hours_enabled
    return settings.min_max_work_hours_enabled


@dbsession(commit=True)
def toggle_multi_emps_in_shift(account_id: int, *, session: _SessionType) -> bool:
    """Toggles whether multiple employees can be assigned to a single shift."""
    _check_account(account_id, session=session)
    settings = session.query(Settings).filter_by(account_id=account_id).first()
    if settings is None:
        settings = Settings(**_get_default_settings_kwargs(account_id, 'multi_emps_in_shift_enabled'))
        session.add(settings)
    else:
        settings.multi_emps_in_shift_enabled = not settings.multi_emps_in_shift_enabled
    return settings.multi_emps_in_shift_enabled


@dbsession(commit=True)
def toggle_multi_shifts_one_emp(account_id: int, *, session: _SessionType) -> bool:
    """Toggles whether an employee can be assigned to multiple shifts in a single day."""
    _check_account(account_id, session=session)
    settings = session.query(Settings).filter_by(account_id=account_id).first()
    if settings is None:
        settings = Settings(**_get_default_settings_kwargs(account_id, 'multi_shifts_one_emp_enabled'))
        session.add(settings)
    else:
        settings.multi_shifts_one_emp_enabled = not settings.multi_shifts_one_emp_enabled
    return settings.multi_shifts_one_emp_enabled


@dbsession(commit=True)
def update_weekend_days(account_id: int, weekend_days: str, *, session: _SessionType) -> str:
    """Updates the weekend days of an account."""
    _check_account(account_id, session=session)
    settings = session.query(Settings).filter_by(account_id=account_id).first()
    if settings is None:
        settings = Settings(**_get_default_settings_kwargs(account_id, 'weekend_days', weekend_days))
        session.add(settings)
    else:
        if weekend_days not in LIST_OF_WEEKEND_DAYS: raise ValueError(f'Invalid weekend days passed: "{weekend_days}"')
        settings.weekend_days = weekend_days
    return settings.weekend_days


@dbsession(commit=True)
def update_max_emps_in_shift(account_id: int, max_emps_in_shift: int, *, session: _SessionType) -> int:
    """Updates the maximum number of employees in a single shift for an account."""
    _check_account(account_id, session=session)
    settings = session.query(Settings).filter_by(account_id=account_id).first()
    if settings is None:
        settings = Settings(**_get_default_settings_kwargs(account_id))
        session.add(settings)
        raise ValueError('multi_emps_in_shift_enabled must be True first before updating max_emps_in_shift')
    else:
        if not settings.multi_emps_in_shift_enabled: raise ValueError('multi_emps_in_shift_enabled must be True first before updating max_emps_in_shift')
        if not (1 <= max_emps_in_shift <= 10): raise ValueError('max_emps_in_shift must be in the range [1, 10]')
        settings.max_emps_in_shift = max_emps_in_shift
    return settings.max_emps_in_shift