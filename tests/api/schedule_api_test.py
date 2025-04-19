from fastapi.testclient import TestClient
from src.server.main import app
from src.server.lib.models import Credentials
from src.server.db import create_team, create_schedule, create_employee, create_shift
from tests.utils import ctxtest, signup, delete_schedule

# Init
client = TestClient(app)
CRED2 = Credentials(email='abc@somemail.com', password='somepass')
SCHEDULE = {'schedule': [[[1, 2], [3, 4]]], 'year': 2023, 'month': 5}

@ctxtest()
def setup_and_teardown():
    account_id = signup(client).json()['account']['account_id']
    team_id = create_team(account_id, 'Test Team').team_id
    schedule_id = create_schedule(account_id, team_id=team_id, **SCHEDULE).schedule_id
    create_employee(account_id, 'John', 1)
    create_shift(account_id, 'Morning', '06:00', '12:00')
    yield account_id, team_id, schedule_id


# Tests
def test_read_schedules(setup_and_teardown):
    account_id, _, _ = setup_and_teardown
    response = client.get(f'/schedules/{account_id}')
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_new_schedule(setup_and_teardown):
    account_id, team_id, _ = setup_and_teardown
    new_data = {'schedule': [[[5, 6], [7]]], 'year': 2025, 'month': 7}
    updated_data = create_schedule(account_id, team_id=team_id, **new_data)

    assert updated_data.schedule == new_data['schedule']
    assert updated_data.month == new_data['month']
    assert updated_data.year == new_data['year']
    delete_schedule(client, updated_data.schedule_id)


def test_delete_existing_schedule(setup_and_teardown):
    _, _, schedule_id = setup_and_teardown
    response = delete_schedule(client, schedule_id)
    assert response.status_code == 200
    assert response.json()['detail'] == 'Schedule deleted successfully'


def test_unimplemented_algorithm_for_account():
    r1 = signup(client, CRED2)
    assert r1.status_code == 200
    new_account_id = r1.json()['account']['account_id']
    assert new_account_id == 2

    team2 = create_team(new_account_id, 'Test Team2')
    create_employee(new_account_id, 'John2', team2.team_id)
    create_shift(new_account_id, 'Morning2', '06:00', '12:00')

    r2 = client.get(f'/engine/generate_schedule?account_id={new_account_id}&num_days=31&year=2024&month=7')
    assert r2.status_code == 200
    assert 'not yet implemented' in r2.json()['error']