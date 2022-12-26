"""Sensors for Schlage WiFi locks."""

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.core import callback
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.util import slugify

from .const import DOMAIN, LOGGER, TOPIC_UPDATE


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors based on a config entry."""
    data = hass.data[DOMAIN][config_entry.entry_id]
    entities = []
    for device in data.api.devices:
        entities.append(BatterySensor(device["name"], device["deviceId"], data.api))
    async_add_entities(entities, True)


class BatterySensor(SensorEntity):

    _attr_should_poll = False
    _attr_device_class = SensorDeviceClass.BATTERY
    _attr_icon = "mdi:battery"

    def __init__(self, name, device_id, api):
        self._name = name
        self._id = device_id
        self._api = api
        self._state = None
        self._async_unsub_dispatcher_connect = None

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._id)},
            "name": self._name,
            "manufacturer": "Schlage",
            "model": "Encode",
        }

    @property
    def available(self) -> bool:
        return self._api.states[self._id]["available"]

    @property
    def name(self) -> str:
        return f"{self._name} Battery"

    @property
    def unique_id(self) -> str:
        return slugify(f"{self._id}_battery_life_sensor")

    @property
    def state(self) -> str:
        return self._api.states[self._id]["batteryLife"]

    @property
    def native_unit_of_measurement(self):
        return "%"

    async def async_update(self) -> None:
        LOGGER.debug("%s -> self._state: %s", self._name, self._state)

    async def async_added_to_hass(self) -> None:
        @callback
        def update() -> None:
            self.async_schedule_update_ha_state(True)

        self._async_unsub_dispatcher_connect = async_dispatcher_connect(
            self.hass, TOPIC_UPDATE, update
        )

    async def async_will_remove_from_hass(self) -> None:
        if self._async_unsub_dispatcher_connect:
            self._async_unsub_dispatcher_connect()
