from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_SSL, CONF_TOKEN
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .client import PiControlClient
from .const import CONF_ENTRY_ID, DATA_CLIENTS, DOMAIN, PLATFORMS

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
    hass.data.setdefault(DOMAIN, {DATA_CLIENTS: {}, "services": False})
    conf = config.get(DOMAIN)
    if conf is None:
        return True

    entry_id = "yaml"
    client = _create_client(hass, conf)
    hass.data[DOMAIN][DATA_CLIENTS][entry_id] = client
    _register_services(hass)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {DATA_CLIENTS: {}, "services": False})
    client = _create_client(hass, entry.data)
    hass.data[DOMAIN][DATA_CLIENTS][entry.entry_id] = client
    _register_services(hass)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN][DATA_CLIENTS].pop(entry.entry_id, None)
    return unload_ok


def _create_client(hass: HomeAssistant, conf: dict[str, Any]) -> PiControlClient:
    scheme = "https" if conf.get(CONF_SSL) else "http"
    base_url = f"{scheme}://{conf[CONF_HOST]}:{conf[CONF_PORT]}"
    token = conf.get(CONF_TOKEN) or None
    session = async_get_clientsession(hass)
    return PiControlClient(base_url, token, session)


def _get_client_for_call(hass: HomeAssistant, call: ServiceCall) -> PiControlClient:
    clients = hass.data[DOMAIN][DATA_CLIENTS]
    entry_id = call.data.get(CONF_ENTRY_ID)
    if entry_id and entry_id in clients:
        return clients[entry_id]
    if clients:
        return next(iter(clients.values()))
    raise RuntimeError("No Pi Control client configured")


def _register_services(hass: HomeAssistant) -> None:
    if hass.data[DOMAIN]["services"]:
        return

    async def async_reboot(call: ServiceCall) -> None:
        client = _get_client_for_call(hass, call)
        await client.reboot()

    async def async_get_fullpageos(call: ServiceCall) -> None:
        client = _get_client_for_call(hass, call)
        result = await client.get_fullpageos()
        hass.states.async_set(f"{DOMAIN}.fullpageos", result.get("content", ""))

    async def async_set_fullpageos(call: ServiceCall) -> None:
        client = _get_client_for_call(hass, call)
        content = call.data["content"]
        await client.set_fullpageos(content)

    async def async_run_ssh(call: ServiceCall) -> None:
        client = _get_client_for_call(hass, call)
        payload = {
            "host": call.data["host"],
            "command": call.data["command"],
            "port": call.data.get("port", 22),
        }
        if "user" in call.data:
            payload["user"] = call.data["user"]
        if "identity_file" in call.data:
            payload["identity_file"] = call.data["identity_file"]
        result = await client.run_ssh(payload)
        hass.states.async_set(f"{DOMAIN}.ssh_result", result)

    hass.services.async_register(DOMAIN, SERVICE_REBOOT, async_reboot)
    hass.services.async_register(DOMAIN, SERVICE_GET_FULLPAGEOS, async_get_fullpageos)
    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_FULLPAGEOS,
        async_set_fullpageos,
        schema=vol.Schema({vol.Required("content"): cv.string, vol.Optional(CONF_ENTRY_ID): cv.string}),
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
                vol.Optional(CONF_ENTRY_ID): cv.string,
            }
        ),
    )

    hass.data[DOMAIN]["services"] = True
