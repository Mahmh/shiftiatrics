from typing import Optional, Callable, Any
from textwrap import dedent
from functools import wraps
from datetime import datetime, timezone
from sqlalchemy.orm import Session as _SessionType
from sqlalchemy import Boolean, String, Enum
import unicodedata, re, bcrypt, inspect, secrets, stripe
from src.server.lib.constants import MIN_EMAIL_LEN, MAX_EMAIL_LEN, MIN_PASSWORD_LEN, MAX_PASSWORD_LEN
from src.server.lib.utils import log, errlog, get_token_expiry_datetime, utcnow
from src.server.lib.models import Credentials, Cookies, ContactUsSubmissionData
from src.server.lib.types import TokenType, SettingValue
from src.server.lib.exceptions import EmailTaken, NonExistent, InvalidCredentials, CookiesUnavailable, InvalidCookies
from .tables import Session, Account, Token, Subscription, Employee, Shift, Schedule, Holiday, Settings

def _handle_args(args: tuple) -> tuple:
    # Sanitize credentials if the first parameter is of type `Credentials`
    if args and isinstance(args[0], Credentials):
        args = ( _sanitize_credentials(args[0]), ) + args[1:]
    return args


def _handle_result(commit: bool, func: Callable, result: Any, args: tuple, kwargs: dict[str, Any], *, session: _SessionType) -> None:
    if commit: session.commit()
    log(f'[{func.__name__}] args={args}\tkwargs={kwargs}\t{result}', 'db', 'DEBUG')

    if isinstance(result, (Account, Token, Employee, Shift, Schedule, Holiday, Settings)):
        session.refresh(result)
    return result


def _handle_exception(e: Exception, func: Callable, *, session: _SessionType) -> None:
    session.rollback()
    is_auth = (type(e) in (EmailTaken, InvalidCredentials, CookiesUnavailable, InvalidCookies)) or (type(e) is NonExistent and e.entity == 'account')
    errlog(func.__name__, e, 'auth' if is_auth else 'db')
    raise e


def dbsession(*, commit: bool = False):
    def decorator(func: Callable) -> Callable:
        is_async = inspect.iscoroutinefunction(func)

        if is_async:
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                session = Session()
                try:
                    args = _handle_args(args)
                    result = await func(*args, session=session, **kwargs)
                    _handle_result(commit, func, result, args, kwargs, session=session)
                    return result
                except Exception as e:
                    _handle_exception(e, func, session=session)
                finally:
                    session.close()
            return async_wrapper
        else:
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                session = Session()
                try:
                    args = _handle_args(args)
                    result = func(*args, session=session, **kwargs) 
                    _handle_result(commit, func, result, args, kwargs, session=session)
                    return result
                except Exception as e:
                    _handle_exception(e, func, session=session)
                finally:
                    session.close()
            return sync_wrapper
    return decorator



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


def _init_settings(account_id: int, *, session: _SessionType) -> Settings:
    """Initializes a Settings object in the DB."""
    settings = Settings(account_id=account_id)
    session.add(settings)
    session.commit()
    session.refresh(settings)
    return settings


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


def _verify_password(input_password: str, stored_hash: str) -> bool:
    """Compares the input password with its stored hash securely."""
    input_password = _sanitize_password(input_password)
    return bcrypt.checkpw(input_password.encode('utf-8'), stored_hash.encode('utf-8'))


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

    # Verify the provided password against the stored hash
    if not _verify_password(sanitized_cred.password, account.hashed_password):
        raise InvalidCredentials(cred)

    return account


def _generate_new_token(token_type: TokenType = 'auth') -> dict[str, str | datetime]:
    """Generates & returns a new authentication token with an expiry date."""
    return {
        'token': secrets.token_urlsafe(32),
        'expires_at': get_token_expiry_datetime(),
        'token_type': token_type
    }


def _create_new_token(account_id: int, token_type: Optional[TokenType] = None, *, session: _SessionType) -> str:
    """Creates a new authentication token for the client."""
    token_obj = Token(account_id=account_id, **_generate_new_token(token_type))
    session.add(token_obj)
    session.commit()
    log(f'New token created for account ID {account_id}: {token_obj.token}', 'auth')
    return token_obj.token


def _get_token_from_account(account_id: int, token_type: Optional[TokenType] = None, *, session: _SessionType) -> Optional[Token]:
    """Attempts to retrieve an already created token from a given account ID."""
    return session.query(Token).filter_by(account_id=account_id, token_type=token_type).first()


def _renew_token(account_id: int, *, session: _SessionType) -> str:
    """Renews an existing auth token of an account by generating a new token and updating the expiry date."""
    token_obj = _get_token_from_account(account_id, 'auth', session=session)
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
    elif utcnow() > token_obj.expires_at:
        raise InvalidCookies(cookies)

    account = _check_account(token_obj.account_id, session=session)
    log(f'Validated cookies: {cookies}', 'auth')
    return account


def _get_email_from_token(token: str, token_type: TokenType, *, session: _SessionType) -> str:
    """
    Retrieves the email associated with a valid, non-expired reset token.
    
    Args:
        reset_token (str): The token provided by the user.
    
    Returns:
        str: The email of the associated account.

    Raises:
        ValueError: If the token is invalid, expired, or not found.
    """
    token_obj = session.query(Token).filter(
        Token.token == token,
        Token.token_type == token_type,
        Token.expires_at > utcnow()  # Ensure token is still valid
    ).first()

    if not token_obj:
        raise ValueError(f'Invalid or expired {token_type} token.')

    account = session.query(Account).filter(Account.account_id == token_obj.account_id).first()
    if not account:
        raise ValueError(f'No account associated with this {token_type} token.')

    return account.email


def _get_active_sub(account_id: int, *, session: _SessionType) -> Optional[Subscription]:
    """Returns the latest active subscription for the given account, or None if no active subscription exists."""
    sub = session.query(Subscription).filter(Subscription.account_id == account_id).order_by(Subscription.expires_at.desc()).first()
    if not sub: return None

    if utcnow() > sub.expires_at:
        stripe_sub = stripe.Subscription.retrieve(sub.stripe_subscription_id)
        if stripe_sub.status not in ('active', 'trialing'):
            return None  # Subscription truly expired or canceled
        sub.expires_at = datetime.fromtimestamp(stripe_sub.current_period_end, tz=timezone.utc)
        session.commit()

    return sub if utcnow() < sub.expires_at else None


def _validate_and_cast(setting: str, value: SettingValue, column_type: Boolean | Enum | String) -> SettingValue:
    """
    Validates and casts the input value based on the SQLAlchemy column type.

    Args:
        setting (str): The name of the setting being updated.
        value (SettingValue): The raw input value to validate and cast.
        column_type: SQLAlchemy column type (e.g., Boolean, Enum, Integer, etc.).

    Returns:
        SettingValue: The casted value ready to store in the DB.

    Raises:
        ValueError or TypeError: If the value is invalid or doesn't match the column type.
    """
    # Handle Boolean
    if isinstance(column_type, Boolean):
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            val = value.lower()
            if val in ('true', '1', 'yes'):
                return True
            elif val in ('false', '0', 'no'):
                return False
        raise ValueError("Must be a boolean or boolean-like string (true/false/1/0/yes/no)")

    # Handle Enum (SQLAlchemy Enum)
    if isinstance(column_type, Enum):
        allowed = column_type.enums
        if isinstance(value, str) and value in allowed:
            return value
        raise ValueError(f"Must be one of: {allowed}")

    # Handle plain strings
    if isinstance(column_type, String):
        if not isinstance(value, str):
            raise ValueError("Must be a string")
        return value

    raise TypeError(f"Unsupported column type: {type(column_type)}")


def _get_email_body(data: ContactUsSubmissionData) -> str:
    return dedent(f'''
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <h2 style="color: #0056b3;">New Contact Us Submission</h2>
            <table style="border-collapse: collapse; width: 100%;">
                <tr><td><strong>Name:</strong></td><td>{data.name}</td></tr>
                <tr><td><strong>Email:</strong></td><td>{data.email}</td></tr>
                <tr><td><strong>Query Type:</strong></td><td>{data.query_type}</td></tr>
                <tr><td><strong>Message:</strong></td></tr>
                <tr><td colspan="2" style="border-top: 1px solid #ccc; padding-top: 10px;">{data.description}</td></tr>
            </table>
        </body>
        </html>
    ''')