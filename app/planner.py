from typing import Any
from anthropic import AsyncAnthropic

from .prompts import BRAINSTORM_PROMPT, FOCUS_COACH_PROMPT
from .config import settings

# Initialize Anthropic client
client = AsyncAnthropic(api_key=settings.anthropic_api_key) if settings.anthropic_api_key else None

async def brainstorm(context: str, question: str) -> str:
    """Use Claude to brainstorm based on Obsidian/context + question."""
    if not client:
        return "⚠️ Anthropic API key not configured. Add ANTHROPIC_API_KEY to your .env file."
    
    try:
        response = await client.messages.create(
            model="claude-sonnet-4-5-20250929",  # Claude Sonnet 4.5 - most capable model
            max_tokens=2000,
            system=BRAINSTORM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": f"Context from my notes and calendar:\n{context}\n\nQuestion:\n{question}"
                }
            ]
        )
        return response.content[0].text
    except Exception as e:
        return f"Error calling Claude: {str(e)}"

async def focus_check(
    priorities_text: str,
    calendar_summary: str,
    current_task_desc: str,
    billable_today_hours: float,
) -> str:
    """Use Claude to evaluate whether you're on the right task."""
    if not client:
        return "⚠️ Anthropic API key not configured. Add ANTHROPIC_API_KEY to your .env file."
    
    try:
        user_message = f"""Here's my current situation:

PRIORITIES:
{priorities_text}

TODAY'S CALENDAR:
{calendar_summary}

CURRENT TASK:
{current_task_desc}

BILLABLE HOURS TODAY:
{billable_today_hours:.1f} hours

Am I working on the right thing? Should I switch focus?"""

        response = await client.messages.create(
            model="claude-sonnet-4-5-20250929",  # Claude Sonnet 4.5 - most capable model
            max_tokens=1000,
            system=FOCUS_COACH_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": user_message
                }
            ]
        )
        return response.content[0].text
    except Exception as e:
        return f"Error calling Claude: {str(e)}"
