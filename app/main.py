import asyncio
from fastapi import FastAPI
from contextlib import asynccontextmanager

from .time_tracker import init_db
from .telegram_bot import build_telegram_app

telegram_app = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global telegram_app
    await init_db()
    telegram_app = build_telegram_app()
    
    # Initialize and start the telegram app
    await telegram_app.initialize()
    await telegram_app.start()
    await telegram_app.updater.start_polling()
    
    yield
    
    # Shutdown
    if telegram_app:
        await telegram_app.updater.stop()
        await telegram_app.stop()
        await telegram_app.shutdown()

app = FastAPI(title="Personal AI Agent", lifespan=lifespan)

@app.get("/health")
async def health():
    return {"status": "ok"}
