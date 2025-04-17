from fastapi_mail import FastMail, ConnectionConfig, MessageSchema
from src.server.lib.utils import errlog
from src.server.lib.constants import MAIL_USERNAME, MAIL_PASSWORD, MAIL_FROM, MAIL_PORT, MAIL_SERVER, MAIL_TLS, MAIL_SSL, NOREPLY_EMAIL

conf = ConnectionConfig(
    MAIL_USERNAME=MAIL_USERNAME,
    MAIL_PASSWORD=MAIL_PASSWORD,
    MAIL_FROM=MAIL_FROM,
    MAIL_PORT=MAIL_PORT,
    MAIL_SERVER=MAIL_SERVER,
    MAIL_STARTTLS=MAIL_TLS,
    MAIL_SSL_TLS=MAIL_SSL,
    USE_CREDENTIALS=True
)
fm = FastMail(conf)


async def send_email(subject: str, body: str, recipients: list[str], reply_to: list[str] = [], noreply: bool = False) -> None:
    """Makes the server send an email to receipent(s)."""
    try:
        message = MessageSchema(
            subject=f'Shiftiatrics: {subject}',
            recipients=recipients,
            body=body,
            subtype='html',
            reply_to=reply_to,
            headers=({'From': NOREPLY_EMAIL} if noreply else None)
        )
        await fm.send_message(message)
    except Exception as e:
        errlog('send_email', e, 'emails')