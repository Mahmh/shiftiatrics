from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
import os, jpype, psycopg2
from src.server.rate_limit import limiter, rate_limit_handler
from src.server.lib.constants import BACKEND_SERVER_URL, WEB_SERVER_URL, SCHEDULE_ENGINE_PATH, DB_SCHEMA_PATH, PSQL_DB, PSQL_USER, PSQL_PASSWORD, PSQL_HOST, PSQL_PORT
from src.server.routers.auth import auth_router
from src.server.routers.db import account_router, team_router, employee_router, shift_router, schedule_router, holiday_router, settings_router, sub_router
from src.server.routers.engine import engine_router
from src.server.routers.contact import contact_router

def _create_db_if_not_exists():
     # Connect to default 'postgres' DB to check/create the target DB
    try:
        admin_conn = psycopg2.connect(
            dbname="postgres",  # This must exist
            user=PSQL_USER,
            password=PSQL_PASSWORD,
            host=PSQL_HOST,
            port=PSQL_PORT
        )
        admin_conn.autocommit = True
        admin_cur = admin_conn.cursor()

        admin_cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (PSQL_DB,))
        exists = admin_cur.fetchone()

        if not exists:
            print(f"📦 Creating database '{PSQL_DB}'...")
            admin_cur.execute(f"CREATE DATABASE {PSQL_DB}")
        else:
            print(f"✅ Database '{PSQL_DB}' already exists")

        admin_cur.close()
        admin_conn.close()
    except Exception as e:
        print(f"❌ Failed to connect to admin DB or create target DB: {e}")
        return


def _apply_schema():
    if not os.path.exists(DB_SCHEMA_PATH):
        print('❌ schema.sql not found!')
        return

    # Now connect to the actual target DB and apply schema.sql
    try:
        with open(DB_SCHEMA_PATH, 'r') as f:
            schema = f.read()

        conn = psycopg2.connect(
            dbname=PSQL_DB,
            user=PSQL_USER,
            password=PSQL_PASSWORD,
            host=PSQL_HOST,
            port=PSQL_PORT
        )
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute(schema)
        cur.close()
        conn.close()
        print("🎉 schema.sql applied successfully.")
    except Exception as e:
        print(f"❌ Failed to apply schema.sql: {e}")


@asynccontextmanager
async def _lifespan(app: FastAPI):
    """Defines the application lifespan to manage JVM startup and shutdown."""
    _create_db_if_not_exists()
    _apply_schema()

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, rate_limit_handler) 

    if not jpype.isJVMStarted():
        jpype.startJVM(classpath=SCHEDULE_ENGINE_PATH)
    try:
        yield
    finally:
        if jpype.isJVMStarted():
            jpype.shutdownJVM()


app = FastAPI(lifespan=_lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[BACKEND_SERVER_URL, WEB_SERVER_URL],
    allow_methods=['GET', 'POST', 'PATCH', 'DELETE'],
    allow_headers=['*'],
    allow_credentials=True
)


for r in (
    auth_router,
    account_router,
    team_router,
    employee_router,
    shift_router,
    schedule_router,
    holiday_router,
    settings_router,
    sub_router,
    engine_router,
    contact_router
): app.include_router(r)