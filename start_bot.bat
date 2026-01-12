@echo off
cd /d "%~dp0"
start "Telegram Bot" cmd /k ".\.venv\Scripts\python.exe run_bot.py"
