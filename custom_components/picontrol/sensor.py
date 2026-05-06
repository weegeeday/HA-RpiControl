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
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    client: PiControlClient = hass.data[DOMAIN]["clients"][entry.entry_id]

    async def async_update_data() -> dict:
        try:
            return await client.health()
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

    async_add_entities([PiControlStatusSensor(coordinator, entry)])


class PiControlStatusSensor(CoordinatorEntity):
    _attr_name = "Pi Control Status"
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
        return self.coordinator.data.get("status", "unknown")
