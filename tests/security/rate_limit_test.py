from typing import LiteralString, Optional
from fastapi import Response
from fastapi.testclient import TestClient
import random, string
from src.server.main import app
from src.server.lib.models import Credentials
from src.server.db import create_team
from tests.utils import ctxtest, login, signup, CRED

# Init
client = TestClient(app)

@ctxtest(disable_rate_limiting=False)
def setup_and_teardown():
    account_id = signup(client).json()['account']['account_id']
    create_team(account_id, 'Test Team')
    yield


def _handle_client_cookies(cookies: dict) -> None:
    client.cookies.clear()
    for key, value in cookies.items():
        client.cookies.set(key, value)


def _generate_random_cred() -> dict[str, str]:
    email = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
    cred = Credentials(email=email, password=password)
    return dict(cred)


def hit_endpoint(endpoint: str, method: LiteralString = 'get', times=30, json: Optional[dict] = None, cookies: Optional[dict] = None) -> Response:
    """Helper function to spam requests to an endpoint."""
    if cookies: _handle_client_cookies(cookies)

    for i in range(times+1):
        if method == 'get': response = client.get(endpoint)
        elif method == 'post': response = client.post(endpoint, json=json)
        elif method == 'patch': response = client.patch(endpoint, json=json)
        elif method == 'delete': response = client.delete(endpoint)

        # 29 because signup was already called beforehand
        if (i < times and endpoint != '/accounts/signup') or (i < (times-1) and endpoint == '/accounts/signup'):
            assert response.status_code == 200
    return response


# Tests
def test_rate_limit_signup():
    response = hit_endpoint('/accounts/signup', method='post', times=10, json={'cred': _generate_random_cred(), 'legal_agree': True})
    assert response.status_code == 429


def test_rate_limit_login():
    response = hit_endpoint('/auth/login', method='post', times=5, json=dict(CRED))
    assert response.status_code == 429


def test_rate_limit_generate_schedule():
    login_response = login(client)
    response = hit_endpoint('/engine/generate_schedule?account_id=1&num_days=7&year=2023&month=10', cookies=login_response.cookies)
    assert response.status_code == 429


def test_rate_limit_get_shift_counts_of_employees():
    login_response = login(client)
    response = hit_endpoint('/engine/get_shift_counts_of_employees?account_id=1&team_id=1&year=2023&month=10', cookies=login_response.cookies)
    assert response.status_code == 429


def test_rate_limit_get_work_hours_of_employees():
    login_response = login(client)
    response = hit_endpoint('/engine/get_work_hours_of_employees?account_id=1&team_id=1&year=2023&month=10', cookies=login_response.cookies)
    assert response.status_code == 429


def test_rate_limit_create_holiday():
    login_response = login(client)
    holiday_info = {'holiday_name': 'Christmas', 'assigned_to': [1, 2], 'start_date': '2023-12-24', 'end_date': '2023-12-26'}
    response = hit_endpoint('/holidays/1', method='post', json=holiday_info, cookies=login_response.cookies)
    assert response.status_code == 429