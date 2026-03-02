import asyncio
import logging
from pathlib import Path
from telegram import Update
from telegram.error import NetworkError
from telegram.ext import ApplicationBuilder
from telegram.ext import ContextTypes
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler
from telegram.ext import filters
from configuration.constants import TB_TOKEN
from utilities.logging import telegram_message_logger
from services.agent import agent

logger = logging.getLogger(__name__)


async def send_with_retry(coro_fn, retries=3, delay=2):
    for attempt in range(retries):
        try:
            return await coro_fn()
        except NetworkError as e:
            if attempt < retries - 1:
                logger.warning("Network error on attempt %d, retrying: %s", attempt + 1, e)
                await asyncio.sleep(delay)
            else:
                raise


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    BASE_DIR = Path(__file__).parent.parent
    alfred_sticker_path = BASE_DIR / "assets" / "alfred.webp"

    chat_id = update.effective_chat.id
    welcome_message = "Generate a short, friendly welcome message introducing yourself as Alfred."

    telegram_message_logger(update)

    with open(alfred_sticker_path, "rb") as sticker_file:
        await send_with_retry(lambda: context.bot.send_sticker(chat_id=chat_id, sticker=sticker_file))

    await send_with_retry(lambda: context.bot.send_message(chat_id=chat_id, text=agent.run(welcome_message)))


async def text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_message = update.effective_message.text
    loading_sticker = "CAACAgIAAxkBAAIBFmmk8vIL3M3TJ2oREadRc925e6BFAAK0IwACmEspSN65vs0qW-TZOgQ"

    telegram_message_logger(update)

    sticker_message = await send_with_retry(lambda: context.bot.send_sticker(chat_id=chat_id, sticker=loading_sticker))
    response = await asyncio.get_event_loop().run_in_executor(None, lambda: agent.run(user_message))
    await context.bot.delete_message(chat_id=chat_id, message_id=sticker_message.message_id)
    await send_with_retry(lambda: context.bot.send_message(chat_id=chat_id, text=response))


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    if isinstance(context.error, NetworkError):
        logger.warning("Network error, will retry: %s", context.error)
        await asyncio.sleep(1)
    else:
        logger.error("Exception while handling an update:", exc_info=context.error)


def telegram_application() -> None:
    application = ApplicationBuilder().token(TB_TOKEN).build()

    start_commande_handler = CommandHandler('start', start)
    text_message_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), text_message)

    application.add_handler(start_commande_handler)
    application.add_handler(text_message_handler)
    application.add_error_handler(error_handler)
    
    application.run_polling(bootstrap_retries=-1)
