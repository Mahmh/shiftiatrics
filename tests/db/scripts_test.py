import subprocess, pytest
from src.server.lib.models import Cookies
from src.server.db import create_account, get_employees, get_shifts
from tests.utils import ctxtest, CRED

# Init
@ctxtest()
def setup_and_teardown():
    account, token = create_account(CRED)
    yield Cookies(account_id=account.account_id, token=token)


# Tests
def test_create_employee(setup_and_teardown):
    cookies = setup_and_teardown
    account_id = cookies.account_id

    result = subprocess.run(
        [
            'python3', '-m', 'src.server.scripts.create_employee',
            '--account_id', str(account_id),
            '--employee_name', 'Dr. Alice',
            '--min_work_hours', '100',
            '--max_work_hours', '160'
        ],
        capture_output=True,
        text=True
    )
    print(result.stdout, result.stderr, end='')

    emps = get_employees(account_id)
    assert result.returncode == 0
    assert '✅' in result.stdout
    assert len(emps) == 1
    assert emps[0].employee_name == 'Dr. Alice'


def test_create_shift(setup_and_teardown):
    cookies = setup_and_teardown
    account_id = cookies.account_id

    result = subprocess.run(
        [
            'python3', '-m', 'src.server.scripts.create_shift',
            '--account_id', str(account_id),
            '--shift_name', 'D',
            '--start_time', '08:00',
            '--end_time', '16:00'
        ],
        capture_output=True,
        text=True
    )
    print(result.stdout, result.stderr, end='')

    shifts = get_shifts(account_id)
    assert result.returncode == 0
    assert '✅' in result.stdout
    assert len(shifts) == 1
    assert shifts[0].shift_name == 'D'


def test_create_checkout_url():
    STARTER_PLAN_PRICE_ID = 'price_1R57GALcPBGZy9UcVui6CMG9'

    # Mock checkout session creation
    result = subprocess.run(
        [
            'python3', '-m', 'src.server.scripts.create_checkout_url',
            '--price_id', STARTER_PLAN_PRICE_ID
        ],
        capture_output=True,
        text=True
    )
    print(result.stdout, result.stderr, end='')

    assert result.returncode == 0
    assert '✅' in result.stdout


@pytest.mark.parametrize('script, args', [
    (
        'src.server.scripts.create_employee',
        ['--account_id', '9999', '--employee_name', 'Ghost', '--min_work_hours', '100', '--max_work_hours', '160']
    ),
    (
        'src.server.scripts.create_shift',
        ['--account_id', '9999', '--shift_name', 'G', '--start_time', '09:00', '--end_time', '17:00']
    ),
    (
        'src.server.scripts.create_checkout_url',
        ['--price_id', 'price_id_invalid']
    )
])
def test_scripts_invalid_account(script, args):
    result = subprocess.run(
        ['python3', '-m', script] + args,
        capture_output=True,
        text=True
    )
    print(result.stdout, result.stderr, end='')
    assert result.returncode == 0
    assert '❌' in result.stdout or '❌' in result.stderr