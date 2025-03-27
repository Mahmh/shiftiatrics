import pytest
from src.server.db import create_account, get_all_employees_of_account, create_employee, update_employee, delete_employee
from tests.utils import ctxtest, CRED

# Init
@ctxtest()
def setup_and_teardown():
    account_id = create_account(CRED)[0].account_id
    yield account_id


# Tests
def test_create_employee(setup_and_teardown):
    '''Test creating an employee.'''
    account_id = setup_and_teardown
    employee_name = 'John Doe'
    employee = create_employee(account_id, employee_name)
    assert employee.employee_name == employee_name
    assert employee.account_id == account_id


def test_get_all_employees_of_account(setup_and_teardown):
    '''Test retrieving all employees.'''
    account_id = setup_and_teardown
    employee_name = 'John Doe'
    create_employee(account_id, employee_name)
    employees = get_all_employees_of_account(account_id)
    assert len(employees) == 1
    assert employees[0].employee_name == employee_name


def test_update_employee(setup_and_teardown):
    '''Test updating an employee.'''
    account_id = setup_and_teardown
    employee_name = 'John Doe'
    employee = create_employee(account_id, employee_name)
    updates = {'employee_name': 'Jane Doe'}
    updated_employee = update_employee(employee.employee_id, updates)
    assert updated_employee.employee_name == 'Jane Doe'


def test_delete_employee(setup_and_teardown):
    '''Test deleting an employee.'''
    account_id = setup_and_teardown
    employee_name = 'John Doe'
    employee = create_employee(account_id, employee_name)
    delete_employee(employee.employee_id)
    employees = get_all_employees_of_account(account_id)
    assert len(employees) == 0


def test_exceed_max_num_pediatricians_in_free_tier(setup_and_teardown):
    account_id = setup_and_teardown
    with pytest.raises(ValueError, match='max'):
        for name in 'abcdefg':
            create_employee(account_id, name)