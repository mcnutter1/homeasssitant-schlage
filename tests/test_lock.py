"""Test schlage lock."""
from datetime import datetime
from unittest.mock import create_autospec, patch

from homeassistant.components.lock import DOMAIN as LOCK_DOMAIN
from homeassistant.const import ATTR_ENTITY_ID, SERVICE_LOCK, SERVICE_UNLOCK
from pyschlage.code import AccessCode
from pyschlage.lock import Lock
from pyschlage.log import LockLog
from pyschlage.user import User
import pytest
from pytest import fixture
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.schlage.const import DOMAIN

from .const import MOCK_CONFIG


def make_mock(cls, **kwargs):
    """Wrapper around create_autospec & configure_mock.

    Useful when you need to set a |name| attribute in the mock.
    """
    code = create_autospec(cls)
    code.configure_mock(**kwargs)
    return code


@fixture
def mock_lock(mock_access_code):
    mock_lock = make_mock(
        Lock,
        device_id="test",
        name="Vault Door",
        model_name="<model-name>",
        is_locked=False,
        is_jammed=False,
        battery_level=0,
        firmware_version="1.0",
    )
    mock_lock.access_codes.return_value = [mock_access_code]
    return mock_lock


@fixture
def mock_access_code():
    yield make_mock(
        AccessCode,
        access_code_id="__access-code-id__",
        name="SECRET CODE",
    )


@fixture
def mock_user():
    yield make_mock(
        User,
        name="robot",
        email="robot@cyb.org",
        user_id="__user-id__",
    )


class TestChangedBy:
    """Test parsing of logs for the changed_by attribute."""

    async def test_thumbturn_unlock(self, hass, bypass_auth_init, mock_lock):
        mock_lock.logs.return_value = [
            create_autospec(
                LockLog,
                created_at=datetime(2023, 1, 1, 0, 0, 0),
                message="Locked by keypad",
            ),
            create_autospec(
                LockLog,
                created_at=datetime(2023, 1, 1, 1, 0, 0),
                message="Unlocked by thumbturn",
            ),
        ]
        mock_locks = patch("pyschlage.Schlage.locks", return_value=[mock_lock])
        mock_users = patch("pyschlage.Schlage.users", return_value=[])
        with mock_locks, mock_users:
            entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG, entry_id="test")
            entry.add_to_hass(hass)

            await hass.config_entries.async_setup(entry.entry_id)
            await hass.async_block_till_done()
            assert DOMAIN in hass.config_entries.async_domains()

            lock_device = hass.states.get("lock.vault_door_lock")
            assert lock_device is not None
            assert lock_device.attributes.get("changed_by") == "thumbturn"

    async def test_keypad_unlock(self, hass, bypass_auth_init, mock_lock):
        mock_lock.logs.return_value = [
            create_autospec(
                LockLog,
                created_at=datetime(2023, 1, 1, 0, 0, 0),
                message="Locked by keypad",
            ),
            create_autospec(
                LockLog,
                created_at=datetime(2023, 1, 1, 1, 0, 0),
                message="Unlocked by keypad",
                access_code_id="__access-code-id__",
            ),
        ]
        mock_locks = patch("pyschlage.Schlage.locks", return_value=[mock_lock])
        mock_users = patch("pyschlage.Schlage.users", return_value=[])
        with mock_locks, mock_users:
            entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG, entry_id="test")
            entry.add_to_hass(hass)

            await hass.config_entries.async_setup(entry.entry_id)
            await hass.async_block_till_done()
            assert DOMAIN in hass.config_entries.async_domains()

            lock_device = hass.states.get("lock.vault_door_lock")
            assert lock_device is not None
            assert lock_device.attributes.get("changed_by") == "keypad - SECRET CODE"

    async def test_mobile_device_unlock(
        self, hass, bypass_auth_init, mock_lock, mock_user
    ):
        mock_lock.logs.return_value = [
            create_autospec(
                LockLog,
                created_at=datetime(2023, 1, 1, 0, 0, 0),
                message="Locked by keypad",
            ),
            create_autospec(
                LockLog,
                created_at=datetime(2023, 1, 1, 1, 0, 0),
                message="Unlocked by mobile device",
                accessor_id="__user-id__",
            ),
        ]
        mock_locks = patch("pyschlage.Schlage.locks", return_value=[mock_lock])
        mock_users = patch("pyschlage.Schlage.users", return_value=[mock_user])
        with mock_locks, mock_users:
            entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG, entry_id="test")
            entry.add_to_hass(hass)

            await hass.config_entries.async_setup(entry.entry_id)
            await hass.async_block_till_done()
            assert DOMAIN in hass.config_entries.async_domains()

            lock_device = hass.states.get("lock.vault_door_lock")
            assert lock_device is not None
            assert lock_device.attributes.get("changed_by") == "mobile device - robot"


async def test_lock_services(hass, bypass_auth_init, mock_lock):
    """Test lock services."""
    mock_lock.logs.return_value = []
    mock_locks = patch("pyschlage.Schlage.locks", return_value=[mock_lock])
    mock_users = patch("pyschlage.Schlage.users", return_value=[])
    with mock_locks, mock_users:
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
