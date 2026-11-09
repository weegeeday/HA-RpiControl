from __future__ import annotations

import json
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
        try:
            async with self._session.request(method, url, json=json_data, headers=headers) as resp:
                body = await resp.text()
                if resp.status >= 400:
                    detail = body.strip() or "empty response"
                    raise RuntimeError(f"Pi service error {resp.status}: {detail}")

                if not body.strip():
                    return {}

                try:
                    data = json.loads(body)
                except json.JSONDecodeError as err:
                    raise RuntimeError("Pi service returned invalid JSON") from err

                if not isinstance(data, dict):
                    raise RuntimeError("Pi service returned an unexpected response")
                return data
        except aiohttp.ClientError as err:
            raise RuntimeError(f"Unable to reach Pi service: {err}") from err

    async def health(self) -> dict[str, Any]:
        return await self.request("GET", "/health")

    async def get_fullpageos(self) -> dict[str, Any]:
        return await self.request("GET", "/fullpageos")

    async def set_fullpageos(self, content: str) -> dict[str, Any]:
        return await self.request("PUT", "/fullpageos", json_data={"content": content})

    async def reboot(self) -> dict[str, Any]:
        return await self.request("POST", "/reboot")

    async def cec_on(self) -> dict[str, Any]:
        return await self.request("POST", "/cec/on")

    async def cec_off(self) -> dict[str, Any]:
        return await self.request("POST", "/cec/off")

    async def cec_active_source(self) -> dict[str, Any]:
        return await self.request("POST", "/cec/active_source")

    async def run_ssh(self, payload: dict[str, Any]) -> dict[str, Any]:
        return await self.request("POST", "/ssh", json_data=payload)
