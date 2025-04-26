from typing import LiteralString
from textwrap import dedent
from fastapi_mail import FastMail, ConnectionConfig, MessageSchema
from src.server.lib.utils import errlog, format_template
from src.server.lib.models import ContactUsSubmissionData, Cookies
from src.server.lib.constants import MAIL_USERNAME, MAIL_PASSWORD, MAIL_PORT, MAIL_SERVER, MAIL_TLS, MAIL_SSL, SUPPORT_EMAIL, SYSTEM_EMAIL
from src.server.db.utils import dbsession, _check_account, _validate_cookies

async def send_email(subject: str, body: str, sender: LiteralString, recipients: list[str], reply_to: list[str] = []) -> None:
    """Makes the server send an email to receipent(s)."""
    try:
        conf = ConnectionConfig(
            MAIL_USERNAME=MAIL_USERNAME,
            MAIL_PASSWORD=MAIL_PASSWORD,
            MAIL_FROM=sender,
            MAIL_PORT=MAIL_PORT,
            MAIL_SERVER=MAIL_SERVER,
            MAIL_STARTTLS=MAIL_TLS,
            MAIL_SSL_TLS=MAIL_SSL,
            USE_CREDENTIALS=True
        )
        fm = FastMail(conf)
        message = MessageSchema(
            subject=f'Shiftiatrics: {subject}',
            recipients=recipients,
            body=body,
            subtype='html',
            reply_to=reply_to
        )
        await fm.send_message(message)
    except Exception as e:
        errlog('send_email', e, 'emails')


@dbsession()
async def contact(data: ContactUsSubmissionData, cookies: Cookies, *, session) -> None:
    """Sends an email message that includes the user's email, query type, and query description to the company."""
    if data.email is None:
        cookies = _validate_cookies(cookies, session=session)
        account = _check_account(cookies.account_id, session=session)
        data.account_id = account.account_id
        data.email = account.email

    await send_email(
        subject='New Contact Us Submission',
        body=format_template(
            'contact_us_submission.html',
            account_id=data.account_id or 'N/A',
            name=data.name or 'N/A',
            email=data.email or 'N/A',
            query_type=data.query_type,
            description=data.description
        ),
        sender=SYSTEM_EMAIL,
        recipients=[SUPPORT_EMAIL],
        reply_to=[data.email]
    )