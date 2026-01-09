import aiohttp
from msal import ConfidentialClientApplication
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any

from .config import settings

GRAPH_BASE = "https://graph.microsoft.com/v1.0"

class MSGraphClient:
    def __init__(self):
        self._app = ConfidentialClientApplication(
            client_id=settings.ms_client_id,
            client_credential=settings.ms_client_secret,
            authority=f"https://login.microsoftonline.com/{settings.ms_tenant_id}"
        )
        self._access_token: str | None = None

    def _get_token(self) -> str:
        if self._access_token:
            # TODO: add expiration check if needed
            return self._access_token
        result = self._app.acquire_token_for_client(scopes=[settings.ms_scope])
        if "access_token" not in result:
            raise RuntimeError(f"Could not get token: {result}")
        self._access_token = result["access_token"]
        return self._access_token

    async def _get(self, path: str, params: dict | None = None):
        token = self._get_token()
        headers = {"Authorization": f"Bearer {token}"}
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{GRAPH_BASE}{path}", headers=headers, params=params) as resp:
                resp.raise_for_status()
                return await resp.json()

    async def get_today_calendar(self):
        """Get today's calendar events from Outlook."""
        # Get start and end of today in UTC
        now = datetime.now(timezone.utc)
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        
        params = {
            "startDateTime": start_of_day.isoformat(),
            "endDateTime": end_of_day.isoformat(),
            "$select": "subject,start,end,isAllDay,location,organizer,attendees",
            "$orderby": "start/dateTime"
        }
        return await self._get("/me/calendarview", params=params)

    async def get_calendar_events(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Get calendar events for a specific date range."""
        params = {
            "startDateTime": start_date.isoformat(),
            "endDateTime": end_date.isoformat(),
            "$select": "subject,start,end,isAllDay,location,organizer,attendees,showAs",
            "$orderby": "start/dateTime"
        }
        result = await self._get("/me/calendarview", params=params)
        return result.get("value", [])

    async def get_obsidian_file_text(self, path: str) -> str:
        """Reads a markdown file from OneDrive/Obsidian path."""
        token = self._get_token()
        headers = {"Authorization": f"Bearer {token}"}
        url = f"{GRAPH_BASE}/me/drive/root:/{path}:/content"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                resp.raise_for_status()
                return await resp.text()


def format_calendar_summary(events: List[Dict[str, Any]]) -> str:
    """Format calendar events into a readable summary."""
    if not events:
        return "No calendar events today."
    
    summary_lines = ["Today's Calendar:"]
    for event in events:
        subject = event.get("subject", "No subject")
        start_time = event.get("start", {}).get("dateTime", "")
        end_time = event.get("end", {}).get("dateTime", "")
        is_all_day = event.get("isAllDay", False)
        
        if is_all_day:
            summary_lines.append(f"  • {subject} (All day)")
        else:
            # Parse and format times
            try:
                start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                time_str = f"{start_dt.strftime('%H:%M')}-{end_dt.strftime('%H:%M')}"
                summary_lines.append(f"  • {time_str}: {subject}")
            except:
                summary_lines.append(f"  • {subject}")
    
    return "\n".join(summary_lines)


async def get_today_calendar_summary() -> str:
    """Convenience function to get today's calendar as a formatted summary."""
    client = MSGraphClient()
    result = await client.get_today_calendar()
    events = result.get("value", [])
    return format_calendar_summary(events)
