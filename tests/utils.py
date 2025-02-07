from sqlalchemy import text
from functools import wraps
import pytest
from src.server.lib.db import Session, Account, Token, Employee, Shift, Schedule, Holiday
from src.server.rate_limit import limiter

def _reset_whole_db() -> None:
    """Resets the DB auto-increment sequence of SERIAL columns, and deletes all rows from all tables."""
    with Session() as session:
        session.query(Token).delete()
        session.query(Employee).delete()
        session.query(Shift).delete()
        session.query(Schedule).delete()
        session.query(Holiday).delete()
        session.query(Account).delete()
        session.commit()
        session.execute(text('ALTER SEQUENCE accounts_account_id_seq RESTART WITH 1;'))
        session.execute(text('ALTER SEQUENCE employees_employee_id_seq RESTART WITH 1;'))
        session.execute(text('ALTER SEQUENCE shifts_shift_id_seq RESTART WITH 1;'))
        session.execute(text('ALTER SEQUENCE holidays_holiday_id_seq RESTART WITH 1;'))
        session.execute(text('ALTER SEQUENCE schedules_schedule_id_seq RESTART WITH 1;'))
        session.commit()


def ctxtest(*, disable_rate_limiting: bool = True):
    """Decorator to reset the database and optionally disable rate limiting for tests."""
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
                yield result  # Correctly yield the tuple
            finally:
                if disable_rate_limiting:
                    limiter.enabled = True
                _reset_whole_db()
        return fixture_wrapper
    return decorator