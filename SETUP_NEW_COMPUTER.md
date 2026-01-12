# Setting Up on a New Computer

This guide will help you get the Assistant bot running on any of your computers.

## Prerequisites

1. **Python 3.10+** - Download from [python.org](https://www.python.org/downloads/)
   - Make sure to check "Add Python to PATH" during installation
2. **Git** (optional) - Only needed if cloning from GitHub
3. **OneDrive** - Already syncing your work OneDrive folder

## Option 1: Using OneDrive (Recommended for your computers)

### First Time Setup

1. **Wait for OneDrive to sync** the `Assistant` folder to your computer
   - Location: `C:\Users\YourName\OneDrive - MOG Pattern & Machine Corp\Documents\GitHub\Assistant`
   - Check for green checkmarks on all files

2. **Open the folder in VS Code or File Explorer**

3. **Run the setup script**
   - Double-click `setup.bat`
   - This will:
     - Check Python installation
     - Create virtual environment
     - Install all required packages
     - Verify `.env` file exists

4. **Verify your `.env` file**
   - The `.env` file should sync via OneDrive (it's local-only, not in GitHub)
   - Check that it contains:
     ```
     TELEGRAM_BOT_TOKEN=7835240627:AAFYf9WfI1bdrdGDOfGfN0WCK2JtzCLLYD0
     ANTHROPIC_API_KEY=sk-ant-api03-...
     OBSIDIAN_LOCAL_PATH=C:\Users\YourName\OneDrive - MOG Pattern & Machine Corp\Apps\obsidian\plan_25
     OBSIDIAN_VAULT_ID=be5d785542010096
     ```
   - **Important:** Update `OBSIDIAN_LOCAL_PATH` to match the path on this computer!

5. **Start the bot**
   - Double-click `start_bot.bat`
   - Bot should start and connect to Telegram

## Option 2: Cloning from GitHub (For fresh installations)

### First Time Setup

1. **Clone the repository**
   ```powershell
   cd "C:\Users\YourName\OneDrive - MOG Pattern & Machine Corp\Documents\GitHub"
   git clone https://github.com/L33B072/Assistant.git
   cd Assistant
   ```

2. **Create `.env` file**
   ```powershell
   copy .env.example .env
   ```
   
3. **Edit `.env` with your credentials**
   - Open `.env` in a text editor
   - Fill in:
     - `TELEGRAM_BOT_TOKEN` - Your bot token
     - `ANTHROPIC_API_KEY` - Your Claude API key
     - `OBSIDIAN_LOCAL_PATH` - Path to your vault on this computer
     - `OBSIDIAN_VAULT_ID` - Your vault ID

4. **Run setup**
   ```powershell
   .\setup.bat
   ```

5. **Start the bot**
   ```powershell
   .\start_bot.bat
   ```

## Troubleshooting

### "Python not found"
- Install Python from python.org
- Make sure to check "Add Python to PATH"
- Restart your terminal after installation

### "Module not found" errors
- Run `setup.bat` again
- Make sure virtual environment activated: `.venv\Scripts\activate`
- Manually install: `pip install -r requirements.txt`

### "Bot won't start"
- Check `.env` file exists and has correct values
- Verify Telegram token is correct
- Check Obsidian path matches your computer's path structure

### "Can't connect to Obsidian"
- Verify `OBSIDIAN_LOCAL_PATH` in `.env` matches actual vault location
- **Important:** Path will be different on each computer!
- Check vault ID matches: Open Obsidian → Settings → About

### Virtual environment issues
- Delete `.venv` folder
- Run `setup.bat` again to recreate it

## Daily Usage

Once set up, just run:
```
start_bot.bat
```

The bot will run in a separate window. You can close the window to stop it.

## Updating the Bot

### If you made changes on another computer:

**Via OneDrive:**
- Wait for OneDrive to sync changes
- Restart the bot

**Via GitHub:**
```powershell
git pull origin main
.\setup.bat
.\start_bot.bat
```

### After making changes locally:

**Push to GitHub:**
```powershell
git add .
git commit -m "Description of changes"
git push origin main
```

**OneDrive will sync automatically** to your other computers.

## Important Notes

- ✅ `.env` file syncs via OneDrive (contains your secrets)
- ✅ Code syncs via both OneDrive and GitHub
- ❌ `.env` is NOT in GitHub (protected by .gitignore)
- ⚠️ Update `OBSIDIAN_LOCAL_PATH` in `.env` for each computer (paths differ!)

## Quick Reference

| File | Purpose |
|------|---------|
| `setup.bat` | First-time setup and package installation |
| `start_bot.bat` | Start the bot in a separate window |
| `.env` | Your credentials (synced via OneDrive only) |
| `requirements.txt` | List of Python packages needed |
| `run_bot.py` | Main bot script (called by start_bot.bat) |
