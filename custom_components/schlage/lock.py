"""Support for Schlage WiFi locks."""

from typing import Any, Dict

from homeassistant.components.lock import LockEntity
from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.util import slugify


from .const import DOMAIN, LOGGER, TOPIC_UPDATE


async def async_setup_entry(hass, config_entry, async_add_entities):
    data = hass.data[DOMAIN][config_entry.entry_id]
    entities = []
    for device in data.api.devices:
        entities.append(SchlageLock(device["name"], device["deviceId"], data.api))
    async_add_entities(entities, True)


class SchlageLock(LockEntity):

    def __init__(self, name, device_id, api):
        self._name = name
        self._id = device_id
        self._api = api
        self._state: Dict[str, Any] = {}
        self._async_unsub_dispatcher_connect = None

    @property
    def should_poll(self) -> bool:
        """Return true."""
        return False

    @property
    def available(self) -> bool:
        """Return true if entity is available."""
        return self._api.states[self._id]["available"]

    @property
    def name(self) -> str:
        """Return the name of the device if any."""
        return "{} Lock".format(self._name)

    @property
    def unique_id(self) -> str:
        """Return an unique ID."""
        return slugify("{}_lock".format(self._id))

    @property
    def is_locked(self) -> bool:
        """Return true if the lock is locked."""
        return self._api.states[self._id]["lockState"]

    async def async_lock(self, **kwargs):
        """Lock the device."""
        lockResult = await self._api.lock(self._id)

    async def async_unlock(self, **kwargs):
        """Unlock the device."""
        lockResult = await self._api.unlock(self._id)

    @property
    def device_info(self):
        device_info = {
            "identifiers": {(DOMAIN, self._id)},
            "name": self._name,
            "manufacturer": "Schlage",
            "model": "Encode",
        }
        return device_info

    async def async_update(self) -> None:
        """Get the latest data and update the state."""
        LOGGER.debug("%s -> self._state: %s", self._name, self._state)

    async def async_added_to_hass(self) -> None:
        """Register callbacks."""

        @callback
        def update() -> None:
            """Update the state."""
            self.async_schedule_update_ha_state(True)

        self._async_unsub_dispatcher_connect = async_dispatcher_connect(
            self.hass, TOPIC_UPDATE, update
        )

    async def async_will_remove_from_hass(self) -> None:
        """Disconnect dispatcher listener when removed."""
        if self._async_unsub_dispatcher_connect:
            self._async_unsub_dispatcher_connect()
