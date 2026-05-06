from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .client import PiControlClient
from .const import DATA_CLIENTS, DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    client: PiControlClient = hass.data[DOMAIN][DATA_CLIENTS][entry.entry_id]
    async_add_entities(
        [
            PiControlRebootButton(client, entry),
            PiControlCecOnButton(client, entry),
            PiControlCecOffButton(client, entry),
            PiControlCecActiveSourceButton(client, entry),
        ]
    )


class PiControlRebootButton(ButtonEntity):
    _attr_has_entity_name = True
    _attr_name = "Reboot"
    _attr_icon = "mdi:restart"

    def __init__(self, client: PiControlClient, entry: ConfigEntry) -> None:
        self._client = client
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_reboot"

    @property
    def device_info(self) -> DeviceInfo:
        host = self._entry.data.get("host")
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name=f"Pi Control ({host})",
            manufacturer="Pi Control",
            entry_type=DeviceEntryType.SERVICE,
        )

    async def async_press(self) -> None:
        """Handle the button press."""
        await self._client.reboot()


class PiControlCecOnButton(ButtonEntity):
    _attr_has_entity_name = True
    _attr_name = "Display On (CEC)"
    _attr_icon = "mdi:television"

    def __init__(self, client: PiControlClient, entry: ConfigEntry) -> None:
        self._client = client
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_cec_on"

    @property
    def device_info(self) -> DeviceInfo:
        host = self._entry.data.get("host")
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name=f"Pi Control ({host})",
            manufacturer="Pi Control",
            entry_type=DeviceEntryType.SERVICE,
        )

    async def async_press(self) -> None:
        """Handle the button press."""
        await self._client.cec_on()


class PiControlCecOffButton(ButtonEntity):
    _attr_has_entity_name = True
    _attr_name = "Display Off (CEC)"
    _attr_icon = "mdi:television-off"

    def __init__(self, client: PiControlClient, entry: ConfigEntry) -> None:
        self._client = client
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_cec_off"

    @property
    def device_info(self) -> DeviceInfo:
        host = self._entry.data.get("host")
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name=f"Pi Control ({host})",
            manufacturer="Pi Control",
            entry_type=DeviceEntryType.SERVICE,
        )

    async def async_press(self) -> None:
        """Handle the button press."""
        await self._client.cec_off()


class PiControlCecActiveSourceButton(ButtonEntity):
    _attr_has_entity_name = True
    _attr_name = "Switch Input to Pi (CEC)"
    _attr_icon = "mdi:import"

    def __init__(self, client: PiControlClient, entry: ConfigEntry) -> None:
        self._client = client
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_cec_active_source"

    @property
    def device_info(self) -> DeviceInfo:
        host = self._entry.data.get("host")
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name=f"Pi Control ({host})",
            manufacturer="Pi Control",
            entry_type=DeviceEntryType.SERVICE,
        )

    async def async_press(self) -> None:
        """Handle the button press."""
        await self._client.cec_active_source()

