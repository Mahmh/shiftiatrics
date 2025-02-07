from dotenv import load_dotenv; load_dotenv()
import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))  # path with respect to this file
_locate = lambda x: os.path.join(CURRENT_DIR, x)

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
MIN_EMAIL_LEN = int(os.getenv('MIN_EMAIL_LEN'))
MAX_EMAIL_LEN = int(os.getenv('MAX_EMAIL_LEN'))
MIN_PASSWORD_LEN = int(os.getenv('MIN_PASSWORD_LEN'))
MAX_PASSWORD_LEN = int(os.getenv('MAX_PASSWORD_LEN'))
TOKEN_EXPIRY_SECONDS = int(os.getenv('TOKEN_EXPIRY_SECONDS'))
DEFAULT_RATE_LIMIT = os.getenv('DEFAULT_RATE_LIMIT')

# Email
SMTP_HOST = os.getenv('SMTP_HOST')
SMTP_PORT = os.getenv('SMTP_PORT')
SMTP_USER = os.getenv('SMTP_USER')
SMTP_PASS = os.getenv('SMTP_PASS')
MAIL_BROKER = os.getenv('MAIL_BROKER')
MAIL_RESULT_BACKEND = os.getenv('MAIL_RESULT_BACKEND')

# Misc
LIST_OF_WEEKEND_DAYS = ['Saturday & Sunday', 'Friday & Saturday', 'Sunday & Monday']
ENABLE_LOGGING = os.getenv('ENABLE_LOGGING', 'false').lower() == 'true'
LOG_DIR = _locate('../logs/')
SCHEDULE_ENGINE_DIR = _locate('../engine/engine.jar')