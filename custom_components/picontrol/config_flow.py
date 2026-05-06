from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_SSL, CONF_TOKEN
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN


class PiControlConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                await self._validate(user_input)
                return self.async_create_entry(title=user_input[CONF_HOST], data=user_input)
            except Exception:  # noqa: BLE001
                errors["base"] = "cannot_connect"

        schema = vol.Schema(
            {
                vol.Required(CONF_HOST): str,
                vol.Optional(CONF_PORT, default=8129): int,
                vol.Optional(CONF_SSL, default=False): bool,
                vol.Optional(CONF_TOKEN, default=""): str,
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def _validate(self, data: dict[str, Any]) -> None:
        scheme = "https" if data.get(CONF_SSL) else "http"
        base_url = f"{scheme}://{data[CONF_HOST]}:{data[CONF_PORT]}"
        headers = {}
        if data.get(CONF_TOKEN):
            headers["X-API-Token"] = data[CONF_TOKEN]
        session = async_get_clientsession(self.hass)
        async with session.get(f"{base_url}/health", headers=headers) as resp:
            if resp.status >= 400:
                raise ConnectionError
