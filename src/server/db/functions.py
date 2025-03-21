from typing import Any, Optional
from datetime import date, time, timezone
from sqlalchemy.dialects.postgresql import array
from sqlalchemy.orm import Session as _SessionType

from src.server.lib.utils import log, parse_date, parse_time, utcnow
from src.server.lib.models import Credentials, Cookies, ScheduleType, SubscriptionInfo
from src.server.lib.exceptions import CookiesUnavailable, NonExistent
from src.server.lib.types import WeekendDays, Interval, WeekendDaysEnum, IntervalEnum, PricingPlanName
from src.server.lib.constants import WEB_SERVER_URL, PREDEFINED_SUB_INFOS
from src.server.lib.emails import send_email

from .tables import Account, Token, Subscription, Employee, Shift, Schedule, ScheduleRequests, Holiday, Settings
from .utils import (
    dbsession,
    _check_email_is_not_registered,
    _check_account,
    _check_employee,
    _check_work_hours,
    _check_shift,
    _check_schedule,
    _check_holiday,
    _check_month_and_year,
    _init_settings,
    _sanitize_email,
    _sanitize_password,
    _sanitize_credentials,
    _hash_password,
    _verify_password,
    _authenticate_credentials,
    _create_new_token,
    _get_token_from_account,
    _renew_token,
    _validate_cookies,
    _get_email_from_token,
    _validate_sub_info,
    _get_active_sub,
    _get_or_create_auth_token,
    _get_or_create_sub,
    _check_schedule_requests,
    _increment_schedule_requests
)

## Account
@dbsession(commit=True)
def create_account(cred: Credentials, sub_info: Optional[SubscriptionInfo] = None, *, session: _SessionType) -> tuple[Account, Optional[Subscription], str]:
    """Creates an account with the provided credentials. Returns the account and a new or the given token."""
    _check_email_is_not_registered(_sanitize_email(cred.email), session=session)
    cred = _sanitize_credentials(cred)

    # Step 1: Create account
    account = Account(email=cred.email, hashed_password=_hash_password(cred.password))
    session.add(account)
    session.commit()  # Commit to generate account_id

    # Step 2: Create subscription
    if sub_info:
        if sub_info.plan == 'basic': sub_info = PREDEFINED_SUB_INFOS['basic']
        if sub_info.plan == 'standard': sub_info = PREDEFINED_SUB_INFOS['standard']
        if sub_info.plan == 'premium': sub_info = PREDEFINED_SUB_INFOS['premium']
        sub_info = _validate_sub_info(account.account_id, sub_info, session=session)
        sub = Subscription(**sub_info)
        session.add(sub)
        session.commit()
    else:
        sub = None

    # Step 3: Set number of schedule requests
    schedule_requests = ScheduleRequests(account_id=account.account_id, num_requests=0, month=utcnow().month)
    session.add(schedule_requests)
    session.commit()

    # Step 4: Generate token
    token = _create_new_token(account.account_id, session=session)
    log(f'Successful account creation for email: "{account.email}", Subscription: {sub_info}', 'account')
    return account, sub, token


@dbsession(commit=True)
def change_email(cookies: Cookies, new_email: str, *, session: _SessionType) -> Account:
    """Updates the account's email after validation."""
    account = _validate_cookies(cookies, session=session)
    new_email = _sanitize_email(new_email)
    _check_email_is_not_registered(new_email, session=session)
    account.email = new_email
    account.email_verified = False
    log(f'Modified account: {account}; email has changed to {new_email}', 'account')
    return account


@dbsession(commit=True)
def change_password(cookies: Cookies, current_password: str, new_password: str, *, session: _SessionType) -> Account:
    """Updates the account's password after validation."""
    account = _validate_cookies(cookies, session=session)

    if not account.hashed_password:
        raise ValueError('This account uses OAuth only. You cannot set a password.')

    if not _verify_password(current_password, account.hashed_password):
        raise ValueError('Incorrect current password.')

    new_password = _sanitize_password(new_password)
    account.hashed_password = _hash_password(new_password)
    log(f'Modified account: {account}; password has changed', 'account')
    return account


@dbsession(commit=True)
def set_password(cookies: Cookies, new_password: str, *, session: _SessionType) -> Account:
    """Allows OAuth-only users to set a password for the first time."""
    account = _validate_cookies(cookies, session=session)

    if account.hashed_password:
        raise ValueError('You already have a password set.')

    if not account.oauth_email or not account.oauth_provider:
        raise ValueError('Only OAuth users can set a password for the first time.')

    new_password = _sanitize_password(new_password)
    account.hashed_password = _hash_password(new_password)

    log(f'Account {account.account_id} (OAuth: {account.oauth_provider}) has set a password for the first time.', 'account')
    return account


@dbsession(commit=True)
def delete_account(cookies: Cookies, *, session: _SessionType) -> None:
    """Deletes an account and all of its associated objects."""
    account = _validate_cookies(cookies, session=session)
    session.delete(account)
    log(f'Deleted account: {account}', 'account')



## Auth
@dbsession()
def log_in_account(cred: Credentials, *, session: _SessionType) -> tuple[Account, Optional[Subscription], str]:
    """
    Authenticate an account based on the provided credentials.
    Retrieves the active subscription and creates a new token if needed.
    """
    account = _authenticate_credentials(cred, session=session)
    retrieved_token_obj = _get_token_from_account(account.account_id, 'auth', session=session)

    # Check if a token is valid or needs to be renewed
    if retrieved_token_obj is None:
        token = _create_new_token(account.account_id, session=session)
    elif utcnow() > retrieved_token_obj.expires_at.replace(tzinfo=timezone.utc):
        token = _renew_token(account.account_id, session=session)
    else:
        token = retrieved_token_obj.token

    # Retrieve the active subscription for the account
    sub = _get_active_sub(account.account_id, session=session)
    log(f'Successful login for email: {cred.email}', 'auth')
    return account, sub, token


@dbsession()
def log_in_account_with_cookies(cookies: Cookies, *, session: _SessionType) -> tuple[Account, Optional[Subscription]]:
    """Authenticate an account based on the given cookies."""
    if not cookies.available(): raise CookiesUnavailable(cookies)
    account = _validate_cookies(cookies, session=session)
    sub = _get_active_sub(account.account_id, session=session)
    log(f'Successful login with cookies for email: {account.email}', 'auth')
    return account, sub


@dbsession(commit=True)
def log_in_with_google(email: str, access_token: str, oauth_id: str, plan_name: Optional[PricingPlanName] = None, *, session: _SessionType) -> tuple[Account, Optional[Subscription], str]:
    """Logs in a Google user, handling cases where they changed their email in your web app. 
    If `plan_name` is provided, it creates a new subscription; otherwise, returns the existing subscription.
    Ensures the user can only receive one free trial, regardless of plan.
    """
    email = _sanitize_email(email)
    account = session.query(Account).filter(Account.oauth_id == oauth_id).first()

    if account:
        # Store OAuth email only the first time
        if account.oauth_email is None:
            account.oauth_email = email  # Store original Google email (first-time login)

        # If the user changed their email in the web app, do NOT overwrite it.
        if not account.email:
            account.email = email  # Set email for first-time login only

        # Update OAuth token
        account.oauth_token = access_token
        session.commit()

        sub = _get_or_create_sub(account.account_id, plan_name, session=session)
        token = _get_or_create_auth_token(account.account_id, session=session)
        return account, sub, token

    # If no matching OAuth ID, check if an account exists with the same email
    existing_account = session.query(Account).filter(Account.email == email).first()

    if existing_account:
        if existing_account.oauth_id:
            # If email exists but is already linked to another OAuth ID, prevent hijacking
            raise ValueError('This email is already linked to a different OAuth account.')

        # Otherwise, link the existing email/password account to Google OAuth
        existing_account.oauth_provider = 'google'
        existing_account.oauth_token = access_token
        existing_account.oauth_id = oauth_id  # Link Google account
        existing_account.oauth_email = email  # Store the original OAuth email
        existing_account.email_verified = True
        session.commit()

        sub = _get_or_create_sub(existing_account.account_id, plan_name, session=session)
        token = _get_or_create_auth_token(existing_account.account_id, session=session)
        return existing_account, sub, token

    # No matching account => create a new one
    new_account = Account(
        email=email,  # First-time login, set email
        hashed_password=None,  # No password for OAuth users
        email_verified=True,
        oauth_provider='google',
        oauth_token=access_token,
        oauth_id=oauth_id,
        oauth_email=email  # Store OAuth email for future reference
    )
    session.add(new_account)
    session.commit()
    session.refresh(new_account)

    schedule_requests = ScheduleRequests(account_id=new_account.account_id, num_requests=0, month=utcnow().month)
    session.add(schedule_requests)
    session.commit()

    sub = _get_or_create_sub(new_account.account_id, plan_name, session=session)
    token = _get_or_create_auth_token(new_account.account_id, session=session)
    return new_account, sub, token


@dbsession(commit=True)
async def request_reset_password(email: str, *, session: _SessionType) -> str:
    """Sends a password reset email to users with a password set, even if they have OAuth."""
    email = _sanitize_email(email)
    account = session.query(Account).filter(Account.email == email).first()
    safe_msg = 'If this email exists, a reset link will be sent.'  # Prevents user enumeration attacks

    if not account: return safe_msg
    if not account.hashed_password: raise ValueError(
        'This account does not have a password. Use OAuth (e.g., Continue with Google) to log in.'
    )

    # Generate a password reset token & send email with reset link
    reset_token = _create_new_token(account.account_id, 'reset', session=session)
    reset_link = f'{WEB_SERVER_URL}/reset-password?token={reset_token}'

    await send_email(
        subject='Reset Your Password',
        body=f'<a href="{reset_link}">Click here to reset your password</a>',
        recipients=[account.email]
    )

    return safe_msg


@dbsession(commit=True)
def reset_password(new_password: str, reset_token: str, *, session: _SessionType) -> str:
    """Resets a user's password after verifying the reset token (when logged-out), without affecting OAuth login."""
    new_password = _sanitize_password(new_password)
    email = _get_email_from_token(reset_token, 'reset', session=session)

    # Find the account by email
    account = session.query(Account).filter(Account.email == email).first()
    if not account:
        raise NonExistent('account', email)
    if not account.hashed_password:
        raise ValueError('This account does not have a password. Use OAuth to log in.')

    # Hash and store the new password
    account.hashed_password = _hash_password(new_password)
    # Delete the used reset token
    session.query(Token).filter(Token.token == reset_token, Token.token_type == 'reset').delete()
    session.commit()

    return 'Password reset successfully. You can now log in with your new password or continue using OAuth.'


@dbsession(commit=True)
async def request_verify_email(email: str, *, session: _SessionType) -> str:
    """Sends an email verification link to users who need to verify their email."""
    email = _sanitize_email(email)
    account = session.query(Account).filter(Account.email == email).first()
    safe_msg = 'If this email exists, a verification link will be sent.'  # Prevents user enumeration attacks

    if not account: return safe_msg
    if account.email_verified: raise ValueError('Your email is already verified.')

    # Generate a verification token & send email with verification link
    verify_token = _create_new_token(account.account_id, 'verify', session=session)
    verify_link = f'{WEB_SERVER_URL}/verify-email?token={verify_token}'

    await send_email(
        subject='Verify Your Email',
        body=f'<a href="{verify_link}">Click here to verify your email</a>',
        recipients=[account.email]
    )

    return safe_msg


@dbsession(commit=True)
def verify_email(verify_token: str, *, session: _SessionType) -> str:
    """Verifies a user's email using the provided verification token."""
    email = _get_email_from_token(verify_token, 'verify', session=session)

    # Find the associated account
    account = session.query(Account).filter(Account.email == email).first()
    if not account: raise NonExistent('account', email)
    if account.email_verified: return 'Your email is already verified.'

    # Mark email as verified
    account.email_verified = True
    # Delete the used verification token
    session.query(Token).filter(Token.token == verify_token, Token.token_type == 'verify').delete()
    session.commit()

    return 'Email verified successfully!'



## Employee
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
    _check_schedule_requests(account_id, session=session)
    schedule = Schedule(account_id=account_id, schedule=schedule, month=month, year=year)
    session.add(schedule)
    _increment_schedule_requests(account_id, session=session)
    log(f'Created schedule: {schedule}', 'db')
    return schedule


@dbsession(commit=True)
def update_schedule(schedule_id: int, updates: dict[str, Any], *, session: _SessionType) -> Schedule:
    """Updates a schedule's attributes based on the given schedule ID and updates."""
    schedule = _check_schedule(schedule_id, session=session)
    _check_schedule_requests(schedule.account_id, session=session)

    ALLOWED_FIELDS = {'schedule'}
    for key, value in updates.items():
        if key not in ALLOWED_FIELDS: raise ValueError(f'"{key}" is not a valid attribute to modify.')
        setattr(schedule, key, value)

    _increment_schedule_requests(schedule.account_id, session=session)
    log(f'Updated schedule: {schedule}, updates: {updates}', 'db')
    return schedule


@dbsession(commit=True)
def delete_schedule(schedule_id: int, *, session: _SessionType) -> None:
    """Deletes a schedule by its ID."""
    schedule = _check_schedule(schedule_id, session=session)
    _check_schedule_requests(schedule.account_id, session=session)
    session.delete(schedule)
    _increment_schedule_requests(schedule.account_id, session=session)
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
    if settings is None: settings = _init_settings(account_id, session=session)
    settings.dark_theme_enabled = not settings.dark_theme_enabled
    return settings.dark_theme_enabled


@dbsession(commit=True)
def toggle_min_max_work_hours(account_id: int, *, session: _SessionType) -> bool:
    """Switches between light & dark themes of an account."""
    _check_account(account_id, session=session)
    settings = session.query(Settings).filter_by(account_id=account_id).first()
    if settings is None: settings = _init_settings(account_id, session=session)
    settings.min_max_work_hours_enabled = not settings.min_max_work_hours_enabled
    return settings.min_max_work_hours_enabled


@dbsession(commit=True)
def toggle_multi_emps_in_shift(account_id: int, *, session: _SessionType) -> bool:
    """Toggles whether multiple employees can be assigned to a single shift."""
    _check_account(account_id, session=session)
    settings = session.query(Settings).filter_by(account_id=account_id).first()
    if settings is None: settings = _init_settings(account_id, session=session)
    settings.multi_emps_in_shift_enabled = not settings.multi_emps_in_shift_enabled
    return settings.multi_emps_in_shift_enabled


@dbsession(commit=True)
def toggle_multi_shifts_one_emp(account_id: int, *, session: _SessionType) -> bool:
    """Toggles whether an employee can be assigned to multiple shifts in a single day."""
    _check_account(account_id, session=session)
    settings = session.query(Settings).filter_by(account_id=account_id).first()
    if settings is None: settings = _init_settings(account_id, session=session)
    settings.multi_shifts_one_emp_enabled = not settings.multi_shifts_one_emp_enabled
    return settings.multi_shifts_one_emp_enabled


@dbsession(commit=True)
def update_weekend_days(account_id: int, weekend_days: WeekendDays, *, session: _SessionType) -> str:
    """Updates the weekend days of an account."""
    _check_account(account_id, session=session)
    settings = session.query(Settings).filter_by(account_id=account_id).first()
    if settings is None: settings = _init_settings(account_id, session=session)
    LIST_OF_WEEKEND_DAYS = (WeekendDaysEnum.SAT_SUN.value, WeekendDaysEnum.FRI_SAT.value, WeekendDaysEnum.SUN_MON.value)
    if weekend_days not in LIST_OF_WEEKEND_DAYS: raise ValueError(f'Invalid weekend days passed: "{weekend_days}"')
    settings.weekend_days = weekend_days
    return settings.weekend_days


@dbsession(commit=True)
def update_max_emps_in_shift(account_id: int, max_emps_in_shift: int, *, session: _SessionType) -> int:
    """Updates the maximum number of employees in a single shift for an account."""
    _check_account(account_id, session=session)
    settings = session.query(Settings).filter_by(account_id=account_id).first()
    if settings is None: settings = _init_settings(account_id, session=session)
    if not settings.multi_emps_in_shift_enabled: raise ValueError('multi_emps_in_shift_enabled must be True first before updating max_emps_in_shift')
    if not (1 <= max_emps_in_shift <= 10): raise ValueError('max_emps_in_shift must be in the range [1, 10]')
    settings.max_emps_in_shift = max_emps_in_shift
    return settings.max_emps_in_shift


@dbsession(commit=True)
def toggle_email_ntf(account_id: int, *, session: _SessionType) -> bool:
    """Toggles whether an employee can be assigned to multiple shifts in a single day."""
    _check_account(account_id, session=session)
    settings = session.query(Settings).filter_by(account_id=account_id).first()
    if settings is None: settings = _init_settings(account_id, session=session)
    settings.email_ntf_enabled = not settings.email_ntf_enabled
    return settings.email_ntf_enabled


@dbsession(commit=True)
def update_email_ntf_interval(account_id: int, interval: Interval, *, session: _SessionType) -> bool:
    """Toggles whether an employee can be assigned to multiple shifts in a single day."""
    _check_account(account_id, session=session)
    settings = session.query(Settings).filter_by(account_id=account_id).first()
    if settings is None: settings = _init_settings(account_id, session=session)
    INTERVALS = (IntervalEnum.DAILY.value, IntervalEnum.WEEKLY.value, IntervalEnum.MONTHLY.value)
    if interval not in INTERVALS: raise ValueError(f'Invalid interval passed: "{interval}"')
    settings.email_ntf_interval = interval
    return settings.email_ntf_interval




## Subscription
@dbsession()
def get_num_schedule_requests(account_id: int, *, session: _SessionType) -> int:
    _check_account(account_id, session=session)
    return session.get(ScheduleRequests, account_id).num_requests


@dbsession()
def check_sub_expired(account_id: int, *, session: _SessionType) -> int:
    _check_account(account_id, session=session)
    sub = _get_active_sub(account_id, session=session)
    all_subs_count = session.query(Subscription).filter(Subscription.account_id == account_id).count()
    return sub is None and all_subs_count > 0