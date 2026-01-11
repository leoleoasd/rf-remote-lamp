"""
Custom integration for RF Remote Lamp control.

This integration allows controlling RF lamps through a remote entity,
tracking assumed state internally since RF remotes are one-way.
"""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, PLATFORMS

_LOGGER = logging.getLogger(__name__)

# Track entries being reloaded to prevent infinite loops
_reloading: set[str] = set()


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up RF Remote Lamp from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register update listener for options changes
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    # Prevent infinite reload loop
    if entry.entry_id in _reloading:
        return
    
    _reloading.add(entry.entry_id)
    try:
        await hass.config_entries.async_reload(entry.entry_id)
    finally:
        _reloading.discard(entry.entry_id)
