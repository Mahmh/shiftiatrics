from fastapi.testclient import TestClient
from src.server.main import app
from src.server.lib.types import WeekendDaysEnum
from tests.utils import ctxtest, signup

# Init
client = TestClient(app)

@ctxtest()
def setup_and_teardown():
    account_id = signup(client).json()['account']['account_id']
    yield account_id

def _patch_setting(account_id: int, setting: str, new_value):
    return client.patch(
        f'/settings/{account_id}',
        json={'setting': setting, 'new_value': new_value}
    )


# Tests
def test_read_settings(setup_and_teardown):
    account_id = setup_and_teardown
    response = client.get(f'/settings/{account_id}')
    assert response.status_code == 200
    assert response.json()['account_id'] == account_id


def test_dark_theme_toggle(setup_and_teardown):
    account_id = setup_and_teardown

    r1 = _patch_setting(account_id, 'dark_theme_enabled', True)
    assert r1.status_code == 200
    assert r1.json()['dark_theme_enabled'] is True

    r2 = _patch_setting(account_id, 'dark_theme_enabled', False)
    assert r2.status_code == 200
    assert r2.json()['dark_theme_enabled'] is False


def test_update_weekend_days(setup_and_teardown):
    account_id = setup_and_teardown
    r = _patch_setting(account_id, 'weekend_days', WeekendDaysEnum.FRI_SAT.value)
    assert r.status_code == 200
    assert r.json()['weekend_days'] == WeekendDaysEnum.FRI_SAT.value