
from fastapi_mail import ConnectionConfig
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