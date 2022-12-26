"""Schlage Wifi Home Assistant Integration."""

from datetime import timedelta
from pyschlage import Auth, Schlage

from homeassistant.const import CONF_PASSWORD, CONF_USERNAME, Platform
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN, LOGGER
from .new_api import SchlageAPI

UPDATE_INTERVAL = timedelta(seconds=15)
PLATFORMS: list[Platform] = [Platform.LOCK, Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Schlage from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    auth = await hass.async_add_executor_job(
        Auth(entry.data[CONF_USERNAME], entry.data[CONF_PASSWORD])
    )
    api = Schlage(auth)

    async def async_update_data():
        locks = await hass.async_add_executor_job(api.locks)
        return {lock.device_id: lock for lock in locks}

    coordinator = DataUpdateCoordinator(
        hass,
        LOGGER,
        name="schlage",
        update_method=async_update_data,
        update_interval=UPDATE_INTERVAL,
    )
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = {
        DATA_API: api,
        DATA_COORDINATOR: coordinator,
    }
    await hass.config_entrires.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload Schlage config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
