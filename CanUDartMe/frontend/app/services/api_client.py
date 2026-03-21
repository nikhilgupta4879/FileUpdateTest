"""
Async HTTP client wrapping all backend REST endpoints.
"""
import httpx
from app.utils.constants import API_BASE_URL


class ApiClient:
    def __init__(self, token: str | None = None):
        self._token = token
        self._base = API_BASE_URL

    def _headers(self) -> dict:
        h = {"Content-Type": "application/json"}
        if self._token:
            h["Authorization"] = f"Bearer {self._token}"
        return h

    def set_token(self, token: str):
        self._token = token

    # ------------------------------------------------------------------ #
    # Auth                                                                  #
    # ------------------------------------------------------------------ #
    async def register(self, profile_name: str, email: str, password: str) -> dict:
        async with httpx.AsyncClient() as client:
            r = await client.post(f"{self._base}/api/v1/auth/register",
                                  json={"profile_name": profile_name, "email": email, "password": password})
            r.raise_for_status()
            return r.json()

    async def login(self, email: str, password: str) -> dict:
        async with httpx.AsyncClient() as client:
            r = await client.post(f"{self._base}/api/v1/auth/token",
                                  json={"profile_name": "", "email": email, "password": password})
            r.raise_for_status()
            return r.json()

    # ------------------------------------------------------------------ #
    # Users                                                                 #
    # ------------------------------------------------------------------ #
    async def get_me(self) -> dict:
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{self._base}/api/v1/users/me", headers=self._headers())
            r.raise_for_status()
            return r.json()

    async def find_friend(self, profile_name: str) -> dict:
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{self._base}/api/v1/users/search",
                                 params={"profile_name": profile_name}, headers=self._headers())
            r.raise_for_status()
            return r.json()

    # ------------------------------------------------------------------ #
    # Groups                                                                #
    # ------------------------------------------------------------------ #
    async def create_group(self, name: str, is_public: bool = True) -> dict:
        async with httpx.AsyncClient() as client:
            r = await client.post(f"{self._base}/api/v1/groups/",
                                  json={"name": name, "is_public": is_public}, headers=self._headers())
            r.raise_for_status()
            return r.json()

    async def search_groups(self, query: str) -> list[dict]:
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{self._base}/api/v1/groups/search",
                                 params={"q": query}, headers=self._headers())
            r.raise_for_status()
            return r.json()

    async def join_group(self, group_id: str) -> dict:
        async with httpx.AsyncClient() as client:
            r = await client.post(f"{self._base}/api/v1/groups/join",
                                  json={"group_id": group_id}, headers=self._headers())
            r.raise_for_status()
            return r.json()

    async def toggle_favorite(self, group_id: str) -> dict:
        async with httpx.AsyncClient() as client:
            r = await client.post(f"{self._base}/api/v1/groups/{group_id}/favorite",
                                  headers=self._headers())
            r.raise_for_status()
            return r.json()

    # ------------------------------------------------------------------ #
    # Sessions                                                              #
    # ------------------------------------------------------------------ #
    async def list_sessions(self) -> list[dict]:
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{self._base}/api/v1/sessions/", headers=self._headers())
            r.raise_for_status()
            return r.json()

    async def create_session(self, group_id: str, dart_travel_time: float = 2.0, max_players: int = 6) -> dict:
        async with httpx.AsyncClient() as client:
            r = await client.post(f"{self._base}/api/v1/sessions/",
                                  json={"group_id": group_id, "dart_travel_time": dart_travel_time,
                                        "max_players": max_players},
                                  headers=self._headers())
            r.raise_for_status()
            return r.json()
