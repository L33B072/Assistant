import asyncio
from fastapi import FastAPI

from .time_tracker import init_db
from .telegram_bot import build_telegram_app

app = FastAPI(title="Personal AI Agent")

telegram_app = build_telegram_app()

@app.on_event("startup")
async def startup_event():
    # Init DB
    await init_db()
    # Start Telegram polling in background
    asyncio.create_task(telegram_app.run_polling(close_loop=False))

@app.get("/health")
async def health():
    return {"status": "ok"}
