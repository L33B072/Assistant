import asyncio
from typing import Callable, Awaitable

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

from .config import settings
from .time_tracker import get_active_entry, start_timer, stop_timer
from .planner import brainstorm, focus_check

# type alias for your router to talk to FastAPI/other modules if needed
Handler = Callable[[str], Awaitable[str]]

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hi! I'm your field agent. Try:\n"
        "- /brainstorm <idea>\n"
        "- /focus\n"
        "- /starttimer <task description>\n"
        "- /stoptimer"
    )

async def brainstorm_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question = " ".join(context.args)
    if not question:
        await update.message.reply_text("Please provide a topic, e.g. /brainstorm new CNC product.")
        return

    # You could pull in Obsidian context here
    context_text = "Context from Obsidian, weekly plan, etc."
    answer = await brainstorm(context_text, question)
    await update.message.reply_text(answer)

async def focus_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Here you'd:
    # - Read priorities from Obsidian
    # - Summarize today's calendar via Graph
    # - Get current active timer/task
    priorities_text = "Weekly priorities from Obsidian."
    calendar_summary = "Calendar summary from Outlook."
    active = await get_active_entry()
    current_task_desc = active["notes"] if active else "No active task"
    billable_today_hours = 0.0  # TODO: compute from DB

    reply = await focus_check(
        priorities_text=priorities_text,
        calendar_summary=calendar_summary,
        current_task_desc=current_task_desc,
        billable_today_hours=billable_today_hours,
    )
    await update.message.reply_text(reply)

async def starttimer_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    desc = " ".join(context.args) or "Untitled task"
    # TODO: look up or create a task row in DB
    task_id = 1  # placeholder
    entry_id = await start_timer(task_id=task_id, billable=True, notes=desc)
    await update.message.reply_text(f"Started timer #{entry_id} for: {desc}")

async def stoptimer_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    active = await get_active_entry()
    if not active:
        await update.message.reply_text("No active timer.")
        return
    await stop_timer(active["id"])
    await update.message.reply_text(f"Stopped timer #{active['id']} (task {active['task_id']}).")

async def echo_fallback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""
    await update.message.reply_text(
        "You said:\n"
        f"{text}\n\nTry /focus or /brainstorm to get started."
    )

def build_telegram_app() -> Application:
    application = Application.builder().token(settings.telegram_bot_token).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("brainstorm", brainstorm_command))
    application.add_handler(CommandHandler("focus", focus_command))
    application.add_handler(CommandHandler("starttimer", starttimer_command))
    application.add_handler(CommandHandler("stoptimer", stoptimer_command))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo_fallback))

    return application
