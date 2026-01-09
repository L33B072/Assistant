# Personal AI Assistant

A Telegram-based AI assistant that integrates with:
- 📝 **Obsidian** - Task tracking and note management
- 📅 **Microsoft Outlook** - Calendar integration via Graph API
- ⏱️ **Time Tracking** - SQLite-based billable hours tracking
- 🤖 **AI** - LLM-powered brainstorming and focus coaching

## Features

### Telegram Commands
- `/start` - Show available commands
- `/focus` - AI focus coach (compares priorities, calendar, and current task)
- `/brainstorm <topic>` - AI brainstorming with Obsidian context
- `/priorities` - View your weekly priorities from Obsidian
- `/calendar` - See today's calendar events
- `/starttimer <description>` - Start tracking time on a task
- `/stoptimer` - Stop the active timer

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

# OpenAI (for LLM features)
OPENAI_API_KEY=sk-your_openai_api_key
```

### 3. Configure Obsidian Path

The Obsidian vault path is configured in `app/config.py`:
```python
obsidian_local_path: str = r"C:\Users\leebe\OneDrive - MOG Pattern & Machine Corp\Apps\obsidian\plan_25"
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
│   ├── config.py           # Settings and environment variables
│   ├── main.py             # FastAPI app entry point
│   ├── telegram_bot.py     # Telegram bot commands and handlers
│   ├── msgraph_client.py   # Microsoft Graph API client
│   ├── obsidian_tasks.py   # Obsidian note/task parsing
│   ├── time_tracker.py     # SQLite time tracking database
│   ├── planner.py          # LLM integration (brainstorm, focus)
│   └── prompts.py          # LLM system prompts
├── data/                   # SQLite database files
├── test_obsidian.py        # Test Obsidian integration
├── test_timetracker.py     # Test time tracking
├── requirements.txt        # Python dependencies
└── .env                    # Environment variables (not committed)
```

## Azure App Registration Setup

To use Microsoft Graph API:

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to "App Registrations" → "New registration"
3. Set up application permissions:
   - `Calendars.Read` - Read calendar events
   - `Files.Read.All` - Read OneDrive files (for Obsidian)
4. Create a client secret under "Certificates & secrets"
5. Copy the Application (client) ID, Directory (tenant) ID, and client secret to `.env`

## Telegram Bot Setup

1. Message [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/newbot` and follow the prompts
3. Copy the bot token to `.env`

## Next Steps

- [ ] Implement LLM integration (OpenAI/Anthropic) in `planner.py`
- [ ] Add task CRUD operations
- [ ] Calculate billable hours per day
- [ ] Deploy to cloud hosting
- [ ] Add more calendar features (tomorrow, week view)

## Testing

The project includes test scripts:
- `test_obsidian.py` - Verifies Obsidian vault access and task parsing
- `test_timetracker.py` - Tests database and time tracking functionality

## License

Private project
