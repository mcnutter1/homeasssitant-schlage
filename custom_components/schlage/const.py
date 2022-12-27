"""Constants for the Schlage WiFi integration."""

import logging

from homeassistant.const import Platform

LOGGER = logging.getLogger(__package__)

DOMAIN = "schlage"
MANUFACTURER = "Schlage"
PLATFORMS: list[Platform] = [Platform.LOCK, Platform.SENSOR]
