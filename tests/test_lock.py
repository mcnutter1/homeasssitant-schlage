"""Test schlage lock."""
from unittest.mock import call, create_autospec, patch

from homeassistant.components.lock import (
    DOMAIN as LOCK_DOMAIN,
    STATE_JAMMED,
    STATE_LOCKING,
    STATE_UNLOCKING,
)
from homeassistant.const import ATTR_ENTITY_ID, SERVICE_LOCK, SERVICE_UNLOCK
import pyschlage
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.schlage import async_setup_entry
from custom_components.schlage.const import DOMAIN

from .const import MOCK_CONFIG


async def test_lock_services(hass, bypass_auth_init):
    """Test lock services."""
    mock_lock = create_autospec(
        pyschlage.Lock,
        device_id="test",
        name="My Lock",
        model_name="Test Lock",
        is_locked=False,
        is_jammed=False,
        battery_level=0,
        firmware_version="1.0",
    )
    with patch("pyschlage.Schlage.locks", return_value=[mock_lock]) as locks_fn:
        entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG, entry_id="test")
        #entry.add_to_hass(hass)
        assert await async_setup_entry(hass, entry)
        await hass.async_block_till_done()

        await hass.services.async_call(
            LOCK_DOMAIN,
            SERVICE_LOCK,
            service_data={ATTR_ENTITY_ID: "lock.test_lock_lock"},
            blocking=True,
        )
        mock_lock.lock.assert_called_with()

        await hass.services.async_call(
            LOCK_DOMAIN,
            SERVICE_LOCK,
            service_data={ATTR_ENTITY_ID: "lock.test_lock_lock"},
            blocking=True,
        )
        mock_lock.unlock.assert_called_with()
