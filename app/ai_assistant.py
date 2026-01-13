"""
Debby - AI-First Assistant with Function Calling
"""
import json
from typing import Dict, Any, List
from anthropic import AsyncAnthropic
from datetime import datetime

from .config import settings
from .time_tracker import get_active_entry, start_timer, stop_timer, get_all_active_entries
from .obsidian_tasks import (
    get_priorities_from_obsidian, 
    read_obsidian_note,
    add_task_to_note,
    complete_task_in_note,
    create_obsidian_page,
    append_to_obsidian_page
)
from .msgraph_client import get_today_calendar_summary, create_calendar_event_helper

# Initialize Claude client
client = AsyncAnthropic(api_key=settings.anthropic_api_key) if settings.anthropic_api_key else None

# Function definitions for Claude
AVAILABLE_FUNCTIONS = [
    {
        "name": "start_timer",
        "description": "Start a time tracking timer for a task",
        "input_schema": {
            "type": "object",
            "properties": {
                "task_description": {
                    "type": "string",
                    "description": "Description of the task to track time for"
                },
                "billable": {
                    "type": "boolean", 
                    "description": "Whether this is billable time"
                }
            },
            "required": ["task_description"]
        }
    },
    {
        "name": "stop_timer", 
        "description": "Stop the currently active timer",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "get_active_timers",
        "description": "Get all currently running timers with durations",
        "input_schema": {
            "type": "object", 
            "properties": {},
            "required": []
        }
    },
    {
        "name": "get_calendar_today",
        "description": "Get today's calendar events from all calendars",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "create_calendar_event",
        "description": "Create a new calendar event in Outlook/Office 365",
        "input_schema": {
            "type": "object",
            "properties": {
                "subject": {
                    "type": "string",
                    "description": "The title/subject of the event"
                },
                "start_time": {
                    "type": "string",
                    "description": "Start time in ISO format (e.g., '2026-01-13T17:15:00')"
                },
                "end_time": {
                    "type": "string",
                    "description": "End time in ISO format (e.g., '2026-01-13T18:15:00')"
                },
                "attendees": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of attendee email addresses"
                },
                "location": {
                    "type": "string",
                    "description": "Location of the event"
                }
            },
            "required": ["subject", "start_time", "end_time"]
        }
    },
    {
        "name": "get_obsidian_priorities", 
        "description": "Get weekly priorities and tasks from Obsidian",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "create_obsidian_page",
        "description": "Create a new page in Obsidian with optional content",
        "input_schema": {
            "type": "object",
            "properties": {
                "page_name": {
                    "type": "string",
                    "description": "Name of the page to create"
                },
                "content": {
                    "type": "string", 
                    "description": "Initial content for the page"
                }
            },
            "required": ["page_name"]
        }
    },
    {
        "name": "add_to_obsidian_page",
        "description": "Add content to an existing Obsidian page (or create if doesn't exist)",
        "input_schema": {
            "type": "object",
            "properties": {
                "page_name": {
                    "type": "string",
                    "description": "Name of the page to add content to"
                },
                "content": {
                    "type": "string",
                    "description": "Content to add to the page"
                }
            },
            "required": ["page_name", "content"]
        }
    },
    {
        "name": "add_task_to_weekly_plan",
        "description": "Add a task to the weekly plan in Obsidian", 
        "input_schema": {
            "type": "object",
            "properties": {
                "task_description": {
                    "type": "string",
                    "description": "Description of the task to add"
                },
                "section": {
                    "type": "string",
                    "description": "Section to add to (e.g., '## Today', '## This Week')"
                }
            },
            "required": ["task_description"]
        }
    },
    {
        "name": "complete_task",
        "description": "Mark a task as complete in the weekly plan",
        "input_schema": {
            "type": "object", 
            "properties": {
                "task_number": {
                    "type": "integer",
                    "description": "Number of the task to complete (from priorities list)"
                }
            },
            "required": ["task_number"]
        }
    }
]

async def call_function(function_name: str, parameters: Dict[str, Any]) -> str:
    """Execute a function call and return the result as a string"""
    try:
        if function_name == "start_timer":
            desc = parameters.get("task_description", "Untitled task")
            billable = parameters.get("billable", True)  # Default to True
            entry_id = await start_timer(task_id=1, billable=billable, notes=desc)
            
            # Also get current timers to show status
            active_timers = await get_all_active_entries()
            timer_count = len(active_timers)
            return f"✅ Started timer #{entry_id} for: {desc}\n⏱️ You now have {timer_count} active timer{'s' if timer_count != 1 else ''}"
            
        elif function_name == "stop_timer":
            active = await get_active_entry()
            if not active:
                return "❌ No active timer to stop"
            await stop_timer(active["id"])
            
            # Show remaining timers
            remaining_timers = await get_all_active_entries() 
            remaining_count = len(remaining_timers)
            return f"⏹️ Stopped timer #{active['id']} for: {active['notes']}\n⏱️ {remaining_count} timer{'s' if remaining_count != 1 else ''} remaining"
            
        elif function_name == "get_active_timers":
            timers = await get_all_active_entries()
            if not timers:
                return "⏱️ No active timers"
            
            result = "⏱️ **Active Timers:**\n"
            for timer in timers:
                start_time = datetime.fromisoformat(timer['start_time'])
                now = datetime.utcnow()
                duration = now - start_time
                hours = int(duration.total_seconds() // 3600)
                minutes = int((duration.total_seconds() % 3600) // 60)
                
                billable_icon = "💰" if timer['billable'] else "🆓"
                result += f"{billable_icon} **#{timer['id']}** - {timer['notes']} ({hours:02d}:{minutes:02d})\n"
            return result
            
        elif function_name == "get_calendar_today":
            return await get_today_calendar_summary()
            
        elif function_name == "create_calendar_event":
            from datetime import datetime
            subject = parameters["subject"]
            start_time_str = parameters["start_time"]
            end_time_str = parameters["end_time"]
            attendees = parameters.get("attendees", [])
            location = parameters.get("location")
            
            # Parse ISO datetime strings
            start_time = datetime.fromisoformat(start_time_str)
            end_time = datetime.fromisoformat(end_time_str)
            
            return await create_calendar_event_helper(subject, start_time, end_time, attendees, location)
            
        elif function_name == "get_obsidian_priorities":
            return await get_priorities_from_obsidian()
            
        elif function_name == "create_obsidian_page":
            page_name = parameters["page_name"]
            content = parameters.get("content", "")  # Default to empty string
            success = await create_obsidian_page(page_name, content)
            if success:
                return f"✅ Created new Obsidian page: **{page_name}.md**"
            else:
                return f"❌ Failed to create page: {page_name}"
                
        elif function_name == "add_to_obsidian_page":
            page_name = parameters["page_name"]
            content = parameters["content"]
            success = await append_to_obsidian_page(page_name, content)
            if success:
                return f"✅ Added content to **{page_name}.md** in Obsidian"
            else:
                return f"❌ Failed to update page: {page_name}"
                
        elif function_name == "add_task_to_weekly_plan":
            task_desc = parameters["task_description"]
            section = parameters.get("section", "## Today")  # Default to "## Today"
            success = await add_task_to_note(task_desc, section=section)
            if success:
                return f"✅ Added to weekly plan:\n- [ ] {task_desc}"
            else:
                return f"❌ Failed to add task: {task_desc}"
                
        elif function_name == "complete_task":
            task_num = parameters["task_number"]
            success = await complete_task_in_note(task_num)
            if success:
                return f"✅ Task #{task_num} marked as complete!"
            else:
                return f"❌ Couldn't find or complete task #{task_num}"
                
        else:
            return f"❌ Unknown function: {function_name}"
            
    except Exception as e:
        return f"❌ Error calling {function_name}: {str(e)}"

async def debby_respond(user_message: str) -> str:
    """
    Debby - AI Assistant that can think and use tools naturally
    """
    if not client:
        return "⚠️ Debby needs her Anthropic API key configured. Add ANTHROPIC_API_KEY to your .env file."
    
    system_prompt = """You are Debby, a helpful AI assistant for Lee, a product strategist and entrepreneur in the construction/retrofit/CNC business. 

You have access to several tools to help Lee manage his productivity:
- Timer management for time tracking (start, stop, view active timers)
- Calendar integration with Office 365 (view today's schedule, CREATE new events)
- Obsidian note management for priorities and planning
- Task management and completion

Key personality traits:
- Think independently and make smart decisions about which tools to use
- Be conversational and natural, not robotic
- Proactively suggest improvements to Lee's workflow
- Focus on helping Lee stay productive and avoid distractions
- Use tools automatically when it makes sense - don't ask permission

When Lee asks to add/create calendar events, USE THE create_calendar_event FUNCTION. You CAN directly add events to his calendar.
When Lee asks about timers, calendar, tasks, or wants to create/update notes, use the appropriate functions and respond naturally about what you did.

Current date and time: """ + datetime.now().strftime("%Y-%m-%d %H:%M")
    
    try:
        response = await client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=2000,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
            tools=AVAILABLE_FUNCTIONS
        )
        
        # Handle function calls
        assistant_response = ""
        
        for content_block in response.content:
            if content_block.type == "text":
                assistant_response += content_block.text
            elif content_block.type == "tool_use":
                function_name = content_block.name
                parameters = content_block.input
                
                # Execute the function
                function_result = await call_function(function_name, parameters)
                assistant_response += f"\n\n{function_result}"
        
        return assistant_response.strip() or "I'm not sure how to help with that. Could you try rephrasing?"
        
    except Exception as e:
        return f"Sorry, I had trouble processing that: {str(e)}"