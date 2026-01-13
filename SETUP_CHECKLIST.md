# Setup Checklist

## ✅ Completed
- [x] Obsidian integration (reads from local vault)
- [x] Calendar integration (Microsoft Graph API)
- [x] Calendar event creation and deletion
- [x] Timezone-aware calendar operations
- [x] Time tracking database with multiple active timers
- [x] Telegram bot with AI-first architecture
- [x] Claude AI integration for natural language processing
- [x] Conversation memory and logging
- [x] Multi-calendar support
- [x] Test scripts created

## 🔧 Configuration Needed

### 1. Create Telegram Bot
1. Message @BotFather on Telegram
2. Send `/newbot`
3. Choose a name and username for your bot
4. Copy the token and add to `.env`:
   ```
   TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
   ```

### 2. Set up Azure App Registration
1. Go to https://portal.azure.com
2. Navigate to "App Registrations" → "New registration"
3. Name: "Personal Assistant Bot"
4. Supported account types: "Single tenant"
5. Click "Register"

**Add API Permissions:**
1. Go to "API permissions" → "Add a permission"
2. Select "Microsoft Graph" → "Application permissions"
3. Add these permissions:
   - `Calendars.ReadWrite` (to read and write calendar events for all mailboxes)
   - `Files.Read.All` (to read OneDrive/Obsidian files)
4. Click "Grant admin consent" (required for Application permissions)

**Create Client Secret:**
1. Go to "Certificates & secrets" → "New client secret"
2. Description: "Bot secret"
3. Expires: Choose duration (e.g., 12 months)
4. Click "Add"
5. **COPY THE VALUE IMMEDIATELY** (you can't see it again)

**Get IDs:**
1. Go to "Overview" page
2. Copy "Application (client) ID" → MS_CLIENT_ID in .env
3. Copy "Directory (tenant) ID" → MS_TENANT_ID in .env
4. Copy the secret value → MS_CLIENT_SECRET in .env

### 3. Get Anthropic API Key (For AI features)
1. Go to https://console.anthropic.com/
2. Create an account or sign in
3. Navigate to API Keys
4. Create new secret key
5. Copy to `.env`:
   ```
   ANTHROPIC_API_KEY=sk-ant-api03-...
   ```

### 4. Configure User Settings
Update `app/config.py` with your specific settings:
```python
ms_user_email: str = "your.email@domain.com"
ms_user_timezone: str = "Central Standard Time"  # or your timezone
obsidian_local_path: str = r"C:\Users\YourName\OneDrive\path\to\vault"
```

### 5. Create WeeklyPlan.md in Obsidian
Create a file in your vault root with tasks like:
```markdown
# Weekly Plan

## This Week's Priorities
- [ ] Complete project X #work
- [ ] Review designs #creative
- [ ] Client meeting prep #urgent
- [x] This is a completed task
```

The bot will read uncompleted tasks from this file.

## 🧪 Testing Instructions

### Test 1: Obsidian Integration
```powershell
python test_obsidian.py
```
**Expected:** Should find your vault and list markdown files

### Test 2: Time Tracking
```powershell
python test_timetracker.py
```
**Expected:** Should create database and test timer start/stop

### Test 3: Run the Bot
```powershell
uvicorn app.main:app --reload
```
**Expected:** Bot starts polling Telegram, FastAPI runs on http://localhost:8000

### Test 4: Test Telegram Commands

#### Basic Commands
1. Find your bot on Telegram (search for the username you created)
2. Send `/start` - should show all available commands
3. Send `/priorities` - should read from Obsidian
4. Send `/calendar` - should show today's events
5. Send `/timers` - should show active timers

#### Natural Language (AI-powered)
Just talk naturally to Debby:
- "What's on my calendar today?"
- "Create a dinner event at 5:15 PM on January 25th"
- "Start tracking time on the CNC project"
- "Delete the calendar event at 11:15 AM"
- "Show me all active timers"

#### All Available Commands
- `/start` - Show available commands
- `/focus` - AI focus coach with priorities and calendar
- `/brainstorm <topic>` - AI brainstorming with context
- `/priorities` - View weekly priorities from Obsidian
- `/calendar` - See today's calendar events
- `/starttimer <description>` - Start tracking time
- `/stoptimer` - Stop the active timer
- `/timers` - Show all active timers
- `/history [search term]` - View or search conversation history
- `/export [days]` - Export conversation log to markdown file
- `/addtask <description>` - Add task to weekly plan
- `/completetask <number>` - Mark task as complete

## 📝 Current Status

**Working (tested):**
- ✅ Database and time tracking (multiple timers supported)
- ✅ Obsidian file reading from local path
- ✅ Telegram bot with AI-first architecture
- ✅ Claude AI natural language processing
- ✅ Calendar viewing (all calendars, timezone-aware)
- ✅ Calendar event creation with date parsing
- ✅ Calendar event deletion (single and multiple)
- ✅ Conversation memory and logging
- ✅ Conversation search and export

**Needs Configuration:**
- ⚙️ Telegram bot token (in `.env`)
- ⚙️ Azure app credentials (in `.env`)
- ⚙️ Anthropic API key (in `.env`)
- ⚙️ User email and timezone (in `app/config.py`)
- ⚙️ Obsidian vault path (in `app/config.py`)
- ⚙️ WeeklyPlan.md file in vault

**Future Enhancements:**
- 🔨 Week/month calendar views
- 🔨 Calculate billable hours per day
- 🔨 Conversation analytics
- 🔨 More Obsidian integrations

## 🚀 Quick Start (After Configuration)

1. Update `.env` with all credentials (Telegram, Azure, Anthropic)
2. Update `app/config.py` with your email, timezone, and Obsidian path
3. Create `WeeklyPlan.md` in your Obsidian vault
4. Install dependencies: `pip install -r requirements.txt`
5. Run: `uvicorn app.main:app --reload` or use `start_bot.bat`
6. Message your bot on Telegram - talk naturally or use commands!

## 🎯 Key Features

### AI-First Architecture
- **Natural Language**: Just talk to Debby naturally
- **Context Aware**: Remembers recent conversation history
- **Smart Decisions**: Claude analyzes intent and executes appropriate actions

### Calendar Management
- View today's events across all calendars
- Create events with natural date parsing
- Delete events by time or subject
- Timezone-aware (displays in your local time)

### Conversation Memory
- All conversations stored in SQLite database
- Search past conversations: `/history calendar`
- Export to markdown: `/export 30` (last 30 days)
- Debby remembers context for follow-up questions

## 🐛 Troubleshooting

**"Could not get authority configuration"**
- Your MS_TENANT_ID in `.env` is still set to the placeholder "yourtenant"
- Update with your actual Azure tenant ID

**"WeeklyPlan.md not found"**
- Create this file in your vault root, or modify the code to use a different file

**"No calendar events today"**
- Either you have no events scheduled, or Azure permissions aren't configured
- Verify `Calendars.ReadWrite` permission is granted in Azure

**Bot doesn't respond**
- Check that uvicorn is running (or `start_bot.bat`)
- Check that your bot token is correct in `.env`
- Check terminal for error messages

**"Debby needs her Anthropic API key configured"**
- Add `ANTHROPIC_API_KEY=sk-ant-...` to your `.env` file
- Get key from https://console.anthropic.com/

**Calendar shows events from wrong timezone**
- Update `ms_user_timezone` in `app/config.py`
- Use Windows timezone name (e.g., "Central Standard Time")

**Events showing from yesterday/tomorrow**
- Calendar uses UTC internally - filtering is timezone-aware
- Verify your timezone setting in `app/config.py`
