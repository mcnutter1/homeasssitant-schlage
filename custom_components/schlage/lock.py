"""Support for Schlage WiFi locks."""

from pyschlage import Lock

from homeassistant.components.lock import LockEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import callback, HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import DOMAIN, MANUFACTURER


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Schlage WiFi locks based on a config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities(
        [SchlageLock(coordinator, device_id) for device_id in coordinator.data.keys()]
    )


class SchlageLock(CoordinatorEntity, LockEntity):
    """Schlage lock entity."""

    def __init__(self, coordinator: DataUpdateCoordinator, device_id: str) -> None:
        """Initializer."""
        super().__init__(coordinator)
        self.device_id: str = device_id
        self._attr_unique_id = device_id
        self._update_attrs()

    @property
    def _lock(self) -> Lock:
        return self.coordinator.data[self.device_id]

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._update_attrs()
        self.async_write_ha_state()

    def _update_attrs(self) -> None:
        self._attr_name = f"{self._lock.name} Lock"
        self._attr_is_locked = self._lock.is_locked
        self._attr_is_jammed = self._lock.is_jammed
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self.device_id)},
            name=self._attr_name,
            manufacturer=MANUFACTURER,
            model=self._lock.model_name,
            sw_version=self._lock.firmware_version,
        )

    async def async_lock(self, **kwargs):
        """Lock the device."""
        await self.hass.async_add_executor_job(self._lock.lock)
        self._update_attrs()
        self.async_write_ha_state()

    async def async_unlock(self, **kwargs):
        """Unlock the device."""
        await self.hass.async_add_executor_job(self._lock.unlock)
        self._update_attrs()
        self.async_write_ha_state()
