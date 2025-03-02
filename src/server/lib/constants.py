from dotenv import load_dotenv; load_dotenv()
import os, bcrypt

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))  # path with respect to this file
_locate = lambda x: os.path.join(CURRENT_DIR, x)

# Net
BACKEND_SERVER_URL = os.getenv('BACKEND_SERVER_URL', 'http://localhost:8000')
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
FAKE_HASH = bcrypt.hashpw(b'fake_password', bcrypt.gensalt()).decode('utf-8')
TOKEN_EXPIRY_SECONDS = int(os.getenv('TOKEN_EXPIRY_SECONDS'))
DEFAULT_RATE_LIMIT = os.getenv('DEFAULT_RATE_LIMIT')
COOKIE_DOMAIN = None

# Email
MAIL_USERNAME = os.getenv('MAIL_USERNAME')
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
MAIL_FROM = os.getenv('MAIL_FROM')
MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
MAIL_SERVER = os.getenv('MAIL_SERVER')
MAIL_TLS = bool(int(os.getenv('MAIL_TLS', '1')))
MAIL_SSL = bool(int(os.getenv('MAIL_SSL', '0'))) 
COMPANY_EMAIL = os.getenv('COMPANY_EMAIL')

# OAuth
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
GOOGLE_AUTH_URL = 'https://accounts.google.com/o/oauth2/auth'
GOOGLE_REDIRECT_URI = f'{BACKEND_SERVER_URL}/auth/google/callback'
GOOGLE_USERINFO_URL = 'https://www.googleapis.com/oauth2/v2/userinfo'
GOOGLE_TOKEN_URL = 'https://oauth2.googleapis.com/token'

# Misc
ENABLE_LOGGING = bool(int(os.getenv('ENABLE_LOGGING', '0')))
LOG_DIR = _locate('../logs/')
SCHEDULE_ENGINE_DIR = _locate('../engine/engine.jar')