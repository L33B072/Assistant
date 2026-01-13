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

    async def _post(self, path: str, data: dict):
        token = self._get_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{GRAPH_BASE}{path}", headers=headers, json=data) as resp:
                resp.raise_for_status()
                return await resp.json()

    async def _delete(self, path: str):
        token = self._get_token()
        headers = {"Authorization": f"Bearer {token}"}
        async with aiohttp.ClientSession() as session:
            async with session.delete(f"{GRAPH_BASE}{path}", headers=headers) as resp:
                resp.raise_for_status()
                return True

    async def get_all_calendars(self):
        """Get all calendars the user has access to."""
        return await self._get(f"/users/{settings.ms_user_email}/calendars")

    async def get_today_calendar(self):
        """Get today's calendar events from ALL calendars."""
        # Get start and end of today in LOCAL timezone
        from datetime import datetime
        import pytz
        
        # Get current local time
        local_tz = pytz.timezone('America/Chicago')
        now = datetime.now(local_tz)  # Local time with timezone
        
        # Get start and end of TODAY only in local timezone
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        print(f"DEBUG: Today is {now.strftime('%A, %B %d, %Y')}")
        print(f"DEBUG: Fetching events from {start_of_day} to {end_of_day}")
        
        # Get all calendars first
        calendars_result = await self.get_all_calendars()
        all_calendars = calendars_result.get("value", [])
        
        all_events = []
        
        # Get events from each calendar
        for calendar in all_calendars:
            calendar_id = calendar.get("id")
            calendar_name = calendar.get("name", "Unknown Calendar")
            
            try:
                params = {
                    "startDateTime": start_of_day.isoformat(),
                    "endDateTime": end_of_day.isoformat(),
                    "$select": "subject,start,end,isAllDay,location,organizer,attendees",
                    "$orderby": "start/dateTime"
                }
                
                calendar_events = await self._get(f"/users/{settings.ms_user_email}/calendars/{calendar_id}/calendarview", params=params)
                events = calendar_events.get("value", [])
                
                # Add calendar name to each event
                for event in events:
                    event["calendarName"] = calendar_name
                
                all_events.extend(events)
                
            except Exception as e:
                print(f"Error fetching calendar {calendar_name}: {e}")
                continue
        
        # Sort all events by start time
        all_events.sort(key=lambda x: x.get("start", {}).get("dateTime", ""))
        
        return {"value": all_events}

    async def get_calendar_events(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Get calendar events for a specific date range."""
        params = {
            "startDateTime": start_date.isoformat(),
            "endDateTime": end_date.isoformat(),
            "$select": "subject,start,end,isAllDay,location,organizer,attendees,showAs",
            "$orderby": "start/dateTime"
        }
        result = await self._get(f"/users/{settings.ms_user_email}/calendarview", params=params)
        return result.get("value", [])

    async def create_calendar_event(self, subject: str, start_time: datetime, end_time: datetime, 
                                   attendees: List[str] = None, location: str = None, body: str = None) -> Dict[str, Any]:
        """Create a new calendar event."""
        event_data = {
            "subject": subject,
            "start": {
                "dateTime": start_time.isoformat(),
                "timeZone": settings.ms_user_timezone  # Use user's local timezone
            },
            "end": {
                "dateTime": end_time.isoformat(),
                "timeZone": settings.ms_user_timezone  # Use user's local timezone
            }
        }
        
        if attendees:
            event_data["attendees"] = [
                {
                    "emailAddress": {"address": email},
                    "type": "required"
                }
                for email in attendees
            ]
        
        if location:
            event_data["location"] = {"displayName": location}
        
        if body:
            event_data["body"] = {
                "contentType": "text",
                "content": body
            }
        
        result = await self._post(f"/users/{settings.ms_user_email}/calendar/events", event_data)
        return result

    async def delete_calendar_event(self, event_id: str) -> bool:
        """Delete a calendar event by ID."""
        await self._delete(f"/users/{settings.ms_user_email}/calendar/events/{event_id}")
        return True

    async def find_events_by_time_or_subject(self, time_str: str = None, subject_keywords: str = None) -> List[Dict[str, Any]]:
        """Find events matching time or subject keywords from today's calendar."""
        today_result = await self.get_today_calendar()
        events = today_result.get("value", [])
        
        matching_events = []
        for event in events:
            # Check time match - convert to local time for comparison
            if time_str:
                from datetime import datetime
                import pytz
                
                event_time = event.get("start", {}).get("dateTime", "")
                event_tz_name = event.get("start", {}).get("timeZone", "UTC")
                
                try:
                    # Parse the event time
                    event_dt = datetime.fromisoformat(event_time)
                    event_tz = pytz.timezone(event_tz_name) if event_tz_name != "UTC" else pytz.UTC
                    event_dt_aware = event_tz.localize(event_dt)
                    
                    # Convert to local time
                    local_tz = pytz.timezone('America/Chicago')
                    event_dt_local = event_dt_aware.astimezone(local_tz)
                    
                    # Format as string for comparison
                    event_time_str = event_dt_local.strftime('%I:%M %p').lstrip('0').lower()
                    
                    print(f"DEBUG: Comparing '{time_str.lower()}' with event time '{event_time_str}'")
                    
                    # Check if the time string matches
                    if time_str.lower() in event_time_str:
                        matching_events.append(event)
                        continue
                except Exception as e:
                    print(f"DEBUG: Error parsing event time: {e}")
                    pass
            
            # Check subject match
            if subject_keywords:
                subject = event.get("subject", "").lower()
                if subject_keywords.lower() in subject:
                    matching_events.append(event)
        
        return matching_events

    async def get_obsidian_file_text(self, path: str) -> str:
        """Reads a markdown file from OneDrive/Obsidian path."""
        token = self._get_token()
        headers = {"Authorization": f"Bearer {token}"}
        url = f"{GRAPH_BASE}/users/{settings.ms_user_email}/drive/root:/{path}:/content"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                resp.raise_for_status()
                return await resp.text()


def format_calendar_summary(events: List[Dict[str, Any]]) -> str:
    """Format calendar events into a readable summary."""
    if not events:
        return "No calendar events today."
    
    from datetime import datetime
    
    # Get today's date in local time for filtering
    today = datetime.now().date()
    
    summary_lines = ["Today's Calendar:"]
    for event in events:
        subject = event.get("subject", "No subject")
        start_time = event.get("start", {}).get("dateTime", "")
        end_time = event.get("end", {}).get("dateTime", "")
        is_all_day = event.get("isAllDay", False)
        calendar_name = event.get("calendarName", "")
        
        # Add calendar name in parentheses if available
        calendar_suffix = f" [{calendar_name}]" if calendar_name else ""
        
        # Parse and check date for both all-day and timed events
        try:
            # Get the timezone from the event
            start_tz = event.get("start", {}).get("timeZone", "UTC")
            print(f"DEBUG Event: {subject}, Start: {start_time}, TZ: {start_tz}")
            
            # Parse the datetime - Graph API returns them without timezone info
            start_dt = datetime.fromisoformat(start_time)
            
            # Convert to local time
            import pytz
            local_tz = pytz.timezone('America/Chicago')
            
            # The datetime from Graph is in the timezone specified in the event
            event_tz = pytz.timezone(start_tz) if start_tz != "UTC" else pytz.UTC
            start_dt_aware = event_tz.localize(start_dt)
            start_dt_local = start_dt_aware.astimezone(local_tz)
            
            # Only show events that start TODAY in local time
            if start_dt_local.date() != today:
                continue
        except Exception as e:
            print(f"DEBUG: Error parsing event {subject}: {e}")
            # If we can't parse the date, skip this event
            continue
        
        if is_all_day:
            summary_lines.append(f"  • {subject} (All day){calendar_suffix}")
        else:
            # Format times for regular events
            try:
                import pytz
                local_tz = pytz.timezone('America/Chicago')
                
                # Get end time and timezone
                end_tz = event.get("end", {}).get("timeZone", "UTC")
                end_dt = datetime.fromisoformat(end_time)
                
                # Convert end time to local
                event_end_tz = pytz.timezone(end_tz) if end_tz != "UTC" else pytz.UTC
                end_dt_aware = event_end_tz.localize(end_dt)
                end_dt_local = end_dt_aware.astimezone(local_tz)
                
                # Format in 12-hour time with AM/PM (Windows compatible)
                time_str = f"{start_dt_local.strftime('%I:%M %p').lstrip('0')}-{end_dt_local.strftime('%I:%M %p').lstrip('0')}"
                summary_lines.append(f"  • {time_str}: {subject}{calendar_suffix}")
            except Exception as e:
                print(f"Error formatting event: {e}")
                summary_lines.append(f"  • {subject}{calendar_suffix}")
    
    if len(summary_lines) == 1:
        return "No calendar events today."
    
    return "\n".join(summary_lines)


async def get_today_calendar_summary() -> str:
    """Convenience function to get today's calendar as a formatted summary."""
    client = MSGraphClient()
    result = await client.get_today_calendar()
    events = result.get("value", [])
    return format_calendar_summary(events)

async def create_calendar_event_helper(subject: str, start_time: datetime, end_time: datetime, 
                                       attendees: List[str] = None, location: str = None) -> str:
    """Helper function to create a calendar event and return a formatted message."""
    try:
        client = MSGraphClient()
        event = await client.create_calendar_event(subject, start_time, end_time, attendees, location)
        
        # Format success message
        time_str = start_time.strftime("%I:%M %p")
        msg = f"✅ Created calendar event:\n📅 **{subject}**\n🕐 {time_str}"
        
        if attendees:
            msg += f"\n👥 Attendees: {', '.join(attendees)}"
        if location:
            msg += f"\n📍 Location: {location}"
        
        return msg
    except Exception as e:
        return f"❌ Failed to create calendar event: {str(e)}"

async def delete_calendar_event_helper(time_str: str = None, subject_keywords: str = None) -> str:
    """Helper function to delete calendar events by time or subject."""
    try:
        client = MSGraphClient()
        
        # Find matching events
        matching_events = await client.find_events_by_time_or_subject(time_str, subject_keywords)
        
        if not matching_events:
            return "❌ No matching events found to delete"
        
        if len(matching_events) > 1:
            # Multiple matches - list them
            msg = f"⚠️ Found {len(matching_events)} matching events:\n"
            for i, event in enumerate(matching_events, 1):
                subject = event.get("subject", "No subject")
                start = event.get("start", {}).get("dateTime", "")
                msg += f"{i}. {subject} at {start}\n"
            msg += "\nPlease be more specific about which event to delete."
            return msg
        
        # Single match - delete it
        event = matching_events[0]
        event_id = event.get("id")
        subject = event.get("subject", "Event")
        
        await client.delete_calendar_event(event_id)
        return f"✅ Deleted calendar event: **{subject}**"
        
    except Exception as e:
        return f"❌ Failed to delete calendar event: {str(e)}"

async def delete_multiple_events_helper(subject_keywords: str) -> str:
    """Helper function to delete ALL matching calendar events by subject."""
    try:
        client = MSGraphClient()
        
        # Find matching events
        matching_events = await client.find_events_by_time_or_subject(None, subject_keywords)
        
        if not matching_events:
            return "❌ No matching events found to delete"
        
        # Delete all matching events
        deleted_count = 0
        for event in matching_events:
            try:
                event_id = event.get("id")
                await client.delete_calendar_event(event_id)
                deleted_count += 1
            except Exception as e:
                print(f"Error deleting event: {e}")
        
        if deleted_count == len(matching_events):
            return f"✅ Deleted {deleted_count} calendar event(s) matching '{subject_keywords}'"
        else:
            return f"⚠️ Deleted {deleted_count} of {len(matching_events)} events. Some deletions failed."
        
    except Exception as e:
        return f"❌ Failed to delete calendar events: {str(e)}"
