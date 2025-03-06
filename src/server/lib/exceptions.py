from typing import Literal
from src.server.lib.models import Credentials, Cookies

class EmailTaken(Exception):
    """Exception for entering an existing email."""
    def __init__(self, email: str):
        super().__init__(f'Email "{email}" is already registered by another account. Please try a different one.')


class InvalidCredentials(Exception):
    """Exception for entering invalid credentials."""
    def __init__(self, cred: Credentials):
        super().__init__(f'Invalid credentials: email={cred.email}')


class NonExistent(Exception):
    """Exception for non-existent entities."""
    def __init__(self, entity: Literal['account', 'token', 'employee', 'shift', 'schedule', 'holiday', 'setting'], identifier: str|int):
        self.entity = entity
        msg = ''
        if type(identifier) is int: msg = f'{entity.title()} with ID "{identifier}" does not exist.'
        else: msg = f'{entity.title()} with email "{identifier}" does not exist.'
        super().__init__(msg)


class CookiesUnavailable(Exception):
    """Exception for missing or null cookies."""
    def __init__(self, cookies: Cookies):
        super().__init__(f'Expected cookie(s) are not available in the request: {cookies}')


class InvalidCookies(Exception):
    """Exception for invalid cookies."""
    def __init__(self, cookies: Cookies):
        super().__init__(f'Invalid cookies: {cookies}')


class EndpointAuthError(Exception):
    """Exception for unsuccessful authentication using a request to a back-end server's endpoint."""
    def __init__(self):
        super().__init__(f'Authentication required')