"""
Conversation logging and memory management for Debby.
Stores all conversations in SQLite for later reference.
"""
import aiosqlite
from datetime import datetime
from typing import List, Tuple, Optional
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "conversations.db"

async def init_conversation_db():
    """Initialize the conversation database."""
    DB_PATH.parent.mkdir(exist_ok=True)
    
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                user_name TEXT,
                user_message TEXT NOT NULL,
                debby_response TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                action_type TEXT
            )
        """)
        await db.commit()

async def log_conversation(user_id: int, user_name: str, user_message: str, 
                          debby_response: str, action_type: str = None):
    """Log a conversation exchange to the database."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """INSERT INTO conversations 
               (user_id, user_name, user_message, debby_response, action_type) 
               VALUES (?, ?, ?, ?, ?)""",
            (user_id, user_name, user_message, debby_response, action_type)
        )
        await db.commit()

async def get_recent_conversations(user_id: int, limit: int = 5) -> List[Tuple[str, str]]:
    """Get recent conversation history for a user."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            """SELECT user_message, debby_response 
               FROM conversations 
               WHERE user_id = ? 
               ORDER BY timestamp DESC 
               LIMIT ?""",
            (user_id, limit)
        ) as cursor:
            rows = await cursor.fetchall()
            # Reverse to get chronological order (oldest first)
            return [(row[0], row[1]) for row in reversed(rows)]

async def search_conversations(user_id: int, search_term: str, limit: int = 10) -> List[dict]:
    """Search conversation history for a specific term."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            """SELECT timestamp, user_message, debby_response, action_type
               FROM conversations 
               WHERE user_id = ? 
               AND (user_message LIKE ? OR debby_response LIKE ?)
               ORDER BY timestamp DESC 
               LIMIT ?""",
            (user_id, f"%{search_term}%", f"%{search_term}%", limit)
        ) as cursor:
            rows = await cursor.fetchall()
            return [
                {
                    "timestamp": row[0],
                    "user": row[1],
                    "debby": row[2],
                    "action": row[3]
                }
                for row in rows
            ]

async def get_conversation_summary(user_id: int, days: int = 7) -> str:
    """Get a summary of conversations from the past N days."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            """SELECT COUNT(*), MIN(timestamp), MAX(timestamp)
               FROM conversations 
               WHERE user_id = ? 
               AND timestamp >= datetime('now', '-' || ? || ' days')""",
            (user_id, days)
        ) as cursor:
            row = await cursor.fetchone()
            count = row[0]
            first = row[1]
            last = row[2]
            
            if count == 0:
                return f"No conversations in the past {days} days."
            
            return f"📊 **Conversation Summary (Last {days} days)**\n" \
                   f"Total exchanges: {count}\n" \
                   f"First: {first}\n" \
                   f"Last: {last}"

async def export_conversations_to_markdown(user_id: int, days: int = 7) -> str:
    """Export recent conversations to markdown format."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            """SELECT timestamp, user_message, debby_response, action_type
               FROM conversations 
               WHERE user_id = ? 
               AND timestamp >= datetime('now', '-' || ? || ' days')
               ORDER BY timestamp ASC""",
            (user_id, days)
        ) as cursor:
            rows = await cursor.fetchall()
            
            if not rows:
                return f"# No conversations in the past {days} days"
            
            md = f"# Conversation Log\n\n"
            md += f"**User ID:** {user_id}\n"
            md += f"**Period:** Last {days} days\n"
            md += f"**Total Exchanges:** {len(rows)}\n\n---\n\n"
            
            for row in rows:
                timestamp = row[0]
                user_msg = row[1]
                debby_resp = row[2]
                action = row[3] or "CHAT"
                
                md += f"## {timestamp}\n\n"
                md += f"**Action:** {action}\n\n"
                md += f"**User:** {user_msg}\n\n"
                md += f"**Debby:** {debby_resp}\n\n"
                md += "---\n\n"
            
            return md

async def clear_old_conversations(days: int = 90):
    """Clear conversations older than N days."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """DELETE FROM conversations 
               WHERE timestamp < datetime('now', '-' || ? || ' days')""",
            (days,)
        )
        deleted = cursor.rowcount
        await db.commit()
        return deleted
