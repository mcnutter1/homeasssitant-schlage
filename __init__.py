
import logging
from typing import Any, Dict, List
from datetime import timedelta
from . new_api import (SchlageAPI)
import asyncio
import voluptuous as vol

from homeassistant.const import (
    CONF_ID,
    CONF_TYPE,
    CONF_PASSWORD,
    CONF_USERNAME,
)

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.config_entries import SOURCE_IMPORT, ConfigEntry
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.event import async_track_time_interval

from .const import (
    DOMAIN,
    DATA_SCHLAGE_API,
    TOPIC_UPDATE
)

_LOGGER = logging.getLogger(__name__)


CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_USERNAME): cv.string,
                vol.Required(CONF_PASSWORD): cv.string,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)

DEFAULT_UPDATE_RATE = timedelta(seconds=15)
PLATFORMS = ['lock', 'sensor']

async def async_setup(hass, config) -> bool:
    conf = config.get(DOMAIN)
    hass.data.setdefault(DOMAIN, {})


    if not conf:
        return True

    
 
    hass.async_create_task(
        hass.config_entries.flow.async_init(
            DOMAIN, context={"source": SOURCE_IMPORT}, data=conf
        )
    )
    return True
   
    schlageAPIObject = SchlageAPI(
            conf[CONF_USERNAME],
            conf[CONF_PASSWORD],
            hass.loop
        )


    
   

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):

    conf = entry.data
    username = conf[CONF_USERNAME]
    password = conf[CONF_PASSWORD]
    scan_interval = DEFAULT_UPDATE_RATE

    API =  SchlageAPI(conf[CONF_USERNAME],conf[CONF_PASSWORD],hass.loop)
    hass.data.setdefault(DOMAIN, {})
    hub = hass.data[DOMAIN][entry.entry_id] = SchlageDevice(hass, API)
    
    await hub.async_update()

    async_track_time_interval(hass, hub.async_update, scan_interval)


    for component in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, component)
        )
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, component)
                for component in PLATFORMS
            ]
        )
    )
    unload_ok = True
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok

class SchlageDevice:

    def __init__(self, hass, api) -> None:
        """Initialize the Sure Petcare object."""
        self.hass = hass
        self.api = api


    async def async_update(self, arg: Any = None) -> None:

        #await self.gdo.update()
        await self.api.update()
        devices = self.api.devices
        for device in devices:
           print("Lock: {}, ID: {}, State: {}".format(device['name'],device['deviceId'], device['attributes']['lockState']))
        async_dispatcher_send(self.hass, TOPIC_UPDATE)
