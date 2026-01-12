@echo off
echo ========================================
echo Assistant Bot Setup Script
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10+ from python.org
    pause
    exit /b 1
)

echo [1/5] Python found: 
python --version
echo.

REM Check if virtual environment exists
if exist ".venv\Scripts\activate.bat" (
    echo [2/5] Virtual environment found
) else (
    echo [2/5] Creating virtual environment...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment created successfully
)
echo.

REM Activate virtual environment
echo [3/5] Activating virtual environment...
call .venv\Scripts\activate.bat
echo.

REM Upgrade pip
echo [4/5] Upgrading pip...
python -m pip install --upgrade pip --quiet
echo.

REM Install/update requirements
echo [5/5] Installing required packages...
pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    echo ERROR: Failed to install packages
    pause
    exit /b 1
)
echo.

echo ========================================
echo Setup Complete!
echo ========================================
echo.

REM Check if .env file exists
if exist ".env" (
    echo [OK] .env file found
) else (
    echo [WARNING] .env file NOT found
    echo.
    echo You need to create a .env file with your credentials:
    echo   - TELEGRAM_BOT_TOKEN=your_token_here
    echo   - ANTHROPIC_API_KEY=your_key_here
    echo   - OBSIDIAN_LOCAL_PATH=C:\path\to\your\vault
    echo   - OBSIDIAN_VAULT_ID=your_vault_id
    echo.
    echo Copy .env.example to .env and fill in your values
)
echo.

REM Display installed packages
echo Installed packages:
pip list | findstr "python-telegram-bot anthropic fastapi pydantic"
echo.

echo ========================================
echo Ready to run!
echo ========================================
echo.
echo To start the bot, run: start_bot.bat
echo.
pause
