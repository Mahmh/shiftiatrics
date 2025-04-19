from typing import Optional, Any
from functools import wraps
from datetime import datetime, timezone
from dataclasses import dataclass, field
from sqlalchemy import text
import pytest
from src.server.rate_limit import limiter
from src.server.lib.models import Credentials
from src.server.db import Session, Account, Token, Team, Employee, Shift, Schedule, Holiday

# Defaults & constants
CRED = Credentials(email='testuser@gmail.com', password='testpass')
signup = lambda client, cred=CRED: client.post('/accounts/signup', json=dict(cred))
login = lambda client, cred=CRED: client.post('/auth/login', json=dict(cred))

EMPLOYEE = {'employee_name': 'John Doe', 'team_id': 1, 'min_work_hours': 140, 'max_work_hours': 180}
SHIFT1 = {'shift_name': 'Day', 'start_time': '08:00', 'end_time': '16:00'}
SHIFT2 = {'shift_name': 'Evening', 'start_time': '16:00', 'end_time': '20:00'}

SCHEDULE = {'schedule': [[[3], [1]], [[2, 3], [1]], [[3, 1], [2]], [[2], [1, 3]]], 'year': 2024, 'month': 11}
delete_schedule = lambda client, schedule_id: client.request('DELETE', f'/schedules/{schedule_id}')

HOLIDAY = {'holiday_name': 'Christmas', 'assigned_to': [2, 1], 'start_date': '2023-12-25', 'end_date': '2023-12-26'}
create_holiday = lambda client, account_id, holiday=HOLIDAY: client.post(f'/holidays/{account_id}', json=holiday)
delete_holiday = lambda client, holiday_id: client.request('DELETE', f'/holidays/{holiday_id}')



# Other utils
def _reset_whole_db() -> None:
    """Resets the DB auto-increment sequence of SERIAL columns, and deletes all rows from all tables."""
    with Session() as session:
        session.query(Token).delete()
        session.query(Employee).delete()
        session.query(Team).delete()
        session.query(Shift).delete()
        session.query(Schedule).delete()
        session.query(Holiday).delete()
        session.query(Account).delete()
        session.commit()
        session.execute(text('ALTER SEQUENCE accounts_account_id_seq RESTART WITH 1;'))
        session.execute(text('ALTER SEQUENCE tokens_token_id_seq RESTART WITH 1;'))
        session.execute(text('ALTER SEQUENCE teams_team_id_seq RESTART WITH 1;'))
        session.execute(text('ALTER SEQUENCE employees_employee_id_seq RESTART WITH 1;'))
        session.execute(text('ALTER SEQUENCE shifts_shift_id_seq RESTART WITH 1;'))
        session.execute(text('ALTER SEQUENCE holidays_holiday_id_seq RESTART WITH 1;'))
        session.execute(text('ALTER SEQUENCE schedules_schedule_id_seq RESTART WITH 1;'))
        session.execute(text('ALTER SEQUENCE subscriptions_subscription_id_seq RESTART WITH 1;'))
        session.commit()


def ctxtest(*, disable_rate_limiting: bool = True):
    """
    Decorator to reset the database after executing a test and optionally disable rate limiting for tests.
    Its wrapped function is executed before and optionally tears down after every test.
    """
    def decorator(testfunc):
        @pytest.fixture(scope='function', autouse=True)
        @wraps(testfunc)
        def fixture_wrapper(*args, **kwargs):
            _reset_whole_db()
            limiter.reset()
            if disable_rate_limiting:
                limiter.enabled = False
            try:
                result = next(testfunc(*args, **kwargs))  # Get the yielded value
                yield result
            finally:
                if disable_rate_limiting:
                    limiter.enabled = True
                _reset_whole_db()
        return fixture_wrapper
    return decorator



# Mock models
@dataclass
class FakeStripeCheckoutSession:
    id: str = 'cs_test_123'
    url: str = 'https://checkout.stripe.com/pay/cs_test_123'
    mode: str = 'subscription'
    customer: str = 'cus_test_abc'
    subscription: str = 'sub_test_abc'


@dataclass
class FakeStripeSubscription:
    unit_amount: int = 4900
    lookup_key: str = 'advanced'
    status: str = 'active'
    period_end: Optional[datetime] = None
    items: Optional[dict[str, Any]] = None  # Allow override
    current_period_end: int = field(init=False)

    def __post_init__(self):
        self.period_end = self.period_end or datetime(2025, 12, 1, tzinfo=timezone.utc)
        if self.items is None:
            self.items = {
                'data': [{
                    'price': {'unit_amount': self.unit_amount, 'lookup_key': self.lookup_key}
                }]
            }
        self.current_period_end = int(self.period_end.timestamp())

    def __getitem__(self, key):
        return getattr(self, key)