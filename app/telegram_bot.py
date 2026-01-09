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
from .msgraph_client import get_today_calendar_summary
from .obsidian_tasks import (
    get_priorities_from_obsidian, 
    read_obsidian_note,
    add_task_to_note,
    complete_task_in_note,
    remove_task_from_note
)

# type alias for your router to talk to FastAPI/other modules if needed
Handler = Callable[[str], Awaitable[str]]

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hi! I'm your field agent. Try:\n"
        "- /brainstorm <idea>\n"
        "- /focus\n"
        "- /priorities\n"
        "- /addtask <task description>\n"
        "- /completetask <number>\n"
        "- /calendar\n"
        "- /starttimer <task description>\n"
        "- /stoptimer"
    )

async def brainstorm_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question = " ".join(context.args)
    if not question:
        await update.message.reply_text("Please provide a topic, e.g. /brainstorm new CNC product.")
        return

    # Pull in context from Obsidian and calendar
    try:
        priorities = await get_priorities_from_obsidian()
        calendar = await get_today_calendar_summary()
        context_text = f"{priorities}\n\n{calendar}"
    except Exception as e:
        context_text = f"Context unavailable: {e}"
    
    answer = await brainstorm(context_text, question)
    await update.message.reply_text(answer)

async def focus_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Read priorities from Obsidian
    # Summarize today's calendar via Graph
    # Get current active timer/task
    
    try:
        priorities_text = await get_priorities_from_obsidian()
    except Exception as e:
        priorities_text = f"Could not load priorities: {e}"
    
    try:
        calendar_summary = await get_today_calendar_summary()
    except Exception as e:
        calendar_summary = f"Could not fetch calendar: {e}"
    
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

async def priorities_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show weekly priorities from Obsidian."""
    try:
        priorities = await get_priorities_from_obsidian()
        await update.message.reply_text(priorities)
    except Exception as e:
        await update.message.reply_text(f"Error fetching priorities: {str(e)}")

async def addtask_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add a new task to WeeklyPlan.md."""
    task_description = " ".join(context.args)
    if not task_description:
        await update.message.reply_text("Please provide a task description.\nExample: /addtask Review Q1 budget #work")
        return
    
    try:
        success = await add_task_to_note(task_description)
        if success:
            await update.message.reply_text(f"✅ Task added: {task_description}")
        else:
            await update.message.reply_text("❌ Failed to add task")
    except Exception as e:
        await update.message.reply_text(f"Error adding task: {str(e)}")

async def completetask_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mark a task as complete by number."""
    if not context.args:
        await update.message.reply_text("Please provide a task number.\nExample: /completetask 3")
        return
    
    try:
        task_number = int(context.args[0])
        success = await complete_task_in_note(task_number)
        if success:
            await update.message.reply_text(f"✅ Task #{task_number} marked as complete!")
        else:
            await update.message.reply_text(f"❌ Could not find task #{task_number}")
    except ValueError:
        await update.message.reply_text("Please provide a valid task number.\nExample: /completetask 3")
    except Exception as e:
        await update.message.reply_text(f"Error completing task: {str(e)}")

async def calendar_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show today's calendar events."""
    try:
        calendar_summary = await get_today_calendar_summary()
        await update.message.reply_text(calendar_summary)
    except Exception as e:
        await update.message.reply_text(f"Error fetching calendar: {str(e)}")

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
    application.add_handler(CommandHandler("priorities", priorities_command))
    application.add_handler(CommandHandler("addtask", addtask_command))
    application.add_handler(CommandHandler("completetask", completetask_command))
    application.add_handler(CommandHandler("calendar", calendar_command))
    application.add_handler(CommandHandler("starttimer", starttimer_command))
    application.add_handler(CommandHandler("stoptimer", stoptimer_command))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo_fallback))

    return application
