
import logging
from typing import Any, Dict, Optional


from homeassistant.helpers.entity import Entity

from homeassistant.const import CONF_ID, CONF_TYPE, DEVICE_CLASS_BATTERY
from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.util import slugify


from .const import DOMAIN, TOPIC_UPDATE, BATTERY_ICON

_LOGGER = logging.getLogger(__name__)




async def async_setup_entry(hass, config_entry, async_add_entities):
   


    SchlageAccount = hass.data[DOMAIN][config_entry.entry_id]
    devices = SchlageAccount.api.devices
    entities = []
    for device in devices:
           entities.append(SchlageBatteryLifeSensor(device['name'], device['deviceId'], SchlageAccount))
    async_add_entities(entities, True)




class SchlageSensor(Entity):


    def __init__(self, name, device_id, schlage_device):

        self._name = name
        self._id = device_id
        self._schlage_device = schlage_device
        self._state = None
        self._async_unsub_dispatcher_connect = None


    @property
    def should_poll(self) -> bool:
        return False

    @property
    def device_info(self):
        device_info = {
            "identifiers": {(DOMAIN, self._id)},
            "name": self._name,
            "manufacturer": "Schlage",
            "model" : "Encode"
        }
        return device_info

    async def async_update(self) -> None:
        _LOGGER.debug("%s -> self._state: %s", self._name, self._state)
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


class SchlageBatteryLifeSensor(SchlageSensor):
    @property
    def available(self) -> bool:
        return self._schlage_device.api.states[self._id]["available"]

    @property
    def name(self) -> str:
        return "{} Battery Life Sensor".format(self._name)
    @property
    def unique_id(self) -> str:
        return slugify("{}_battery_life_sensor".format(self._id))
    @property
    def state(self) -> str:
        return self._schlage_device.api.states[self._id]["batteryLife"]
    @property
    def native_unit_of_measurement(self):
        return "%"
    @property 
    def device_class(self):
        return DEVICE_CLASS_BATTERY
    @property
    def icon(self):
        return  BATTERY_ICON
