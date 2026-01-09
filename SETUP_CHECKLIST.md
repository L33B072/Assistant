# Setup Checklist

## ✅ Completed
- [x] Obsidian integration (reads from local vault)
- [x] Calendar integration (Microsoft Graph API)
- [x] Time tracking database
- [x] Telegram bot structure
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
   - `Calendars.Read` (to read calendar events)
   - `Files.Read.All` (to read OneDrive/Obsidian files)
4. Click "Grant admin consent"

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

### 3. Get OpenAI API Key (Optional - for LLM features)
1. Go to https://platform.openai.com/api-keys
2. Create new secret key
3. Copy to `.env`:
   ```
   OPENAI_API_KEY=sk-proj-...
   ```

### 4. Create WeeklyPlan.md in Obsidian
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
1. Find your bot on Telegram (search for the username you created)
2. Send `/start` - should show available commands
3. Send `/priorities` - should read from Obsidian (or show error if WeeklyPlan.md missing)
4. Send `/calendar` - should fetch today's events (or show auth error if Azure not configured)
5. Send `/starttimer Test task` - should start tracking time
6. Send `/stoptimer` - should stop the timer

## 📝 Current Status

**Working (tested):**
- ✅ Database and time tracking
- ✅ Obsidian file reading from local path
- ✅ Telegram bot command structure

**Needs Configuration:**
- ⚙️ Telegram bot token
- ⚙️ Azure app credentials
- ⚙️ OpenAI API key
- ⚙️ WeeklyPlan.md file in vault

**Needs Implementation:**
- 🔨 LLM calls in `planner.py` (currently returns placeholders)
- 🔨 Calculate billable hours per day
- 🔨 Task CRUD operations

## 🚀 Quick Start (After Configuration)

1. Update `.env` with all credentials
2. Create `WeeklyPlan.md` in your Obsidian vault
3. Run: `uvicorn app.main:app --reload`
4. Message your bot on Telegram

## 🐛 Troubleshooting

**"Could not get authority configuration"**
- Your MS_TENANT_ID in `.env` is still set to the placeholder "yourtenant"

**"WeeklyPlan.md not found"**
- Create this file in your vault root, or modify the code to use a different file

**"No calendar events today"**
- Either you have no events, or Azure permissions aren't configured

**Bot doesn't respond**
- Check that uvicorn is running
- Check that your bot token is correct
- Check terminal for error messages
