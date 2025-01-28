from typing import LiteralString, Optional
from fastapi import Response
from fastapi.testclient import TestClient
import pytest, random, string
from src.server.main import app
from src.server.lib.db import reset_whole_db
from src.server.rate_limit import limiter

# Init
client = TestClient(app)
CRED = {'username': 'testuser', 'password': 'testpass'}
create_account = lambda: client.post('/accounts/signup', json=CRED)
login = lambda: client.post('/accounts/login', json=CRED)

@pytest.fixture(scope='function', autouse=True)
def setup_and_teardown():
    limiter.reset()
    reset_whole_db()
    create_account()
    yield
    reset_whole_db()


def _generate_random_credentials() -> dict[str, str]:
    username = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
    return {'username': username, 'password': password}


def _handle_client_cookies(cookies: dict) -> None:
    client.cookies.clear()
    for key, value in cookies.items():
        client.cookies.set(key, value)


def hit_endpoint(endpoint: str, method: LiteralString = 'get', json: Optional[dict] = None, cookies: Optional[dict] = None) -> Response:
    """Helper function to spam requests to an endpoint."""
    if cookies: _handle_client_cookies(cookies)

    for i in range(31):
        if endpoint == '/accounts/signup':
            json = _generate_random_credentials()

        if method == 'get': response = client.get(endpoint)
        elif method == 'post': response = client.post(endpoint, json=json)
        elif method == 'patch': response = client.patch(endpoint, json=json)
        elif method == 'delete': response = client.delete(endpoint)

        # 29 because create_account was already called beforehand
        if (i < 30 and endpoint != '/accounts/signup') or (i < 29 and endpoint == '/accounts/signup'):
            assert response.status_code == 200
    return response


# Tests
def test_rate_limit_signup():
    response = hit_endpoint('/accounts/signup', method='post', json=CRED)
    assert response.status_code == 429


def test_rate_limit_login():
    response = hit_endpoint('/accounts/login', method='post', json=CRED)
    assert response.status_code == 429


def test_rate_limit_generate_schedule():
    login_response = login()
    response = hit_endpoint('/engine/generate_schedule?account_id=1&num_days=7&year=2023&month=10', cookies=login_response.cookies)
    assert response.status_code == 429


def test_rate_limit_get_shift_counts_of_employees():
    login_response = login()
    response = hit_endpoint('/engine/get_shift_counts_of_employees?account_id=1&year=2023&month=10', cookies=login_response.cookies)
    assert response.status_code == 429


def test_rate_limit_get_work_hours_of_employees():
    login_response = login()
    response = hit_endpoint('/engine/get_work_hours_of_employees?account_id=1&year=2023&month=10', cookies=login_response.cookies)
    assert response.status_code == 429


def test_rate_limit_create_employee():
    login_response = login()
    employee_info = {'employee_name': 'John Doe', 'min_work_hours': 20, 'max_work_hours': 40}
    response = hit_endpoint('/accounts/1/employees', method='post', json=employee_info, cookies=login_response.cookies)
    assert response.status_code == 429


def test_rate_limit_create_shift():
    login_response = login()
    shift_info = {'shift_name': 'Morning Shift', 'start_time': '08:00', 'end_time': '16:00'}
    response = hit_endpoint('/accounts/1/shifts', method='post', json=shift_info, cookies=login_response.cookies)
    assert response.status_code == 429


def test_rate_limit_create_schedule():
    login_response = login()
    schedule_info = {'schedule': [[[1], [2]], [[3], [4]]], 'month': 10, 'year': 2023}
    response = hit_endpoint('/accounts/1/schedules', method='post', json=schedule_info, cookies=login_response.cookies)
    assert response.status_code == 429


def test_rate_limit_create_holiday():
    login_response = login()
    holiday_info = {'holiday_name': 'Christmas', 'assigned_to': [1, 2], 'start_date': '2023-12-24', 'end_date': '2023-12-26'}
    response = hit_endpoint('/accounts/1/holidays', method='post', json=holiday_info, cookies=login_response.cookies)
    assert response.status_code == 429