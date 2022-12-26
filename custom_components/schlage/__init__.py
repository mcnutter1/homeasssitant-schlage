"""Schlage Wifi Home Assistant Integration."""

from typing import Any
from datetime import timedelta

from homeassistant.const import CONF_PASSWORD, CONF_USERNAME, Platform
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.event import async_track_time_interval

from .const import DOMAIN, TOPIC_UPDATE
from .new_api import SchlageAPI


UPDATE_INTERVAL = timedelta(seconds=15)
PLATFORMS: list[Platform] = [Platform.LOCK, Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Schlage from a config entry."""
    api = SchlageAPI(entry.data[CONF_USERNAME], entry.data[CONF_PASSWORD], hass.loop)
    hass.data.setdefault(DOMAIN, {})
    schlage_data = hass.data[DOMAIN][entry.entry_id] = SchlageData(hass, api)

    await schlage_data.async_update()

    async_track_time_interval(hass, schlage_data.async_update, UPDATE_INTERVAL)
    await hass.config_entrires.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload Schlage config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


class SchlageData:
    """Data entry for Schlage."""

    def __init__(self, hass: HomeAssistant, api: SchlageAPI) -> None:
        """Initializer."""
        self.hass = hass
        self.api = api

    async def async_update(self, arg: Any = None) -> None:
        await self.api.update()
        async_dispatcher_send(self.hass, TOPIC_UPDATE)
