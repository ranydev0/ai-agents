import asyncio
from smolagents.agents import FinalAnswerStep
from telegram.ext import ApplicationBuilder
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler
from telegram.ext import filters
from configuration.constants import TB_TOKEN
from agent import agent

BATCH_SIZE = 20  # characters to accumulate before editing the message


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
    message = await update.message.reply_text(words[0])
    current_text = words[0]
    pending = ""

    for word in words[1:]:
        pending += f" {word}"
        if len(pending) >= BATCH_SIZE:
            current_text += pending
            pending = ""
            await message.edit_text(current_text)

    if pending:
        current_text += pending
        await message.edit_text(current_text)


async def start(update, context):
    await update.message.reply_sticker(sticker=open("assets/alfred.webp", "rb"))
    await stream_agent_reply(update, update.message.text)


async def handle_message(update, context):
    await stream_agent_reply(update, update.message.text)


def main():
    app = ApplicationBuilder().token(TB_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()


if __name__ == "__main__":
    main()
