from __future__ import annotations

import asyncio
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant.const import CONF_HOST, CONF_PORT, CONF_SSL, CONF_TOKEN
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN

SERVICE_REBOOT = "reboot"
SERVICE_GET_FULLPAGEOS = "get_fullpageos"
SERVICE_SET_FULLPAGEOS = "set_fullpageos"
SERVICE_RUN_SSH = "run_ssh"

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_HOST): cv.string,
                vol.Optional(CONF_PORT, default=8129): cv.port,
                vol.Optional(CONF_SSL, default=False): cv.boolean,
                vol.Optional(CONF_TOKEN, default=""): cv.string,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass: HomeAssistant, config: dict[str, Any]) -> bool:
    conf = config.get(DOMAIN)
    if conf is None:
        return True

    scheme = "https" if conf[CONF_SSL] else "http"
    base_url = f"{scheme}://{conf[CONF_HOST]}:{conf[CONF_PORT]}"
    token = conf.get(CONF_TOKEN) or None

    async def request(
        method: str, path: str, *, json_data: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        headers = {}
        if token:
            headers["X-API-Token"] = token
        url = f"{base_url}{path}"
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.request(method, url, json=json_data, headers=headers) as resp:
                data = await resp.json(content_type=None)
                if resp.status >= 400:
                    raise RuntimeError(f"Pi service error {resp.status}: {data}")
                return data

    async def async_reboot(_: ServiceCall) -> None:
        await request("POST", "/reboot")

    async def async_get_fullpageos(call: ServiceCall) -> None:
        result = await request("GET", "/fullpageos")
        hass.states.async_set(
            f"{DOMAIN}.fullpageos", result.get("content", "")
        )

    async def async_set_fullpageos(call: ServiceCall) -> None:
        content = call.data["content"]
        await request("PUT", "/fullpageos", json_data={"content": content})

    async def async_run_ssh(call: ServiceCall) -> None:
        payload = {
            "host": call.data["host"],
            "command": call.data["command"],
            "port": call.data.get("port", 22),
        }
        if "user" in call.data:
            payload["user"] = call.data["user"]
        if "identity_file" in call.data:
            payload["identity_file"] = call.data["identity_file"]
        result = await request("POST", "/ssh", json_data=payload)
        hass.states.async_set(f"{DOMAIN}.ssh_result", result)

    hass.services.async_register(DOMAIN, SERVICE_REBOOT, async_reboot)
    hass.services.async_register(DOMAIN, SERVICE_GET_FULLPAGEOS, async_get_fullpageos)
    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_FULLPAGEOS,
        async_set_fullpageos,
        schema=vol.Schema({vol.Required("content"): cv.string}),
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_RUN_SSH,
        async_run_ssh,
        schema=vol.Schema(
            {
                vol.Required("host"): cv.string,
                vol.Required("command"): cv.string,
                vol.Optional("user"): cv.string,
                vol.Optional("port"): cv.port,
                vol.Optional("identity_file"): cv.string,
            }
        ),
    )

    return True
