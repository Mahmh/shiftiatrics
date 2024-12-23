from src.server.lib.models import Credentials

class UsernameTaken(Exception):
    """Exception for entering an existing username."""
    def __init__(self, username: str):
        super().__init__(f'Username "{username}" is already registered.')


class AccountDoesNotExist(Exception):
    """Exception for attempting to access a non-existent account."""
    def __init__(self, username: str):
        super().__init__(f'Account "{username}" does not exist.')


class InvalidCredentials(Exception):
    """Exception for entering invalid credentials."""
    def __init__(self, cred: Credentials):
        super().__init__(f'Invalid credentials: username={cred.username}, password={cred.password}')