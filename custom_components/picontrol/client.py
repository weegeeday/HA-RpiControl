from __future__ import annotations

from typing import Any, Optional

import aiohttp


class PiControlClient:
    def __init__(self, base_url: str, token: Optional[str], session: aiohttp.ClientSession) -> None:
        self._base_url = base_url
        self._token = token
        self._session = session

    async def request(
        self, method: str, path: str, *, json_data: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        headers = {}
        if self._token:
            headers["X-API-Token"] = self._token
        url = f"{self._base_url}{path}"
        async with self._session.request(method, url, json=json_data, headers=headers) as resp:
            data = await resp.json(content_type=None)
            if resp.status >= 400:
                raise RuntimeError(f"Pi service error {resp.status}: {data}")
            return data

    async def health(self) -> dict[str, Any]:
        return await self.request("GET", "/health")

    async def get_fullpageos(self) -> dict[str, Any]:
        return await self.request("GET", "/fullpageos")

    async def set_fullpageos(self, content: str) -> dict[str, Any]:
        return await self.request("PUT", "/fullpageos", json_data={"content": content})

    async def reboot(self) -> dict[str, Any]:
        return await self.request("POST", "/reboot")

    async def run_ssh(self, payload: dict[str, Any]) -> dict[str, Any]:
        return await self.request("POST", "/ssh", json_data=payload)
