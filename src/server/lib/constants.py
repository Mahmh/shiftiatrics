from dotenv import load_dotenv; load_dotenv()
import os

# Net
WEB_SERVER_URL = os.getenv('WEB_SERVER_URL', 'http://localhost:3000')

# DB
PSQL_HOST = os.getenv('POSTGRES_HOST', 'localhost')
PSQL_PORT = os.getenv('POSTGRES_PORT', '5432')
PSQL_DB = os.getenv('POSTGRES_DB')
PSQL_USER = os.getenv('POSTGRES_USER')
PSQL_PASSWORD = os.getenv('POSTGRES_PASSWORD')
ENGINE_URL = f'postgresql+psycopg2://{PSQL_USER}:{PSQL_PASSWORD}@{PSQL_HOST}:{PSQL_PORT}/{PSQL_DB}'

# Security
MIN_USERNAME_LEN = int(os.getenv('MIN_USERNAME_LEN'))
MAX_USERNAME_LEN = int(os.getenv('MAX_USERNAME_LEN'))
MIN_PASSWORD_LEN = int(os.getenv('MIN_PASSWORD_LEN'))
MAX_PASSWORD_LEN = int(os.getenv('MAX_PASSWORD_LEN'))
TOKEN_EXPIRY_SECONDS = int(os.getenv('TOKEN_EXPIRY_SECONDS'))
DEFAULT_RATE_LIMIT = os.getenv('DEFAULT_RATE_LIMIT')

# Misc
LIST_OF_WEEKEND_DAYS = ['Saturday & Sunday', 'Friday & Saturday', 'Sunday & Monday']
ENABLE_LOGGING = (os.getenv('ENABLE_LOGGING', 'true').lower() == 'true')
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))  # path with respect to this file
locate = lambda x: os.path.join(CURRENT_DIR, x)