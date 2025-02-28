from textwrap import dedent
from fastapi import APIRouter, Request
from fastapi_mail import FastMail, MessageSchema
from src.server.rate_limit import limiter
from src.server.lib.api import endpoint
from src.server.lib.models import ContactUsSubmissionData
from src.server.lib.emails import conf
from src.server.lib.constants import COMPANY_EMAIL

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


async def _send_email(data: ContactUsSubmissionData) -> None:
    # MAIL_USERNAME -> COMPANY_EMAIL -> data.email
    message = MessageSchema(
        subject='Shiftiatrics: New Contact Us Submission',
        recipients=[COMPANY_EMAIL],
        body=_get_email_body(data),
        subtype='html',
        reply_to=[data.email]
    )
    fm = FastMail(conf)
    await fm.send_message(message)


@contact_router.post('/contact')
@limiter.limit('1/minute')
@endpoint(auth=False)
async def contact_us(data: ContactUsSubmissionData, request: Request) -> dict:
    await _send_email(data)
    return {'detail': 'Submission successful'}