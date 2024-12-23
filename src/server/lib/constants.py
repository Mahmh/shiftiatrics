from dotenv import load_dotenv; load_dotenv()
import os

# DB
PSQL_HOST = os.getenv('POSTGRES_HOST', 'localhost')
PSQL_PORT = os.getenv('POSTGRES_PORT', '5432')
PSQL_DB = os.getenv('POSTGRES_DB')
PSQL_USER = os.getenv('POSTGRES_USER')
PSQL_PASSWORD = os.getenv('POSTGRES_PASSWORD')
ENGINE_URL = f'postgresql+psycopg2://{PSQL_USER}:{PSQL_PASSWORD}@{PSQL_HOST}:{PSQL_PORT}/{PSQL_DB}'

# Misc
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))  # path with respect to this file
ENABLE_LOGGING = (os.getenv('ENABLE_LOGGING', 'true').lower() == 'true')