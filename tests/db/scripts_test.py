from datetime import timedelta
import subprocess, pytest
from src.server.lib.models import Cookies
from src.server.lib.utils import utcnow
from src.server.db import create_account, get_all_employees_of_account, get_all_shifts_of_account, log_in_account_with_cookies
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
    print(result.stdout, result.stderr)

    emps = get_all_employees_of_account(account_id)
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
    print(result.stdout, result.stderr)

    shifts = get_all_shifts_of_account(account_id)
    assert result.returncode == 0
    assert '✅' in result.stdout
    assert len(shifts) == 1
    assert shifts[0].shift_name == 'D'


def test_create_sub(setup_and_teardown):
    cookies = setup_and_teardown
    account_id = cookies.account_id

    result = subprocess.run(
        [
            'python3', '-m', 'src.server.scripts.create_sub',
            '--account_id', str(account_id),
            '--plan', 'starter',
            '--expires_at', '2025-11-23',
            '--stripe_customer_id', 'cus_test123',
            '--stripe_subscription_id', 'sub_test123'
        ],
        capture_output=True,
        text=True
    )
    print(result.stdout, result.stderr)

    sub = log_in_account_with_cookies(cookies)[1]
    assert result.returncode == 0
    assert '✅' in result.stdout
    assert sub is not None
    assert sub.plan.value == 'starter'


@pytest.mark.parametrize('script, args', [
    (
        'src.server.scripts.create_employee',
        ['--account_id', '999999', '--employee_name', 'Ghost', '--min_work_hours', '100', '--max_work_hours', '160']
    ),
    (
        'src.server.scripts.create_shift',
        ['--account_id', '999999', '--shift_name', 'G', '--start_time', '09:00', '--end_time', '17:00']
    ),
    (
        'src.server.scripts.create_sub',
        [
            '--account_id', '999999',
            '--plan', 'starter',
            '--expires_at', (utcnow() + timedelta(days=30)).isoformat(),
            '--stripe_customer_id', 'cus_ghost',
            '--stripe_subscription_id', 'sub_ghost'
        ]
    )
])
def test_scripts_invalid_account(script, args):
    result = subprocess.run(
        ['python3', '-m', script] + args,
        capture_output=True,
        text=True
    )
    print(result.stdout, result.stderr)
    assert result.returncode == 0  # Script runs, but fails internally
    assert '❌' in result.stdout or '❌' in result.stderr