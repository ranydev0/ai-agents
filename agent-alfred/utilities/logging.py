import logging
from telegram import Update
from zoneinfo import ZoneInfo

logging.basicConfig(
    format='%(message)s',
    level=logging.WARNING
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def telegram_message_logger(update: Update) -> None:
    user = update.effective_user
    message = update.effective_message

    user_first_name = getattr(user, "first_name", None) or ""
    user_last_name = getattr(user, "last_name", None) or ""
    user_id = getattr(user, "id", None) or ""

    raw_date = getattr(message, "date", None)
    message_date = raw_date.astimezone(ZoneInfo("Australia/Sydney")).strftime("%Y-%m-%d %H:%M:%S") if raw_date else ""
    message_id = getattr(message, "message_id", None) or ""
    message_text = getattr(message, "text", None) or ""

    logger.info(
        "\nMessage date: %s || Message id: %s || Message: %s || User: %s || User id: %s",
        message_date, message_id, message_text,
        f"{user_first_name} {user_last_name}".strip(), user_id
    )
