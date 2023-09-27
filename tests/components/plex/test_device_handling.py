"""Tests for handling the device registry."""
from homeassistant.components.plex.const import DOMAIN
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr, entity_registry as er


async def test_cleanup_orphaned_devices(
    hass: HomeAssistant, entry, setup_plex_server
) -> None:
    """Test cleaning up orphaned devices on startup."""
    test_device_id = {(DOMAIN, "temporary_device_123")}

    device_registry = dr.async_get(hass)
    entity_registry = er.async_get(hass)
    entry.add_to_hass(hass)

    test_device = device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers=test_device_id,
    )
    assert test_device is not None

    test_entity = entity_registry.async_get_or_create(
        Platform.MEDIA_PLAYER, DOMAIN, "entity_unique_id_123", device_id=test_device.id
    )
    assert test_entity is not None

    # Ensure device is not removed with an entity
    await setup_plex_server()
    device = device_registry.async_get_device(identifiers=test_device_id)
    assert device is not None

    await hass.config_entries.async_unload(entry.entry_id)

    # Ensure device is removed without an entity
    entity_registry.async_remove(test_entity.entity_id)
    await setup_plex_server()
    device = device_registry.async_get_device(identifiers=test_device_id)
    assert device is None
