import aiohttp
from msal import ConfidentialClientApplication

from .config import settings

GRAPH_BASE = "https://graph.microsoft.com/v1.0"

class MSGraphClient:
    def __init__(self):
        self._app = ConfidentialClientApplication(
            client_id=settings.ms_client_id,
            client_credential=settings.ms_client_secret,
            authority=f"https://login.microsoftonline.com/{settings.ms_tenant_id}"
        )
        self._access_token: str | None = None

    def _get_token(self) -> str:
        if self._access_token:
            # TODO: add expiration check if needed
            return self._access_token
        result = self._app.acquire_token_for_client(scopes=[settings.ms_scope])
        if "access_token" not in result:
            raise RuntimeError(f"Could not get token: {result}")
        self._access_token = result["access_token"]
        return self._access_token

    async def _get(self, path: str, params: dict | None = None):
        token = self._get_token()
        headers = {"Authorization": f"Bearer {token}"}
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{GRAPH_BASE}{path}", headers=headers, params=params) as resp:
                resp.raise_for_status()
                return await resp.json()

    async def get_today_calendar(self):
        # TODO: add start/end ISO params for today
        params = {
            # Example params stub
        }
        return await self._get("/me/calendarview", params=params)

    async def get_obsidian_file_text(self, path: str) -> str:
        """Reads a markdown file from OneDrive/Obsidian path."""
        token = self._get_token()
        headers = {"Authorization": f"Bearer {token}"}
        url = f"{GRAPH_BASE}/me/drive/root:/{path}:/content"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                resp.raise_for_status()
                return await resp.text()
