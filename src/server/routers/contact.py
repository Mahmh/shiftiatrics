from fastapi import APIRouter, Request
from src.server.rate_limit import limiter
from src.server.lib.api import endpoint, get_cookies
from src.server.lib.models import ContactUsSubmissionData
from src.server.db import contact

contact_router = APIRouter(prefix='/contact')

@contact_router.post('/')
@limiter.limit('1/minute')
@endpoint(auth=False)
async def contact_us(data: ContactUsSubmissionData, request: Request) -> dict:
    await contact(data, get_cookies(request))
    return {'detail': 'Submission successful'}