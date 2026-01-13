import aiosqlite
from datetime import datetime
from typing import Optional, List

from .config import settings

DB_PATH = settings.database_path

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript(
            """
            PRAGMA journal_mode=WAL;

            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            );

            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER REFERENCES clients(id),
                name TEXT NOT NULL,
                UNIQUE(client_id, name)
            );

            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER REFERENCES projects(id),
                description TEXT NOT NULL,
                obsidian_note TEXT,
                obsidian_line INTEGER,
                tags TEXT
            );

            CREATE TABLE IF NOT EXISTS time_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER REFERENCES tasks(id),
                start_time TEXT NOT NULL,
                end_time TEXT,
                billable INTEGER DEFAULT 1,
                notes TEXT
            );
            """
        )
        await db.commit()

async def start_timer(task_id: int, billable: bool = True, notes: str = "") -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        now = datetime.utcnow().isoformat()
        cursor = await db.execute(
            """
            INSERT INTO time_entries (task_id, start_time, billable, notes)
            VALUES (?, ?, ?, ?)
            """,
            (task_id, now, 1 if billable else 0, notes),
        )
        await db.commit()
        return cursor.lastrowid

async def stop_timer(entry_id: int) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        now = datetime.utcnow().isoformat()
        await db.execute(
            "UPDATE time_entries SET end_time = ? WHERE id = ? AND end_time IS NULL",
            (now, entry_id),
        )
        await db.commit()

async def get_active_entry() -> Optional[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT id, task_id, start_time, billable, notes FROM time_entries WHERE end_time IS NULL ORDER BY id DESC LIMIT 1"
        )
        row = await cursor.fetchone()
        if not row:
            return None
        return {
            "id": row[0],
            "task_id": row[1],
            "start_time": row[2],
            "billable": bool(row[3]),
            "notes": row[4],
        }

async def get_all_active_entries() -> List[dict]:
    """Get all currently running timers"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT id, task_id, start_time, billable, notes FROM time_entries WHERE end_time IS NULL ORDER BY start_time DESC"
        )
        rows = await cursor.fetchall()
        return [
            {
                "id": row[0],
                "task_id": row[1],
                "start_time": row[2],
                "billable": bool(row[3]),
                "notes": row[4],
            }
            for row in rows
        ]
