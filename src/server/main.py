from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import jpype
from src.server.lib.constants import WEB_SERVER_URL, locate
from src.server.routers.db import account_router, employee_router, shift_router, schedule_router
from src.server.routers.engine import engine_router

@asynccontextmanager
async def _lifespan(app: FastAPI):
    """Defines the application lifespan to manage JVM startup and shutdown."""
    if not jpype.isJVMStarted():
        jpype.startJVM(classpath=locate('../engine/engine.jar'))
    try:
        yield 
    finally:
        if jpype.isJVMStarted():
            jpype.shutdownJVM()

app = FastAPI(lifespan=_lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[WEB_SERVER_URL],
    allow_credentials=True,
    allow_methods=['GET', 'POST', 'PATCH', 'DELETE'],
    allow_headers=['*'],
)

for r in (account_router, employee_router, shift_router, schedule_router, engine_router):
    app.include_router(r)