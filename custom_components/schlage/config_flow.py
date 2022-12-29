"""Config flow for the Schlage WiFi integration."""

from __future__ import annotations

from typing import Any

from pyschlage import Auth
from pyschlage.exceptions import NotAuthorizedError
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, LOGGER

DATA_SCHEMA = vol.Schema(
    {vol.Required(CONF_USERNAME): str, vol.Required(CONF_PASSWORD): str}
)


class ConfigFlow(ConfigFlow, domain=DOMAIN):
    """Schlage WiFi Config Flow."""

    VERSION = 1

    # TODO: Add support for reauth

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            username = user_input[CONF_USERNAME]
            password = user_input[CONF_PASSWORD]
            try:
                auth = await self.hass.async_add_executor_job(Auth, username, password)
                await self.hass.async_add_executor_job(auth.authenticate)
            except NotAuthorizedError:
                LOGGER.exception("Authentication error")
                errors["base"] = "invalid_auth"
            except Exception:
                LOGGER.exception("Unknown error")
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(username.lower())
                return self.async_create_entry(title=username, data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )
