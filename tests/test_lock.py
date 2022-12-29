"""Test schlage lock."""
from unittest.mock import create_autospec, patch

from homeassistant.components.lock import DOMAIN as LOCK_DOMAIN
from homeassistant.const import ATTR_ENTITY_ID, SERVICE_LOCK, SERVICE_UNLOCK
import pyschlage
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.schlage.const import DOMAIN

from .const import MOCK_CONFIG


async def test_lock_services(hass, bypass_auth_init):
    """Test lock services."""
    mock_lock = create_autospec(pyschlage.Lock)
    mock_lock.configure_mock(
        device_id="test",
        name="Vault Door",
        model_name="<model-name>",
        is_locked=False,
        is_jammed=False,
        battery_level=0,
        firmware_version="1.0",
    )

    with patch("pyschlage.Schlage.locks", return_value=[mock_lock]):
        entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG, entry_id="test")
        entry.add_to_hass(hass)

        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
        assert DOMAIN in hass.config_entries.async_domains()

        await hass.services.async_call(
            LOCK_DOMAIN,
            SERVICE_LOCK,
            service_data={ATTR_ENTITY_ID: "lock.vault_door_lock"},
            blocking=True,
        )
        await hass.async_block_till_done()
        mock_lock.lock.assert_called_once_with()

        await hass.services.async_call(
            LOCK_DOMAIN,
            SERVICE_UNLOCK,
            service_data={ATTR_ENTITY_ID: "lock.vault_door_lock"},
            blocking=True,
        )
        await hass.async_block_till_done()
        mock_lock.unlock.assert_called_once_with()
