from src.server.db import create_account, get_employees, create_employee, update_employee, delete_employee
from tests.utils import ctxtest, CRED, EMPLOYEE

# Init
@ctxtest()
def setup_and_teardown():
    account_id = create_account(CRED)[0].account_id
    yield account_id


# Tests
def test_create_employee(setup_and_teardown):
    '''Test creating an employee.'''
    account_id = setup_and_teardown
    employee = create_employee(account_id, **EMPLOYEE)
    assert employee.employee_name == EMPLOYEE['employee_name']
    assert employee.account_id == account_id


def test_get_employees(setup_and_teardown):
    '''Test retrieving all employees.'''
    account_id = setup_and_teardown
    create_employee(account_id, **EMPLOYEE)
    employees = get_employees(account_id)
    assert len(employees) == 1
    assert employees[0].employee_name == EMPLOYEE['employee_name']


def test_update_employee(setup_and_teardown):
    '''Test updating an employee.'''
    account_id = setup_and_teardown
    employee = create_employee(account_id, **EMPLOYEE)
    updates = {'employee_name': 'Jane Doe'}
    updated_employee = update_employee(employee.employee_id, updates)
    assert updated_employee.employee_name == updates['employee_name']


def test_delete_employee(setup_and_teardown):
    '''Test deleting an employee.'''
    account_id = setup_and_teardown
    employee = create_employee(account_id, **EMPLOYEE)
    delete_employee(employee.employee_id)
    employees = get_employees(account_id)
    assert len(employees) == 0