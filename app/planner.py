from typing import Any

from .prompts import BRAINSTORM_PROMPT, FOCUS_COACH_PROMPT

# here you'd plug in your LLM client, e.g. OpenAI
# from openai import AsyncOpenAI
# client = AsyncOpenAI(api_key=settings.openai_api_key)

async def brainstorm(context: str, question: str) -> str:
    """Use LLM to brainstorm based on Obsidian/context + question."""
    # PSEUDOCODE – replace with your LLM of choice
    # resp = await client.chat.completions.create(
    #     model="gpt-4.1-mini",
    #     messages=[
    #         {"role": "system", "content": BRAINSTORM_PROMPT},
    #         {"role": "user", "content": f"Context:\n{context}\n\nQuestion:\n{question}"}
    #     ]
    # )
    # return resp.choices[0].message.content
    return "Brainstorming result placeholder."

async def focus_check(
    priorities_text: str,
    calendar_summary: str,
    current_task_desc: str,
    billable_today_hours: float,
) -> str:
    """Use LLM to evaluate whether you're on the right task."""
    # PSEUDOCODE for LLM call
    # resp = await client.chat.completions.create(...)
    return "Focus check placeholder. (Would tell you if you're off track.)"
