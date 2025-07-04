from typing import Any, Optional
from functools import wraps
from fastapi import Request, Response
from src.server.db import Account, Subscription, Employee, Shift, Schedule, Holiday, Settings, log_in_account_with_cookies, check_sub_expired
from src.server.lib.constants import COOKIE_DOMAIN, TOKEN_EXPIRY_SECONDS
from src.server.lib.models import Cookies
from src.server.lib.utils import log, errlog, todict, todicts
from src.server.lib.exceptions import CookiesUnavailable, InvalidCookies, EndpointAuthError, NonExistent, EmailTaken

## Private
def _authenticate(kwargs: dict[str, Any]) -> Optional[dict[str, str]]:
    """Requires credentials (in cookies) to prevent unauthorized clients from accessing sensitive endpoints."""
    try:
        cookies = get_cookies(kwargs['request'])
        account = log_in_account_with_cookies(cookies)[0]
        if 'account_id' in kwargs:
            if account.account_id != kwargs['account_id']:
                raise EndpointAuthError()
    except (CookiesUnavailable, InvalidCookies) as e:
        raise EndpointAuthError() from e


def _handle_return_type(result: Any) -> dict | list[dict] | Any:
    """Converts a given type to a data type that is suitable to be an API response."""
    if type(result) in (Account, Subscription, Employee, Shift, Schedule, Holiday, Settings):
        return todict(result)
    elif type(result) is list:
        try: return todicts(result)
        except: return result
    return result


def _set_cookie(key: str, value: str, response: Response) -> None:
    """Stores a cookie with a given value."""
    response.set_cookie(
        key=key,
        value=value,
        httponly=True,
        secure=False,
        samesite='strict',
        domain=COOKIE_DOMAIN,
        max_age=TOKEN_EXPIRY_SECONDS
    )


## Public
def endpoint(*, auth: bool = True):
    """If `auth` is true, then the wrapped endpoint requires credentials via cookies."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                if auth: _authenticate(kwargs)
                result = await func(*args, **kwargs)
                return _handle_return_type(result)
            except Exception as e:
                errlog(func.__name__, e, 'api')
                if type(e) is NonExistent and e.entity == 'account':
                    return {'error': 'Invalid credentials'}
                elif type(e) is EmailTaken:
                    return {'error': 'Something went wrong. Please try again or use a different email.'}
                return {'error': str(e)}
        return wrapper
    return decorator


def get_cookies(request: Request) -> Cookies:
    """Returns the email & authentication token stored in the client's cookies."""
    try:
        return Cookies(account_id=int(request.cookies.get('account_id')), token=request.cookies.get('auth_token'))
    except (TypeError, ValueError):
        return Cookies(account_id=None, token=request.cookies.get('token'))


def clear_cookies(response: Response) -> None:
    """Deletes the auth cookies."""
    response.delete_cookie('account_id', httponly=True)
    response.delete_cookie('auth_token', httponly=True)


def store_cookies(cookies: Cookies, response: Response) -> None:
    """Stores the given email & authentication token as HttpOnly cookies in the client."""
    if not cookies.available(): raise CookiesUnavailable(cookies)
    log(f'Storing cookies: {cookies}', 'auth')
    _set_cookie('account_id', cookies.account_id, response)
    _set_cookie('auth_token', cookies.token, response)


def return_account_and_sub(account: Account, sub: Optional[Subscription] = None) -> dict:
    """Returns an API response dictionary with the given account and nullable subscription converted to dictionaries, with additional info given to `account`."""
    return {
        'account': todict(account, sub_expired=check_sub_expired(account.account_id)),
        'subscription': todict(sub)
    }


def check_legal_agree(legal_agree: bool) -> None:
    """Raises an error if the user has not agreed to the terms, conditions, privacy policy, and cookie policy."""
    if legal_agree is False:
        raise Exception('You must agree to the terms, conditions, privacy policy, and cookie policy to set up an account by checking the checkbox above.')