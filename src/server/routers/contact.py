from textwrap import dedent
from fastapi import APIRouter, Request
from src.server.rate_limit import limiter
from src.server.lib.api import endpoint
from src.server.lib.models import ContactUsSubmissionData
from src.server.lib.constants import COMPANY_EMAIL
from src.server.lib.emails import send_email

contact_router = APIRouter()

def _get_email_body(data: ContactUsSubmissionData) -> str:
    return dedent(f'''
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <h2 style="color: #0056b3;">New Contact Us Submission</h2>
            <table style="border-collapse: collapse; width: 100%;">
                <tr><td><strong>Name:</strong></td><td>{data.name}</td></tr>
                <tr><td><strong>Email:</strong></td><td>{data.email}</td></tr>
                <tr><td><strong>Query Type:</strong></td><td>{data.query_type}</td></tr>
                <tr><td><strong>Message:</strong></td></tr>
                <tr><td colspan="2" style="border-top: 1px solid #ccc; padding-top: 10px;">{data.description}</td></tr>
            </table>
        </body>
        </html>
    ''')


@contact_router.post('/contact')
@limiter.limit('1/minute')
@endpoint(auth=False)
async def contact_us(data: ContactUsSubmissionData, request: Request) -> dict:
    await send_email(
        subject='New Contact Us Submission',
        recipients=[COMPANY_EMAIL],
        body=_get_email_body(data),
        reply_to=[data.email]
    )
    return {'detail': 'Submission successful'}