from fastapi import FastAPI
from contextlib import asynccontextmanager
import jpype

# Init
@asynccontextmanager
async def _lifespan(app: FastAPI):
    """Defines the application lifespan to manage JVM startup and shutdown."""
    if not jpype.isJVMStarted():
        jpype.startJVM(classpath='../utils/out/')
    try:
        yield 
    finally:
        if jpype.isJVMStarted():
            jpype.shutdownJVM()

app = FastAPI(lifespan=_lifespan)