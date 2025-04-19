from src.server.lib.models import Credentials
from src.server.db import create_account, create_employee, get_employees_of_team, create_team, get_teams, update_team, delete_team
from tests.utils import ctxtest, CRED

# Init
@ctxtest()
def setup_and_teardown():
    account_id = create_account(CRED)[0].account_id
    yield account_id


# Tests
def test_get_employees_of_team(setup_and_teardown):
    account_id = setup_and_teardown
    team1 = create_team(account_id, 'Team 1')
    team2 = create_team(account_id, 'Team 2')
    emp1 = create_employee(account_id, 'A', team1.team_id)
    emp2 = create_employee(account_id, 'A', team2.team_id)

    emps1 = get_employees_of_team(team1.team_id)
    assert len(emps1) == 1
    assert emps1[0].employee_name == emp1.employee_name

    emps2 = get_employees_of_team(team2.team_id)
    assert len(emps2) == 1
    assert emps2[0].employee_name == emp2.employee_name


def test_create_team(setup_and_teardown):
    account_id = setup_and_teardown
    team = create_team(account_id, 'Alpha Team')
    assert team.team_name == 'Alpha Team'
    assert team.account_id == account_id


def test_get_teams(setup_and_teardown):
    account_id = setup_and_teardown
    create_team(account_id, 'Beta Team')
    teams = get_teams(account_id)
    assert len(teams) == 1
    assert teams[0].team_name == 'Beta Team'


def test_update_team(setup_and_teardown):
    account_id = setup_and_teardown
    team = create_team(account_id, 'Gamma Team')
    updates = {'team_name': 'Delta Team'}
    updated = update_team(team.team_id, updates)
    assert updated.team_name == 'Delta Team'


def test_delete_team(setup_and_teardown):
    account_id = setup_and_teardown
    team = create_team(account_id, 'Epsilon Team')
    delete_team(team.team_id)
    teams = get_teams(account_id)
    assert len(teams) == 0