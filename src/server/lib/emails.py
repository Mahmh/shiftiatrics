from fastapi_mail import FastMail, ConnectionConfig, MessageSchema
from src.server.lib.utils import errlog
from src.server.lib.constants import (
    MAIL_USERNAME,
    MAIL_PASSWORD,
    MAIL_USERNAME,
    MAIL_PASSWORD,
    MAIL_FROM,
    MAIL_PORT,
    MAIL_SERVER,
    MAIL_TLS,
    MAIL_SSL,
)

# conf = ConnectionConfig(
#     MAIL_USERNAME=MAIL_USERNAME,
#     MAIL_PASSWORD=MAIL_PASSWORD,
#     MAIL_FROM=MAIL_FROM,
#     MAIL_PORT=MAIL_PORT,
#     MAIL_SERVER=MAIL_SERVER,
#     MAIL_TLS=MAIL_TLS,
#     MAIL_SSL=MAIL_SSL,
#     USE_CREDENTIALS=True
# )
conf = None


async def send_email(subject: str, body: str, receipents: list[str], reply_to: list[str] = []) -> None:
    """Makes the server send an email to receipent(s)."""
    try:
        message = MessageSchema(
            subject=f'Shiftiatrics: {subject}',
            recipients=receipents,
            body=body,
            subtype='html',
            reply_to=reply_to
        )
        fm = FastMail(conf)
        await fm.send_message(message)
    except Exception as e:
        errlog('send_email', e, 'emails')