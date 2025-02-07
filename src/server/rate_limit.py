from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

async def rate_limit_handler(request, exc):
    """Handles rate limits from a specific client."""
    return JSONResponse(status_code=429, content={'message': 'Too many requests. Please try again later.'})