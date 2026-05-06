from __future__ import annotations

from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from .client import PiControlClient
from .const import DATA_CLIENTS, DEFAULT_SCAN_INTERVAL, DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    client: PiControlClient = hass.data[DOMAIN][DATA_CLIENTS][entry.entry_id]

    async def async_update_data() -> dict:
        try:
            health = await client.health()
            fullpageos = {"content": ""}
            try:
                fullpageos = await client.get_fullpageos()
            except Exception:  # noqa: BLE001
                # Ignore if we can't read the file (e.g. absent or permissions)
                pass

            return {
                "health": health,
                "fullpageos": fullpageos.get("content", ""),
            }
        except Exception as exc:  # noqa: BLE001
            raise UpdateFailed(str(exc)) from exc

    coordinator = DataUpdateCoordinator(
        hass,
        logger=None,
        name=f"{DOMAIN}_{entry.entry_id}",
        update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        update_method=async_update_data,
    )
    await coordinator.async_config_entry_first_refresh()

    async_add_entities(
        [
            PiControlStatusSensor(coordinator, entry),
            PiControlFullpageosSensor(coordinator, entry),
        ]
    )


class PiControlStatusSensor(CoordinatorEntity):
    _attr_has_entity_name = True
    _attr_name = "Status"
    _attr_icon = "mdi:raspberry-pi"

    def __init__(self, coordinator: DataUpdateCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_status"

    @property
    def device_info(self) -> DeviceInfo:
        host = self._entry.data.get("host")
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name=f"Pi Control ({host})",
            manufacturer="Pi Control",
            entry_type=DeviceEntryType.SERVICE,
        )

    @property
    def native_value(self) -> str:
        return self.coordinator.data.get("health", {}).get("status", "unknown")


class PiControlFullpageosSensor(CoordinatorEntity):
    _attr_has_entity_name = True
    _attr_name = "FullPageOS Config"
    _attr_icon = "mdi:file-document-outline"

    def __init__(self, coordinator: DataUpdateCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_fullpageos"

    @property
    def device_info(self) -> DeviceInfo:
        host = self._entry.data.get("host")
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name=f"Pi Control ({host})",
            manufacturer="Pi Control",
            entry_type=DeviceEntryType.SERVICE,
        )

    @property
    def native_value(self) -> str:
        # State limited to 255 chars, so we just say 'Present' or similar
        content = self.coordinator.data.get("fullpageos", "")
        return "Loaded" if content else "Empty/Error"

    @property
    def extra_state_attributes(self) -> dict:
        return {"content": self.coordinator.data.get("fullpageos", "")}
