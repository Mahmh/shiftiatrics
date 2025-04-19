from typing import Any, Optional
from textwrap import dedent
from datetime import date, time, datetime, timezone
from sqlalchemy import inspect
from sqlalchemy.orm import Session as _SessionType
from sqlalchemy.dialects.postgresql import array
import stripe

from src.server.lib.utils import log, parse_date, parse_time, utcnow, todict, todicts
from src.server.lib.models import Credentials, Cookies, ScheduleType, ContactUsSubmissionData
from src.server.lib.exceptions import CookiesUnavailable, NonExistent
from src.server.lib.types import SettingValue
from src.server.lib.constants import WEB_SERVER_URL, SUPPORT_EMAIL, NOREPLY_EMAIL, SYSTEM_EMAIL, PROD_URL
from src.server.lib.emails import send_email

from .tables import Account, Token, Subscription, Team, Employee, Shift, Schedule, Holiday, Settings
from .utils import (
    dbsession,
    _check_email_is_not_registered,
    _check_account,
    _check_team,
    _check_employee,
    _check_work_hours,
    _check_shift,
    _check_schedule,
    _check_holiday,
    _check_month_and_year,
    _init_settings,
    _validate_and_cast,
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
    _get_active_sub,
    _delete_all_holidays_of_employee
)

## Account
@dbsession(commit=True)
def create_account(cred: Credentials, *, session: _SessionType) -> tuple[Account, str]:
    """Creates an account with the provided credentials. Returns the account and a new or the given token."""
    _check_email_is_not_registered(_sanitize_email(cred.email), session=session)
    cred = _sanitize_credentials(cred)

    # Create account
    account = Account(email=cred.email, hashed_password=_hash_password(cred.password))
    session.add(account)
    session.commit()  # Commit to generate account_id

    # Generate token & set up default settings
    token = _create_new_token(account.account_id, session=session)
    _init_settings(account.account_id, session=session)
    log(f'Successful account creation for email: "{account.email}"', 'account')
    return account, token


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
def change_password(cookies: Cookies, new_password: str, current_password: Optional[str] = None, require_current: bool = True, *, session: _SessionType) -> Account:
    """Updates the account's password after validation."""
    if current_password is None: assert require_current is False, 'Please provide the current password.'

    account = _validate_cookies(cookies, session=session)

    if current_password is not None:
        if not _verify_password(current_password, account.hashed_password):
            raise ValueError('Incorrect current password.')

    new_password = _sanitize_password(new_password)
    account.hashed_password = _hash_password(new_password)
    account.password_changed = True
    log(f'Modified account: {account}; password has changed', 'account')
    return account


@dbsession()
async def request_delete_account(cookies: Cookies, *, session: _SessionType) -> None:
    """Sends a delete-account request to SUPPORT_EMAIL."""
    account = _validate_cookies(cookies, session=session)
    await send_email(
        subject='Account Deletion Request',
        body=dedent(f'''
            <h2>A customer has requested their account to be deleted.</h2>
            <p>Customer email: {account.email}</p>
        '''),
        sender=SYSTEM_EMAIL,
        recipients=[SUPPORT_EMAIL],
        reply_to=[account.email]
    )
    log(f'Account to be deleted: {account}', 'account')


@dbsession(commit=True)
def delete_account(account_id: int, *, session: _SessionType) -> None:
    """This functions is used by `src.server.scripts.delete_account` to manually delete an account."""
    account = session.get(Account, account_id)
    session.delete(account)


@dbsession()
def get_account_data(cookies: Cookies, *, session: _SessionType) -> dict[str, dict|list]:
    account_id = _validate_cookies(cookies, session=session).account_id
    return {
        'teams': todicts(get_teams(account_id)),
        'employees': todicts(get_employees(account_id)),
        'shifts': todicts(get_shifts(account_id)),
        'holidays': todicts(get_holidays(account_id)),
        'schedules': todicts(get_schedules(account_id)),
        'settings': todict(get_settings(account_id)),
        'invoices': get_invoices(account_id) if _get_active_sub(account_id, session=session) else []
    }




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
    elif utcnow() > retrieved_token_obj.expires_at:
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
async def request_reset_password(email: str, *, session: _SessionType) -> str:
    """Sends a password reset email to users with a password set."""
    email = _sanitize_email(email)
    account = session.query(Account).filter(Account.email == email).first()
    safe_msg = 'If this email exists, a reset link will be sent.'  # Prevents user enumeration attacks
    if not account: return safe_msg

    # Generate a password reset token & send email with reset link
    reset_token = _create_new_token(account.account_id, 'reset', session=session)
    reset_link = f'{WEB_SERVER_URL}/reset-password?token={reset_token}'

    await send_email(
        subject='Reset Your Shiftiatrics Password',
        body=dedent(f'''
            <p>You have sent a password reset request: <a href="{reset_link}">Click here to reset your password</a></p>
            <p>If you have problems with accessing that link, do not hesitate to <a href="{PROD_URL}/support/contact">contact us</a>.</p>
        '''),
        sender=NOREPLY_EMAIL,
        recipients=[account.email]
    )

    return safe_msg


@dbsession(commit=True)
def reset_password(new_password: str, reset_token: str, *, session: _SessionType) -> str:
    """Resets a user's password after verifying the reset token (when logged-out)."""
    new_password = _sanitize_password(new_password)
    email = _get_email_from_token(reset_token, 'reset', session=session)

    # Find the account by email
    account = session.query(Account).filter(Account.email == email).first()
    if not account:
        raise NonExistent('account', email)

    # Hash and store the new password
    account.hashed_password = _hash_password(new_password)
    # Delete the used reset token
    session.query(Token).filter(Token.token == reset_token, Token.token_type == 'reset').delete()
    session.commit()

    return 'Password reset successfully. You can now log in with your new password.'


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
        sender=NOREPLY_EMAIL,
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




## Teams
@dbsession()
def get_teams(account_id: int, *, session: _SessionType) -> list[Team]:
    """Returns all teams under an account."""
    _check_account(account_id, session=session)
    return session.query(Team).filter_by(account_id=account_id).all()


@dbsession()
def get_employees_of_team(team_id: int, *, session: _SessionType) -> list[Employee]:
    """Returns all employees associated that have the given team ID."""
    _check_team(team_id, session=session)
    return session.query(Employee).filter_by(team_id=team_id).all()


@dbsession(commit=True)
def create_team(account_id: int, team_name: str, *, session: _SessionType) -> Team:
    """Creates a team for the given account ID."""
    _check_account(account_id, session=session)
    teams = session.query(Team).filter_by(account_id=account_id).all()
    team = Team(account_id=account_id, team_name=team_name)
    session.add(team)
    log(f'Created team: {Team}', 'db')
    return team


@dbsession(commit=True)
def update_team(team_id: int, updates: dict, *, session: _SessionType) -> Team:
    """Updates an team's attributes based on its ID and the updates."""
    team = _check_team(team_id, session=session)

    ALLOWED_FIELDS = {'team_name'}
    for key, value in updates.items():
        if key not in ALLOWED_FIELDS: raise ValueError(f'"{key}" is not a valid attribute to modify.')
        setattr(team, key, value)

    log(f'Updated employee: {team}, updates: {updates}', 'db')
    return team


@dbsession(commit=True)
def delete_team(team_id: int, *, session: _SessionType) -> None:
    """Deletes the team and its employees."""
    team = _check_team(team_id, session=session)
    emps = session.query(Employee).filter(Employee.team_id == team_id).all()

    for emp in emps:
        _delete_all_holidays_of_employee(emp.employee_id, session=session)
        session.delete(emp)

    session.delete(team)
    log(f'Deleted team: {team}', 'db')




## Employee
@dbsession()
def get_employees(account_id: int, *, session: _SessionType) -> list[Employee]:
    """Returns all employees in the database."""
    _check_account(account_id, session=session)
    return session.query(Employee).filter_by(account_id=account_id).all()


@dbsession(commit=True)
def create_employee(
    account_id: int,
    employee_name: str,
    team_id: int,
    min_work_hours: Optional[int] = None,
    max_work_hours: Optional[int] = None,
    *,
    session: _SessionType
) -> Employee:
    """Creates an employee for the given account ID."""
    _check_account(account_id, session=session)
    min_work_hours, max_work_hours = _check_work_hours(min_work_hours, max_work_hours)
    employee = Employee(
        account_id=account_id,
        employee_name=employee_name,
        team_id=team_id,
        min_work_hours=min_work_hours,
        max_work_hours=max_work_hours
    )
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
    _delete_all_holidays_of_employee(employee_id, session=session)
    session.delete(employee)
    log(f'Deleted employee: {employee}', 'db')




## Shift
@dbsession()
def get_shifts(account_id: int, *, session: _SessionType) -> list[Shift]:
    """Returns all shifts associated with the given account ID."""
    _check_account(account_id, session=session)
    return session.query(Shift).filter_by(account_id=account_id).all()


@dbsession(commit=True)
def create_shift(account_id: int, shift_name: str, start_time: str|time, end_time: str|time, *, session: _SessionType) -> Shift:
    """Creates a shift for the given account ID."""
    _check_account(account_id, session=session)

    if session.query(Shift).filter(Shift.account_id == account_id, Shift.shift_name == shift_name).first():
        raise ValueError(f'Shift with name {shift_name} was already created in your account.')
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
def get_schedules(account_id: int, *, session: _SessionType, **filter_kwargs) -> list[Schedule]:
    """Returns all schedules associated with the given account ID."""
    _check_account(account_id, session=session)
    return session.query(Schedule).filter_by(account_id=account_id, **filter_kwargs).all()


@dbsession(commit=True)
def create_schedule(account_id: int, schedule: ScheduleType, team_id: int, year: int, month: int, *, session: _SessionType) -> Schedule:
    """Creates a schedule for the given account ID."""
    _check_account(account_id, session=session)
    _check_team(team_id, session=session)
    _check_month_and_year(month, year)
    schedule = Schedule(account_id=account_id, team_id=team_id, schedule=schedule, year=year, month=month)
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
def get_holidays(account_id: int, *, session: _SessionType) -> list[Holiday]:
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
def get_settings(account_id: int, *, session: _SessionType) -> Settings:
    """Returns all settings of an account."""
    return session.query(Settings).filter_by(account_id=account_id).first()


@dbsession(commit=True)
def update_setting(account_id: int, setting: str, new_value: SettingValue, *, session: _SessionType) -> Settings:
    """
    Updates a single setting for a given account.

    Args:
        account_id (int): The account ID to update.
        setting (str): The setting attribute to be updated.
        new_value (SettingValue): The new value to set.
        session (_SessionType): Injected DB session.

    Returns:
        SettingValue: The updated setting's value.

    Raises:
        ValueError: If the setting is invalid or the value is incorrect.
    """
    _check_account(account_id, session=session)
    settings = session.query(Settings).filter_by(account_id=account_id).one()

    if not hasattr(Settings, setting):
        raise ValueError(f'Unsupported setting: "{setting}"')

    column = inspect(Settings).columns[setting]

    if new_value is None and not column.nullable:
        raise ValueError(f"{setting} cannot be None")

    try:
        validated_value = _validate_and_cast(setting, new_value, column.type)
    except (ValueError, TypeError) as e:
        raise ValueError(f"Invalid value for {setting}: {e}")

    setattr(settings, setting, validated_value)
    session.add(settings)
    return settings



## Subscription
@dbsession()
def check_sub_expired(account_id: int, *, session: _SessionType) -> bool:
    """Returns a boolean indicating if the account's active subscription has expired and has at least one subscription made in the past."""
    _check_account(account_id, session=session)
    sub = _get_active_sub(account_id, session=session)
    all_subs_count = session.query(Subscription).filter(Subscription.account_id == account_id).count()
    return sub is None and all_subs_count > 0


@dbsession(commit=True)
def create_sub(account_id: int, chkout_session_id: str, *,  session: _SessionType) -> tuple[Account, Subscription]:
    """Creates a subscription for an account in DB."""
    account = _check_account(account_id, session=session)

    if session.query(Subscription).filter(Subscription.stripe_chkout_session_id == chkout_session_id).first():
        raise ValueError('Checkout session ID was processed.')

    # Retrieve the Stripe Checkout Session
    stripe_session = stripe.checkout.Session.retrieve(chkout_session_id)
    if stripe_session.mode != 'subscription': raise ValueError('Session is not a subscription.')

    # Retrieve the actual subscription details
    stripe_subscription_id = stripe_session.subscription
    stripe_customer_id = stripe_session.customer
    stripe_sub = stripe.Subscription.retrieve(stripe_subscription_id)

    # Retrieve plan
    price_obj = stripe_sub['items']['data'][0]['price']
    lookup_key = price_obj.get('lookup_key')
    if not lookup_key: raise LookupError('Missing lookup_key in Stripe price.')
    plan = lookup_key.lower()

    sub = Subscription(
        account_id=account_id,
        plan=plan,
        expires_at=datetime.fromtimestamp(stripe_sub.current_period_end, tz=timezone.utc),
        stripe_subscription_id=stripe_subscription_id,
        stripe_chkout_session_id=chkout_session_id
    )
    session.add(sub)
    account.stripe_customer_id = stripe_customer_id
    log(f'Created {sub} for customer ID {stripe_customer_id}', 'subscription')
    return account, sub


@dbsession()
def get_invoices(account_id: int, *, session: _SessionType) -> list[dict]:
    """Returns all Stripe invoices associated with the given account."""
    account = _check_account(account_id, session=session)
    customer_id = account.stripe_customer_id
    if customer_id is None: raise LookupError(f'Account ID {account_id} does not have a Stripe customer ID.')

    sub = _get_active_sub(account_id, session=session)
    if not sub: raise LookupError(f'No active subscription found for account ID {account_id}.')

    # List all invoices for the specific subscription & customer
    invoices = stripe.Invoice.list(customer=customer_id, subscription=sub.stripe_subscription_id)
    if not invoices.data: raise LookupError(f'No invoices found for Stripe subscription ID "{sub.stripe_subscription_id}".')

    result = [
        {
            'invoice_id': invoice.id,
            'amount_due': invoice.amount_due / 100,
            'amount_paid': invoice.amount_paid / 100,
            'currency': invoice.currency.upper(),
            'status': invoice.status,
            'invoice_pdf': invoice.invoice_pdf,
            'hosted_invoice_url': invoice.hosted_invoice_url,
            'created_at': datetime.fromtimestamp(invoice.created, tz=timezone.utc).isoformat(),
            'due_date': (
                datetime.fromtimestamp(invoice.due_date, tz=timezone.utc).isoformat()
                if invoice.due_date else None
            ),
            'description': invoice.description,
            'subscription_id': invoice.subscription,
        }
        for invoice in invoices.data
    ]
    result.sort(key=lambda invoice: invoice['created_at'], reverse=True)  # Sort newest firsts
    return result