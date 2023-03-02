"""Sensors for Schlage WiFi locks."""

from pyschlage import Lock

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE
from homeassistant.core import callback, HomeAssistant
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
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
    """Set up sensors based on a config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities(
        [
            BatterySensor(coordinator, device_id)
            for device_id in coordinator.data.locks.keys()
        ]
    )


class BatterySensor(CoordinatorEntity, SensorEntity):
    """Schlage Battery Sensor entity."""

    _attr_device_class = SensorDeviceClass.BATTERY
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_native_unit_of_measurement = PERCENTAGE

    def __init__(self, coordinator: DataUpdateCoordinator, device_id: str) -> None:
        super().__init__(coordinator)
        self.device_id = device_id
        self._attr_unique_id = device_id
        self._update_attrs()

    @property
    def _lock(self) -> Lock:
        return self.coordinator.data.locks[self.device_id].lock

    def _update_attrs(self):
        self._attr_native_value = self._lock.battery_level
        self._attr_name = f"{self._lock.name} Battery"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._lock.device_id)},
            name=f"{self._lock.name} Lock",
            manufacturer=MANUFACTURER,
            model=self._lock.model_name,
            sw_version=self._lock.firmware_version,
        )

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._update_attrs()
        self.async_write_ha_state()
