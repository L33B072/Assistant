import asyncio
from typing import Callable, Awaitable
from datetime import datetime, timedelta

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

from .config import settings
from .time_tracker import get_active_entry, start_timer, stop_timer, get_all_active_entries
from .planner import brainstorm, focus_check
from .msgraph_client import (
    get_today_calendar_summary, 
    create_calendar_event_helper, 
    delete_calendar_event_helper,
    delete_multiple_events_helper
)
from .conversation_log import (
    init_conversation_db,
    log_conversation,
    get_recent_conversations,
    search_conversations,
    export_conversations_to_markdown
)
from .obsidian_tasks import (
    get_priorities_from_obsidian, 
    read_obsidian_note,
    add_task_to_note,
    complete_task_in_note,
    remove_task_from_note,
    create_obsidian_page,
    append_to_obsidian_page
)
from .ai_assistant import debby_respond

# type alias for your router to talk to FastAPI/other modules if needed
Handler = Callable[[str], Awaitable[str]]

# Conversation memory cache - loaded from DB on startup, saved back to DB
# Format: {user_id: [(user_msg, debby_response), ...]}
conversation_memory = {}
MAX_MEMORY_TURNS = 5  # Remember last 5 exchanges in cache

async def load_conversation_memory(user_id: int):
    """Load recent conversation history from database into memory cache."""
    if user_id not in conversation_memory:
        conversation_memory[user_id] = await get_recent_conversations(user_id, MAX_MEMORY_TURNS)

async def format_active_timers() -> str:
    """Format all active timers for display"""
    active_timers = await get_all_active_entries()
    if not active_timers:
        return "⏱️ No active timers"
    
    result = "⏱️ **Active Timers:**\n"
    for timer in active_timers:
        start_time = datetime.fromisoformat(timer['start_time'])
        now = datetime.utcnow()
        duration = now - start_time
        hours = int(duration.total_seconds() // 3600)
        minutes = int((duration.total_seconds() % 3600) // 60)
        
        billable_icon = "💰" if timer['billable'] else "🆓"
        result += f"{billable_icon} **#{timer['id']}** - {timer['notes']} ({hours:02d}:{minutes:02d})\n"
    
    return result

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hi! I'm Debby, your AI assistant. Try:\n"
        "- /brainstorm <idea>\n"
        "- /focus\n"
        "- /priorities\n"
        "- /addtask <task description>\n"
        "- /completetask <number>\n"
        "- /calendar\n"
        "- /starttimer <task description>\n"
        "- /stoptimer\n"
        "- /timers - Show all active timers\n"
        "- /history [search term] - View conversation history\n"
        "- /export [days] - Export conversations to markdown\n\n"
        "Or just talk to me naturally!"
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
    
    # Show confirmation and current active timers
    confirmation = f"✅ Started timer #{entry_id} for: {desc}\n\n"
    timer_status = await format_active_timers()
    
    await update.message.reply_text(confirmation + timer_status)

async def stoptimer_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    active = await get_active_entry()
    if not active:
        await update.message.reply_text("No active timer.")
        return
    await stop_timer(active["id"])
    
    # Show confirmation and remaining active timers
    confirmation = f"⏹️ Stopped timer #{active['id']} (task {active['task_id']}).\n\n"
    timer_status = await format_active_timers()
    
    await update.message.reply_text(confirmation + timer_status)

async def timers_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show all active timers"""
    timer_status = await format_active_timers()
    await update.message.reply_text(timer_status)

async def history_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show recent conversation history."""
    user_id = update.effective_user.id
    
    # Check if they want to search
    if context.args:
        search_term = " ".join(context.args)
        results = await search_conversations(user_id, search_term, limit=5)
        
        if not results:
            await update.message.reply_text(f"🔍 No conversations found matching '{search_term}'")
            return
        
        msg = f"🔍 **Search Results for '{search_term}'**\n\n"
        for result in results:
            timestamp = result['timestamp']
            user_msg = result['user'][:50] + "..." if len(result['user']) > 50 else result['user']
            msg += f"**{timestamp}** ({result['action']})\n{user_msg}\n\n"
        
        await update.message.reply_text(msg)
    else:
        # Show recent history
        history = await get_recent_conversations(user_id, limit=10)
        
        if not history:
            await update.message.reply_text("📖 No conversation history yet.")
            return
        
        msg = "📖 **Recent Conversations:**\n\n"
        for user_msg, debby_resp in history:
            user_short = user_msg[:40] + "..." if len(user_msg) > 40 else user_msg
            debby_short = debby_resp[:40] + "..." if len(debby_resp) > 40 else debby_resp
            msg += f"**You:** {user_short}\n**Debby:** {debby_short}\n\n"
        
        await update.message.reply_text(msg)

async def export_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Export conversation history to markdown."""
    user_id = update.effective_user.id
    
    # Get number of days from args, default to 7
    days = 7
    if context.args:
        try:
            days = int(context.args[0])
        except ValueError:
            await update.message.reply_text("⚠️ Please provide a valid number of days. Example: /export 30")
            return
    
    await update.message.reply_text(f"📝 Exporting last {days} days of conversations...")
    
    markdown = await export_conversations_to_markdown(user_id, days)
    
    # Save to a file and send it
    from pathlib import Path
    export_file = Path(__file__).parent.parent / "data" / f"conversation_export_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    export_file.write_text(markdown, encoding='utf-8')
    
    with open(export_file, 'rb') as f:
        await update.message.reply_document(
            document=f,
            filename=f"conversation_log_{days}days.md",
            caption=f"📊 Conversation log for the last {days} days"
        )

async def echo_fallback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """AI-first assistant where Debby decides what to do, then we execute it."""
    text = update.message.text or ""
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name or "User"
    
    # Load conversation history from database
    await load_conversation_memory(user_id)
    
    await update.message.reply_text("🤖 Debby is thinking...")
    
    # Get conversation history for this user
    if user_id not in conversation_memory:
        conversation_memory[user_id] = []
    
    history = conversation_memory[user_id]
    history_text = ""
    if history:
        history_text = "\n\nRecent conversation:\n"
        for user_msg, debby_msg in history[-3:]:  # Last 3 exchanges
            history_text += f"User: {user_msg}\nDebby: {debby_msg}\n"
    
    # First, let Debby analyze what the user wants
    analysis_prompt = f"""You are Debby, an AI assistant for Lee. Analyze this message and decide what action to take.
{history_text}
Current user message: "{text}"
Current date and time: {datetime.now().strftime("%A, %B %d, %Y at %I:%M %p")}

Available actions:
1. VIEW_CALENDAR - Show today's calendar
2. CREATE_EVENT - Create a calendar event (need: subject, time, date, attendees)
3. DELETE_EVENT - Delete a calendar event (need: time OR subject keywords)
4. DELETE_MULTIPLE - Delete multiple calendar events (need: subject keywords and confirmation)
5. START_TIMER - Start a time tracking timer (need: task description)
6. STOP_TIMER - Stop the active timer
7. VIEW_TIMERS - Show all active timers
8. VIEW_PRIORITIES - Show weekly priorities from Obsidian
9. CREATE_PAGE - Create an Obsidian page (need: page name)
10. ADD_TO_PAGE - Add content to Obsidian page (need: page name, content)
11. COMPLETE_TASK - Mark a task complete (need: task number)
12. CHAT - Just have a conversation, answer a question

IMPORTANT: Use the conversation history to understand context. For example:
- If I just told the user about multiple matching events, and they say "both" or "all", use DELETE_MULTIPLE
- If they're responding to a previous question, consider that context

Respond with ONLY:
- ACTION: [action name]
- PARAMS: [any parameters needed as JSON]
- RESPONSE: [what to tell the user if it's just CHAT]

For CREATE_EVENT:
- date should be in format "YYYY-MM-DD" (e.g., "2026-01-25") or "today" or "tomorrow"
- time should be in 24-hour format "HH:MM" (e.g., "17:15" for 5:15 PM)

Example:
ACTION: CREATE_EVENT
PARAMS: {{"subject": "Dinner with Geoff and Travis", "time": "17:15", "date": "2026-01-25", "attendees": []}}
"""

    try:
        # Get AI decision
        ai_decision = await brainstorm("Analyze user intent", analysis_prompt)
        
        # Parse the decision
        import re
        action_match = re.search(r'ACTION:\s*(\w+)', ai_decision, re.IGNORECASE)
        params_match = re.search(r'PARAMS:\s*(\{.*?\})', ai_decision, re.IGNORECASE | re.DOTALL)
        response_match = re.search(r'RESPONSE:\s*(.+)', ai_decision, re.IGNORECASE | re.DOTALL)
        
        if not action_match:
            # AI didn't follow format, just chat
            await update.message.reply_text(ai_decision)
            return
        
        action = action_match.group(1).upper()
        
        # Execute the action
        if action == "VIEW_CALENDAR":
            result = await get_today_calendar_summary()
            await update.message.reply_text(f"📅 {result}")
            
        elif action == "CREATE_EVENT":
            if params_match:
                import json
                from dateutil import parser as date_parser
                
                params = json.loads(params_match.group(1))
                
                subject = params.get('subject', 'New Event')
                time_str = params.get('time', '')
                date_str = params.get('date', 'today')
                
                # Calculate event date
                now = datetime.now()
                if date_str.lower() == 'today':
                    event_date = now
                elif date_str.lower() == 'tomorrow':
                    event_date = now + timedelta(days=1)
                else:
                    # Try to parse the date string (e.g., "2026-01-25" or "January 25, 2026")
                    try:
                        event_date = date_parser.parse(date_str)
                    except:
                        await update.message.reply_text(f"⚠️ I couldn't understand the date '{date_str}'. Creating for today instead.")
                        event_date = now
                
                if ':' in time_str:
                    hour, minute = map(int, time_str.split(':'))
                    start_time = event_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
                    end_time = start_time + timedelta(hours=1)
                    
                    result = await create_calendar_event_helper(subject, start_time, end_time)
                    await update.message.reply_text(result)
                else:
                    await update.message.reply_text("⚠️ I need a specific time to create the event")
            else:
                await update.message.reply_text("⚠️ I need more details to create the event")
                
        elif action == "DELETE_EVENT":
            if params_match:
                import json
                params = json.loads(params_match.group(1))
                time_str = params.get('time')
                subject = params.get('subject')
                
                result = await delete_calendar_event_helper(time_str, subject)
                await update.message.reply_text(result)
                
                # Store in memory cache and database
                conversation_memory[user_id].append((text, result))
                if len(conversation_memory[user_id]) > MAX_MEMORY_TURNS:
                    conversation_memory[user_id].pop(0)
                await log_conversation(user_id, user_name, text, result, "DELETE_EVENT")
            else:
                await update.message.reply_text("⚠️ I need to know which event to delete (time or subject)")
        
        elif action == "DELETE_MULTIPLE":
            if params_match:
                import json
                params = json.loads(params_match.group(1))
                subject = params.get('subject', '')
                
                # Extract subject from recent conversation if "both" or "all"
                if not subject and history:
                    # Look for subject in last Debby response
                    last_response = history[-1][1] if history else ""
                    if "matching events" in last_response.lower():
                        # Try to extract subject from the message
                        import re
                        match = re.search(r'matching events.*?:\n.*?([^:]+) at', last_response)
                        if match:
                            subject = match.group(1).strip()
                
                result = await delete_multiple_events_helper(subject)
                await update.message.reply_text(result)
                
                # Store in memory cache and database
                conversation_memory[user_id].append((text, result))
                if len(conversation_memory[user_id]) > MAX_MEMORY_TURNS:
                    conversation_memory[user_id].pop(0)
                await log_conversation(user_id, user_name, text, result, "DELETE_MULTIPLE")
            else:
                await update.message.reply_text("⚠️ I need to know which events to delete")
                
        elif action == "START_TIMER":
            if params_match:
                import json
                params = json.loads(params_match.group(1))
                task_desc = params.get('task', 'Untitled task')
                
                entry_id = await start_timer(task_id=1, billable=True, notes=task_desc)
                active_timers = await get_all_active_entries()
                await update.message.reply_text(
                    f"✅ Started timer #{entry_id} for: {task_desc}\n"
                    f"⏱️ You now have {len(active_timers)} active timer(s)"
                )
            else:
                await update.message.reply_text("⚠️ What should I track time for?")
                
        elif action == "STOP_TIMER":
            active = await get_active_entry()
            if active:
                await stop_timer(active["id"])
                await update.message.reply_text(f"⏹️ Stopped timer for: {active['notes']}")
            else:
                await update.message.reply_text("❌ No active timer to stop")
                
        elif action == "VIEW_TIMERS":
            timer_status = await format_active_timers()
            await update.message.reply_text(timer_status)
            
        elif action == "VIEW_PRIORITIES":
            priorities = await get_priorities_from_obsidian()
            await update.message.reply_text(f"📋 {priorities}")
            
        elif action == "CREATE_PAGE":
            if params_match:
                import json
                params = json.loads(params_match.group(1))
                page_name = params.get('page_name', 'Untitled')
                
                success = await create_obsidian_page(page_name)
                if success:
                    await update.message.reply_text(f"✅ Created Obsidian page: **{page_name}.md**")
                else:
                    await update.message.reply_text(f"❌ Failed to create page")
            else:
                await update.message.reply_text("⚠️ What should I name the page?")
                
        elif action == "ADD_TO_PAGE":
            if params_match:
                import json
                params = json.loads(params_match.group(1))
                page_name = params.get('page_name')
                content = params.get('content')
                
                if page_name and content:
                    success = await append_to_obsidian_page(page_name, content)
                    if success:
                        await update.message.reply_text(f"✅ Added to **{page_name}.md**")
                    else:
                        await update.message.reply_text(f"❌ Failed to update page")
                else:
                    await update.message.reply_text("⚠️ I need both page name and content")
            else:
                await update.message.reply_text("⚠️ I need page name and content")
                
        elif action == "COMPLETE_TASK":
            if params_match:
                import json
                params = json.loads(params_match.group(1))
                task_num = params.get('task_number')
                
                success = await complete_task_in_note(task_num)
                if success:
                    await update.message.reply_text(f"✅ Task #{task_num} completed!")
                else:
                    await update.message.reply_text(f"❌ Couldn't find task #{task_num}")
            else:
                await update.message.reply_text("⚠️ Which task number should I complete?")
                
        elif action == "CHAT":
            if response_match:
                response = response_match.group(1).strip()
                await update.message.reply_text(response)
                
                # Store in memory cache and database
                conversation_memory[user_id].append((text, response))
                if len(conversation_memory[user_id]) > MAX_MEMORY_TURNS:
                    conversation_memory[user_id].pop(0)
                await log_conversation(user_id, user_name, text, response, "CHAT")
            else:
                await update.message.reply_text(ai_decision)
                conversation_memory[user_id].append((text, ai_decision))
                if len(conversation_memory[user_id]) > MAX_MEMORY_TURNS:
                    conversation_memory[user_id].pop(0)
                await log_conversation(user_id, user_name, text, ai_decision, "CHAT")
                
        else:
            # Unknown action, just respond with AI's analysis
            await update.message.reply_text(ai_decision)
            conversation_memory[user_id].append((text, ai_decision))
            if len(conversation_memory[user_id]) > MAX_MEMORY_TURNS:
                conversation_memory[user_id].pop(0)
            await log_conversation(user_id, user_name, text, ai_decision, action)
            
    except Exception as e:
        # If anything fails, have a natural conversation
        try:
            answer = await brainstorm("Help the user", text)
            await update.message.reply_text(f"💬 {answer}")
        except:
            await update.message.reply_text(
                f"I heard: {text}\n\n"
                "Try: /focus, /priorities, /calendar, /timers"
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
    application.add_handler(CommandHandler("timers", timers_command))
    application.add_handler(CommandHandler("history", history_command))
    application.add_handler(CommandHandler("export", export_command))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo_fallback))

    return application
