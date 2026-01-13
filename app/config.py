import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()  # Loads from .env in Codespace (not committed)

class Settings(BaseSettings):
    # Telegram
    telegram_bot_token: str

    # Microsoft Graph / Azure AD
    ms_client_id: str
    ms_tenant_id: str
    ms_client_secret: str
    ms_scope: str = "https://graph.microsoft.com/.default"
    ms_user_email: str = "lee.bernard@mogpm.com"  # Your work email for calendar access
    ms_user_timezone: str = "Central Standard Time"  # Outlook timezone name

    # LLM / OpenAI or others
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None

    # Obsidian / OneDrive
    obsidian_root_path: str = "/ObsidianVault"  # OneDrive path root
    obsidian_vault_id: str = "your_vault_id"  # OneDrive vault ID
    obsidian_local_path: str = r"C:\Users\leebe\OneDrive - MOG Pattern & Machine Corp\Apps\obsidian\plan_25"

    # Misc
    database_path: str = "data/time_tracking.db"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
