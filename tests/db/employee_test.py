from sqlalchemy import text
import pytest
from src.server.lib.db import Session, create_account, delete_account, get_all_employees_of_account, create_employee, update_employee, delete_employee
from src.server.lib.models import Credentials
from src.server.lib.exceptions import UsernameTaken, AccountDoesNotExist

CRED = Credentials(username='testuser', password='testpass')

@pytest.fixture(scope="function", autouse=True)
def setup_and_teardown():
    # Setup: Create the account
    try: create_account(CRED)
    except UsernameTaken: pass
    yield  # Run the test
    # Teardown: Delete the account & reset the account_id serial sequence
    try: delete_account(CRED)
    except AccountDoesNotExist: pass
    with Session() as session:
        session.execute(text('ALTER SEQUENCE accounts_account_id_seq RESTART WITH 1;'))
        session.commit()


# Tests
def test_create_employee():
    """Test creating an employee."""
    account_id = 1
    employee_name = "John Doe"
    employee = create_employee(account_id, employee_name)
    assert employee.employee_name == employee_name
    assert employee.account_id == account_id


def test_get_all_employees_of_account():
    """Test retrieving all employees."""
    account_id = 1
    employee_name = "John Doe"
    create_employee(account_id, employee_name)
    employees = get_all_employees_of_account(account_id)
    assert len(employees) == 1
    assert employees[0].employee_name == employee_name


def test_update_employee():
    """Test updating an employee."""
    account_id = 1
    employee_name = "John Doe"
    employee = create_employee(account_id, employee_name)
    updates = {"employee_name": "Jane Doe"}
    updated_employee = update_employee(employee.employee_id, updates)
    assert updated_employee.employee_name == "Jane Doe"


def test_delete_employee():
    """Test deleting an employee."""
    account_id = 1
    employee_name = "John Doe"
    employee = create_employee(account_id, employee_name)
    delete_employee(employee.employee_id)
    employees = get_all_employees_of_account(account_id)
    assert len(employees) == 0