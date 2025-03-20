from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
import jpype
from src.server.rate_limit import limiter, rate_limit_handler
from src.server.lib.constants import BACKEND_SERVER_URL, WEB_SERVER_URL, SCHEDULE_ENGINE_PATH
from src.server.routers.auth import auth_router
from src.server.routers.db import account_router, employee_router, shift_router, schedule_router, holiday_router, settings_router, sub_router
from src.server.routers.engine import engine_router
from src.server.routers.contact import contact_router

@asynccontextmanager
async def _lifespan(app: FastAPI):
    """Defines the application lifespan to manage JVM startup and shutdown."""
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
    employee_router,
    shift_router,
    schedule_router,
    settings_router,
    holiday_router,
    engine_router,
    contact_router,
    sub_router
): app.include_router(r)