"""
Simple standalone Telegram bot runner
Run this directly without FastAPI for easier testing
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from app.telegram_bot import build_telegram_app
from app.time_tracker import init_db

async def main():
    print("=" * 60)
    print("Starting Telegram Bot")
    print("=" * 60)
    
    # Initialize database
    print("\n[1/4] Initializing database...")
    await init_db()
    print("✅ Database ready")
    
    # Build Telegram application
    print("\n[2/4] Building Telegram bot...")
    application = build_telegram_app()
    print("✅ Bot built")
    
    # Initialize the application
    print("\n[3/4] Initializing bot...")
    await application.initialize()
    await application.start()
    print("✅ Bot initialized")
    
    # Start polling
    print("\n[4/4] Starting bot polling...")
    await application.updater.start_polling(
        allowed_updates=["message", "callback_query"]
    )
    print("✅ Bot is running! Send /start to your bot on Telegram")
    print("   Bot username: @mog_outlook_bot")
    print("   Link: https://t.me/mog_outlook_bot")
    print("\nPress Ctrl+C to stop\n")
    print("=" * 60)
    
    # Keep running until interrupted
    try:
        # Run forever
        await asyncio.Event().wait()
    finally:
        # Cleanup
        print("\nShutting down...")
        await application.updater.stop()
        await application.stop()
        await application.shutdown()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n" + "=" * 60)
        print("Bot stopped by user")
        print("=" * 60)
