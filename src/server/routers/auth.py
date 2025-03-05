from urllib.parse import urlencode
from fastapi import APIRouter, HTTPException, Request, Response, Query, Body
from fastapi.responses import RedirectResponse
import httpx, jwt
from src.server.rate_limit import limiter
from src.server.db import log_in_with_google
from src.server.lib.models import Credentials, Cookies
from src.server.lib.api import endpoint, get_cookies, store_cookies, clear_cookies, store_cookies_then_redirect
from src.server.db.functions import log_in_account, log_in_account_with_cookies, request_reset_password, reset_password
from src.server.lib.constants import (
    WEB_SERVER_URL,
    DEFAULT_RATE_LIMIT,
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    GOOGLE_AUTH_URL,
    GOOGLE_REDIRECT_URI,
    GOOGLE_TOKEN_URL
)

auth_router = APIRouter()


@auth_router.get('/auth/log_in_account_with_cookies')
@limiter.limit(DEFAULT_RATE_LIMIT)
@endpoint(auth=False)
async def log_in_account_with_cookies_(request: Request) -> dict:
    cookies = get_cookies(request)
    if cookies.account_id is None: return {'error': 'Account ID is either invalid or not found'}
    elif cookies.token is None: return {'error': 'Token is either invalid or not found'}
    else: return log_in_account_with_cookies(cookies)


@auth_router.post('/auth/login')
@limiter.limit('5/minute')
@endpoint(auth=False)
async def login_account(cred: Credentials, response: Response, request: Request) -> dict:
    account, token = log_in_account(cred)
    store_cookies(Cookies(account_id=account.account_id, token=token), response)
    return account


@auth_router.get('/auth/logout')
@limiter.limit('5/minute')
@endpoint(auth=False)
async def logout_account(response: Response, request: Request) -> dict:
    clear_cookies(response)
    return {'detail': 'Logged out successfully'}


@auth_router.post('/auth/request_reset_password')
@limiter.limit('3/minute')
@endpoint(auth=False)
async def request_reset_password_(request: Request, email: str = Body(..., embed=True)) -> dict:
    return {'detail': await request_reset_password(email)}


@auth_router.put('/auth/reset_password')
@limiter.limit('3/minute')
@endpoint(auth=False)
async def reset_password_(request: Request, new_password: str = Body(..., embed=True), reset_token: str = Body(..., embed=True)) -> dict:
    return {'detail': reset_password(new_password, reset_token)}



## OAuth
@auth_router.get('/auth/google')
@limiter.limit(DEFAULT_RATE_LIMIT)
@endpoint(auth=False)
async def continue_with_google(request: Request) -> dict:
    '''Redirects users to Google's OAuth login page'''
    params = {
        'client_id': GOOGLE_CLIENT_ID,
        'response_type': 'code',
        'scope': 'email',
        'redirect_uri': GOOGLE_REDIRECT_URI,
        'access_type': 'online'
    }
    return {'login_url': f'{GOOGLE_AUTH_URL}?{urlencode(params)}'}


@auth_router.get('/auth/google/callback')
@limiter.limit(DEFAULT_RATE_LIMIT)
@endpoint(auth=False)
async def google_callback(request: Request, code: str = Query(None), error: str = Query(None)) -> RedirectResponse:
    '''Handles Google's OAuth callback, gets user info, and starts a session.'''
    if error or code is None:
        return RedirectResponse(WEB_SERVER_URL)

    async with httpx.AsyncClient() as client:
        # Exchange code for access token
        token_response = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                'client_id': GOOGLE_CLIENT_ID,
                'client_secret': GOOGLE_CLIENT_SECRET,
                'code': code,
                'grant_type': 'authorization_code',
                'redirect_uri': GOOGLE_REDIRECT_URI,
            },
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )

    if token_response.status_code != 200:
        raise HTTPException(status_code=400, detail='Failed to get access token')

    token_data = token_response.json()
    access_token = token_data.get('access_token')
    id_token = token_data.get('id_token')  # ID Token for verification

    # Verify & Decode ID Token to get the OAuth ID (`sub`)
    decoded_id_token = jwt.decode(id_token, options={'verify_signature': False})
    oauth_id = decoded_id_token.get('sub')
    email = decoded_id_token.get('email')
    if not oauth_id:
        raise HTTPException(status_code=400, detail='Invalid ID token')

    account, token = log_in_with_google(email, access_token, oauth_id)
    return store_cookies_then_redirect(Cookies(account_id=account.account_id, token=token))