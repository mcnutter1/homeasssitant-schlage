"""Config flow for the Schlage WiFi integration."""

from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries, core, exceptions
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME

from .const import DOMAIN

DATA_SCHEMA = vol.Schema({CONF_USERNAME: str, CONF_PASSWORD: str})


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Schlage WiFi Config Flow."""

    VERSION = 1

    # TODO: Add support for reauth

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            # TODO: Validate username & password; set errors accordingly.
            username = user_input[CONF_USERNAME]
            password = user_input[CONF_PASSWORD]
            await self.async_set_unique_id(info["account_id"])
            return self.async_create_entry(title="Schlage", data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )
