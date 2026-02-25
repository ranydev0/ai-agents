import asyncio
import logging
from smolagents.agents import FinalAnswerStep
from telegram.ext import ApplicationBuilder
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler
from telegram.ext import filters
from telegram.error import NetworkError
from configuration.constants import TB_TOKEN
from agent import agent

logger = logging.getLogger(__name__)

BATCH_SIZE = 20  # characters to accumulate before editing the message


async def with_retry(coro_fn, retries=3, delay=2):
    for attempt in range(retries):
        try:
            return await coro_fn()
        except NetworkError:
            if attempt == retries - 1:
                raise
            await asyncio.sleep(delay)


async def stream_agent_reply(update, task):
    loop = asyncio.get_event_loop()

    final_answer_future = loop.create_future()

    def run_agent():
        final_answer = None
        for event in agent.run(task, stream=True):
            if isinstance(event, FinalAnswerStep):
                final_answer = str(event.output)
        loop.call_soon_threadsafe(final_answer_future.set_result, final_answer)

    loop.run_in_executor(None, run_agent)

    final_answer = await final_answer_future
    if not final_answer:
        return

    words = final_answer.split()
    message = await with_retry(lambda: update.message.reply_text(words[0]))
    current_text = words[0]
    pending = ""

    for word in words[1:]:
        pending += f" {word}"
        if len(pending) >= BATCH_SIZE:
            current_text += pending
            pending = ""
            await with_retry(lambda: message.edit_text(current_text))

    if pending:
        current_text += pending
        await with_retry(lambda: message.edit_text(current_text))


async def error_handler(update, context):
    if isinstance(context.error, NetworkError):
        logger.warning("Network error: %s", context.error)
    else:
        logger.error("Unhandled exception", exc_info=context.error)


async def start(update, _context):
    await with_retry(
        lambda: update.message.reply_sticker(sticker=open("assets/alfred.webp", "rb"))
    )
    await stream_agent_reply(update, update.message.text)


async def handle_message(update, _context):
    await stream_agent_reply(update, update.message.text)


def main():
    app = ApplicationBuilder().token(TB_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(error_handler)
    app.run_polling(bootstrap_retries=-1)


if __name__ == "__main__":
    main()
