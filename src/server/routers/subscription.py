from fastapi import APIRouter, Body, Request
from src.server.rate_limit import limiter
from src.server.lib.api import endpoint, return_account_and_sub
from src.server.lib.constants import DEFAULT_RATE_LIMIT
from src.server.lib.types import PricingPlanName
from src.server.db import get_num_schedule_requests, create_checkout_session, get_invoice, create_sub, cancel_sub, change_sub

sub_router = APIRouter()

@sub_router.get('/sub/{account_id}/schedule_requests')
@limiter.limit(DEFAULT_RATE_LIMIT)
@endpoint()
async def get_schedule_requests_(account_id: int, request: Request) -> dict:
    return {'num_requests': get_num_schedule_requests(account_id)}


@sub_router.post('/sub/{account_id}/create_checkout_session')
@limiter.limit('10/minute')
@endpoint()
async def create_checkout_session_(account_id: int, request: Request, plan_name: PricingPlanName = Body(..., embed=True)) -> dict:
    return {'checkout_url': create_checkout_session(account_id, plan_name)}


@sub_router.post('/sub/{account_id}/create')
@limiter.limit('10/minute')
@endpoint()
async def create_subscription(account_id: int, request: Request, session_id: str = Body(..., embed=True)) -> dict:
    account, sub = create_sub(account_id, session_id)
    return return_account_and_sub(account, sub)


@sub_router.delete('/sub/{account_id}/cancel')
@limiter.limit(DEFAULT_RATE_LIMIT)
@endpoint()
async def cancel_subscription(account_id: int, request: Request) -> dict:
    cancel_sub(account_id)
    return {'detail': 'Subscription canceled and prorated refund issued.'}


@sub_router.get('/sub/{account_id}/invoice')
@limiter.limit(DEFAULT_RATE_LIMIT)
@endpoint()
async def view_invoice(account_id: int, request: Request) -> dict:
    return get_invoice(account_id)


@sub_router.patch('/sub/{account_id}/change')
@limiter.limit(DEFAULT_RATE_LIMIT)
@endpoint()
async def change_subscription(account_id: int, request: Request, new_plan: PricingPlanName = Body(..., embed=True)) -> dict:
    return change_sub(account_id, new_plan)