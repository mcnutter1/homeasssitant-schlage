"""Support for Schlage WiFi locks."""

from pyschlage.code import AccessCode
from pyschlage.lock import Lock
from pyschlage.log import LockLog
from pyschlage.user import User

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
        [
            SchlageLock(coordinator, device_id)
            for device_id in coordinator.data.locks.keys()
        ]
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
        return self.coordinator.data.locks[self.device_id].lock

    @property
    def _access_codes(self) -> dict[str, AccessCode]:
        return self.coordinator.data.locks[self.device_id].access_codes

    @property
    def _logs(self) -> list[LockLog]:
        return self.coordinator.data.locks[self.device_id].logs

    @property
    def _users(self) -> dict[str, User]:
        return self.coordinator.data.users

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
        self._attr_changed_by = self._get_changed_by()

    def _get_changed_by(self):
        if not self._logs:
            return None
        want_msg_pfx = "Locked by " if self._lock.is_locked else "Unlocked by "
        newest_log = max(self._logs, key=lambda log: log.created_at)
        if not newest_log.message.startswith(want_msg_pfx):
            return None

        message = newest_log.message[len(want_msg_pfx) :]
        match message:
            case "keypad":
                if code := self._access_codes.get(newest_log.access_code_id, None):
                    return f"{message} - {code.name}"
            case "mobile device":
                if user := self._users.get(newest_log.accessor_id, None):
                    return f"{message} - {user.name}"

        return message

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
