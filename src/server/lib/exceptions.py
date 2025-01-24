from typing import Literal
from src.server.lib.models import Credentials, Cookies

class UsernameTaken(Exception):
    """Exception for entering an existing username."""
    def __init__(self, username: str):
        super().__init__(f'Username "{username}" is already registered by another account. Please try a different one.')


class InvalidCredentials(Exception):
    """Exception for entering invalid credentials."""
    def __init__(self, cred: Credentials):
        super().__init__(f'Invalid credentials: username={cred.username}, password={cred.password}')


class NonExistent(Exception):
    """Exception for non-existent entities."""
    def __init__(self, entity: Literal['account', 'token', 'employee', 'shift', 'schedule', 'holiday', 'setting'], identifier: str|int):
        self.entity = entity
        msg = ''
        if type(identifier) is int: msg = f'{entity.title()} with ID "{identifier}" does not exist.'
        else: msg = f'{entity.title()} with name "{identifier}" does not exist.'
        super().__init__(msg)


class CookiesUnavailable(Exception):
    """Exception for missing or null cookies."""
    def __init__(self, cookies: Cookies):
        super().__init__(f'Expected cookie(s) are not available in the request: {cookies}')


class InvalidCookies(Exception):
    """Exception for invalid cookies."""
    def __init__(self, cookies: Cookies):
        super().__init__(f'Invalid cookies: {cookies}')