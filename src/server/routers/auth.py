from fastapi import APIRouter, Request, Response, Body
from src.server.rate_limit import limiter
from src.server.lib.models import Credentials, Cookies
from src.server.lib.api import endpoint, get_cookies, store_cookies, clear_cookies, return_account_and_sub
from src.server.db import log_in_account, log_in_account_with_cookies, request_reset_password, reset_password, request_verify_email, verify_email

auth_router = APIRouter(prefix='/auth')

@auth_router.get('/log_in_account_with_cookies')
@limiter.limit('30/minute')
@endpoint(auth=False)
async def log_in_account_with_cookies_(request: Request) -> dict:
    cookies = get_cookies(request)
    if cookies.account_id is None:
        return {'error': 'Account ID is either invalid or not found'}
    elif cookies.token is None:
        return {'error': 'Token is either invalid or not found'}
    else:
        account, sub = log_in_account_with_cookies(cookies)
        return return_account_and_sub(account, sub)


@auth_router.post('/login')
@limiter.limit('5/minute')
@endpoint(auth=False)
async def login_account(cred: Credentials, response: Response, request: Request) -> dict:
    account, sub, token = log_in_account(cred)
    store_cookies(Cookies(account_id=account.account_id, token=token), response)
    return return_account_and_sub(account, sub)


@auth_router.get('/logout')
@limiter.limit('5/minute')
@endpoint(auth=False)
async def logout_account(response: Response, request: Request) -> dict:
    clear_cookies(response)
    return {'detail': 'Logged out successfully'}


@auth_router.post('/request_reset_password')
@limiter.limit('3/minute')
@endpoint(auth=False)
async def request_reset_password_(request: Request, email: str = Body(..., embed=True)) -> dict:
    return {'detail': await request_reset_password(email)}


@auth_router.patch('/reset_password')
@limiter.limit('3/minute')
@endpoint(auth=False)
async def reset_password_(request: Request, new_password: str = Body(..., embed=True), reset_token: str = Body(..., embed=True)) -> dict:
    return {'detail': reset_password(new_password, reset_token)}


@auth_router.post('/request_verify_email')
@limiter.limit('3/minute')
@endpoint()
async def request_verify_email_(request: Request, email: str = Body(..., embed=True)) -> dict:
    return {'detail': await request_verify_email(email)}


@auth_router.patch('/verify_email')
@limiter.limit('3/minute')
@endpoint(auth=False)
async def verify_email_(request: Request, verify_token: str = Body(..., embed=True)) -> dict:
    return {'detail': verify_email(verify_token)}