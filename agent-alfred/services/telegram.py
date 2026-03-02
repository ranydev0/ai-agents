from pathlib import Path
from telegram import Update
from telegram.ext import ApplicationBuilder
from telegram.ext import ContextTypes
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler
from telegram.ext import filters
from configuration.constants import TB_TOKEN
from utilities.logging import telegram_message_logger


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    BASE_DIR = Path(__file__).parent
    alfred_sticker_path = BASE_DIR / "assets" / "alfred.webp"

    telegram_message_logger(update)

    await context.bot.send_sticker(chat_id=update.effective_chat.id, sticker=alfred_sticker_path)


async def text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_message_logger(update)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)


def telegram_application() -> None:
    application = ApplicationBuilder().token(TB_TOKEN).build()
    
    start_handler = CommandHandler('start', start)
    text_message_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), text_message)


    application.add_handler(start_handler)
    application.add_handler(text_message_handler)
    
    application.run_polling(bootstrap_retries=-1)