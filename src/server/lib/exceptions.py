from typing import Literal
from src.server.lib.models import Credentials

class UsernameTaken(Exception):
    """Exception for entering an existing username."""
    def __init__(self, username: str):
        super().__init__(f'Username "{username}" is already registered.')


class InvalidCredentials(Exception):
    """Exception for entering invalid credentials."""
    def __init__(self, cred: Credentials):
        super().__init__(f'Invalid credentials: username={cred.username}, password={cred.password}')


class NonExistent(Exception):
    """Exception for non-existent entities."""
    def __init__(self, entity: Literal['account', 'employee', 'shift', 'schedule', 'setting'], identifier: str|int):
        self.entity = entity
        msg = ''
        if type(identifier) is int: msg = f'{entity.title()} with ID "{identifier}" does not exist.'
        else: msg = f'{entity.title()} with name "{identifier}" does not exist.'
        super().__init__(msg)