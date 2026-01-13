# Personal AI Assistant - Debby

A Telegram-based AI assistant powered by Claude that integrates with:
- 📝 **Obsidian** - Task tracking and note management
- 📅 **Microsoft Outlook** - Calendar integration via Graph API
- ⏱️ **Time Tracking** - SQLite-based billable hours tracking
- 🤖 **AI** - Claude AI-first architecture with natural language processing
- 💾 **Conversation Memory** - Persistent conversation logging and search

## Features

### Natural Language Interaction
Debby uses AI-first architecture where Claude analyzes your intent and executes actions. Just talk naturally:
- "What's on my calendar today?"
- "Create a dinner event at 5:15 PM on January 25th"
- "Delete both calendar events about the garage"
- "Start tracking time on the CNC project"

### Telegram Commands
- `/start` - Show available commands and introduction
- `/focus` - AI focus coach (compares priorities, calendar, and current task)
- `/brainstorm <topic>` - AI brainstorming with Obsidian context
- `/priorities` - View your weekly priorities from Obsidian
- `/calendar` - See today's calendar events
- `/starttimer <description>` - Start tracking time on a task
- `/stoptimer` - Stop the active timer
- `/timers` - Show all active timers
- `/history [search term]` - View or search conversation history
- `/export [days]` - Export conversation log to markdown file (default: 7 days)

### AI Capabilities
- **Calendar Management**: View, create, and delete calendar events with timezone awareness
- **Time Tracking**: Start/stop timers for billable work
- **Task Management**: Obsidian integration for priorities and tasks
- **Conversation Memory**: Remembers context from previous exchanges
- **Persistent Logging**: All conversations stored in SQLite database

### Integrations
- **Obsidian**: Reads tasks and notes from your local OneDrive-synced vault
- **Microsoft Graph**: Accesses Outlook calendar and OneDrive files
- **Time Tracking**: SQLite database with clients, projects, tasks, and time entries

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your credentials:

```bash
# Telegram Bot (get from @BotFather on Telegram)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# Microsoft Graph / Azure AD (create an Azure App Registration)
MS_CLIENT_ID=your_azure_app_client_id
MS_TENANT_ID=your_azure_tenant_id
MS_CLIENT_SECRET=your_azure_client_secret

# Anthropic Claude API (for AI features)
ANTHROPIC_API_KEY=sk-ant-your_anthropic_api_key
```

### 3. Configure Settings

Update `app/config.py` with your specific settings:
```python
# User timezone (for calendar operations)
ms_user_timezone: str = "Central Standard Time"

# User email (for Microsoft Graph API)
ms_user_email: str = "your.email@domain.com"

# Obsidian vault path
obsidian_local_path: str = r"C:\Users\user\OneDrive\Apps\obsidian\your_vault"
```

### 4. Run Tests

Test Obsidian integration:
```bash
python test_obsidian.py
```

Test time tracking:
```bash
python test_timetracker.py
```

### 5. Run the Bot

```bash
uvicorn app.main:app --reload
```

The bot will start polling Telegram in the background while the FastAPI server runs.

## Project Structure

```
Assistant/
├── app/
│   ├── config.py              # Settings and environment variables
│   ├── main.py                # FastAPI app entry point
│   ├── telegram_bot.py        # Telegram bot with AI-first architecture
│   ├── ai_assistant.py        # Debby's AI brain (function definitions)
│   ├── msgraph_client.py      # Microsoft Graph API client (Calendar)
│   ├── obsidian_tasks.py      # Obsidian note/task parsing
│   ├── time_tracker.py        # SQLite time tracking database
│   ├── conversation_log.py    # Conversation memory and logging
│   ├── planner.py             # Claude AI integration (brainstorm)
│   └── prompts.py             # LLM system prompts
├── data/                      # SQLite database files
│   ├── timetracker.db         # Time tracking data
│   └── conversations.db       # Conversation history
├── test_*.py                  # Test scripts
├── requirements.txt           # Python dependencies
└── .env                       # Environment variables (NOT COMMITTED)
```

## Azure App Registration Setup

To use Microsoft Graph API:

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to "App Registrations" → "New registration"
3. Set up application permissions:
   - `Calendars.ReadWrite` - Read and write calendar events (all mailboxes)
   - `Files.Read.All` - Read OneDrive files (for Obsidian sync)
4. Create a client secret under "Certificates & secrets"
5. Copy the Application (client) ID, Directory (tenant) ID, and client secret to `.env`

**Note**: The app uses **Application** permissions (not Delegated), so it requires admin consent.

## Telegram Bot Setup

1. Message [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/newbot` and follow the prompts
3. Copy the bot token to `.env`

## Next Steps

- [x] Implement Claude AI integration
- [x] Add calendar create/delete operations
- [x] Conversation memory and logging
- [x] Timezone-aware calendar operations
- [x] Multi-event deletion support
- [ ] Add task CRUD operations in Obsidian
- [ ] Calculate billable hours per day
- [ ] Deploy to cloud hosting
- [ ] Add week/month calendar views
- [ ] Conversation analytics and insights

## Key Features

### AI-First Architecture
Debby doesn't use pattern matching - she uses Claude to understand your intent, extract parameters, and decide which action to take. This makes interactions feel natural and conversational.

### Timezone Awareness
All calendar operations are timezone-aware (configurable in settings). Events are displayed in your local time, and you can specify event times naturally.

### Conversation Memory
All conversations are logged to SQLite with timestamps and action types. You can:
- Search past conversations with `/history <search term>`
- Export conversation logs to markdown with `/export [days]`
- Debby remembers recent context for follow-up questions

### Multi-Calendar Support
Integrates with all calendars in your Outlook account, displaying which calendar each event belongs to.

## Testing

The project includes test scripts:
- `test_obsidian.py` - Verifies Obsidian vault access and task parsing
- `test_timetracker.py` - Tests database and time tracking functionality

## License

Private project
