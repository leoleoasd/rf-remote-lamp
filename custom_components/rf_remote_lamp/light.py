"""Light platform for RF Remote Lamp integration."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_COLOR_TEMP_KELVIN,
    ColorMode,
    LightEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from .const import (
    CCT_MAX_KELVIN,
    CCT_MIN_KELVIN,
    CMD_BRIGHTNESS_DOWN,
    CMD_BRIGHTNESS_UP,
    CMD_CCT_TOGGLE,
    CMD_TOGGLE,
    CONF_BRIGHTNESS_LEVELS,
    CONF_CCT_LEVELS,
    CONF_DEVICE_NAME,
    CONF_LAMP_NAME,
    CONF_REMOTE_ENTITY,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up RF Remote Lamp light from a config entry."""
    config = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        [
            RfRemoteLampLight(
                entry=entry,
                lamp_name=config[CONF_LAMP_NAME],
                remote_entity=config[CONF_REMOTE_ENTITY],
                device_name=config[CONF_DEVICE_NAME],
                brightness_levels=config.get(CONF_BRIGHTNESS_LEVELS),
                cct_levels=config.get(CONF_CCT_LEVELS),
            )
        ]
    )


class RfRemoteLampLight(LightEntity, RestoreEntity):
    """Representation of an RF Remote Lamp."""

    _attr_has_entity_name = True

    def __init__(
        self,
        entry: ConfigEntry,
        lamp_name: str,
        remote_entity: str,
        device_name: str,
        brightness_levels: int | None = None,
        cct_levels: int | None = None,
    ) -> None:
        """Initialize the RF Remote Lamp."""
        self._entry = entry
        self._lamp_name = lamp_name
        self._remote_entity = remote_entity
        self._device_name = device_name
        self._brightness_levels = int(brightness_levels) if brightness_levels else None
        self._cct_levels = int(cct_levels) if cct_levels else None
        self._is_on = False
        
        # Current brightness level (1 to brightness_levels), assume full brightness initially
        self._brightness_level = self._brightness_levels if self._brightness_levels else None
        # Current CCT level (1 to cct_levels), assume level 1 initially (warm)
        self._cct_level = 1 if self._cct_levels else None

        # Entity attributes
        self._attr_unique_id = f"{remote_entity}_{device_name}"
        self._attr_name = lamp_name

        # Set color mode based on features
        self._attr_supported_color_modes = set()
        
        if self._brightness_levels and self._cct_levels:
            self._attr_supported_color_modes.add(ColorMode.COLOR_TEMP)
            self._attr_color_mode = ColorMode.COLOR_TEMP
        elif self._brightness_levels:
            self._attr_supported_color_modes.add(ColorMode.BRIGHTNESS)
            self._attr_color_mode = ColorMode.BRIGHTNESS
        elif self._cct_levels:
            self._attr_supported_color_modes.add(ColorMode.COLOR_TEMP)
            self._attr_color_mode = ColorMode.COLOR_TEMP
        else:
            self._attr_supported_color_modes.add(ColorMode.ONOFF)
            self._attr_color_mode = ColorMode.ONOFF

        # Set color temp range if CCT is supported
        if self._cct_levels:
            self._attr_min_color_temp_kelvin = CCT_MIN_KELVIN
            self._attr_max_color_temp_kelvin = CCT_MAX_KELVIN

    @property
    def is_on(self) -> bool:
        """Return true if light is on."""
        return self._is_on

    @property
    def brightness(self) -> int | None:
        """Return the brightness of the light."""
        if not self._brightness_levels or not self._is_on:
            return None
        # Convert level (1-max) to HA brightness (1-255)
        return int((self._brightness_level / self._brightness_levels) * 255)

    @property
    def color_temp_kelvin(self) -> int | None:
        """Return the color temperature in Kelvin."""
        if not self._cct_levels or not self._is_on:
            return None
        # Convert level (1-max) to Kelvin
        # Level 1 = warm (CCT_MIN_KELVIN), Level max = cool (CCT_MAX_KELVIN)
        kelvin_range = CCT_MAX_KELVIN - CCT_MIN_KELVIN
        return CCT_MIN_KELVIN + int((self._cct_level - 1) / (self._cct_levels - 1) * kelvin_range)

    async def async_added_to_hass(self) -> None:
        """Restore last state when added to hass."""
        await super().async_added_to_hass()

        # Restore previous state
        if (last_state := await self.async_get_last_state()) is not None:
            self._is_on = last_state.state == "on"
            # Restore brightness level if available
            if self._brightness_levels and last_state.attributes.get(ATTR_BRIGHTNESS):
                ha_brightness = last_state.attributes[ATTR_BRIGHTNESS]
                self._brightness_level = self._ha_brightness_to_level(ha_brightness)
            # Restore CCT level if available
            if self._cct_levels and last_state.attributes.get(ATTR_COLOR_TEMP_KELVIN):
                kelvin = last_state.attributes[ATTR_COLOR_TEMP_KELVIN]
                self._cct_level = self._kelvin_to_level(kelvin)
            _LOGGER.debug(
                "Restored state for %s: %s, brightness_level: %s, cct_level: %s",
                self._attr_name,
                "on" if self._is_on else "off",
                self._brightness_level,
                self._cct_level,
            )

    def _ha_brightness_to_level(self, ha_brightness: int) -> int:
        """Convert HA brightness (1-255) to lamp level (1-brightness_levels)."""
        if not self._brightness_levels:
            return 1
        # Map 1-255 to 1-brightness_levels evenly
        level = ((ha_brightness - 1) * self._brightness_levels // 254) + 1
        return max(1, min(self._brightness_levels, level))

    def _kelvin_to_level(self, kelvin: int) -> int:
        """Convert Kelvin to CCT level (1-cct_levels)."""
        if not self._cct_levels:
            return 1
        # Clamp kelvin to valid range
        kelvin = max(CCT_MIN_KELVIN, min(CCT_MAX_KELVIN, kelvin))
        # Map to level
        kelvin_range = CCT_MAX_KELVIN - CCT_MIN_KELVIN
        level = round((kelvin - CCT_MIN_KELVIN) / kelvin_range * (self._cct_levels - 1)) + 1
        return max(1, min(self._cct_levels, level))

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the light on."""
        target_brightness = kwargs.get(ATTR_BRIGHTNESS)
        target_color_temp = kwargs.get(ATTR_COLOR_TEMP_KELVIN)

        if not self._is_on:
            # Turn on the light first
            await self._send_command(CMD_TOGGLE)
            self._is_on = True
            # Wait before adjusting if needed
            if (self._brightness_levels and target_brightness is not None) or \
               (self._cct_levels and target_color_temp is not None):
                await asyncio.sleep(0.3)

        # Adjust brightness if specified and supported
        if target_brightness is not None and self._brightness_levels:
            target_level = self._ha_brightness_to_level(target_brightness)
            await self._adjust_brightness(target_level)

        # Adjust CCT if specified and supported
        if target_color_temp is not None and self._cct_levels:
            target_level = self._kelvin_to_level(target_color_temp)
            await self._adjust_cct(target_level)

        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the light off."""
        if not self._is_on:
            _LOGGER.debug("%s is already off, skipping toggle", self._attr_name)
            return

        await self._send_command(CMD_TOGGLE)
        self._is_on = False
        self.async_write_ha_state()

    async def _adjust_brightness(self, target_level: int) -> None:
        """Adjust brightness to target level by sending up/down commands."""
        if not self._brightness_levels or self._brightness_level is None:
            return

        current = self._brightness_level
        diff = target_level - current

        if diff == 0:
            return

        command = CMD_BRIGHTNESS_UP if diff > 0 else CMD_BRIGHTNESS_DOWN
        steps = abs(diff)

        _LOGGER.debug(
            "Adjusting brightness for %s: %d -> %d (%d %s commands)",
            self._attr_name,
            current,
            target_level,
            steps,
            command,
        )

        for i in range(steps):
            if i > 0:
                await asyncio.sleep(0.3)  # 300ms gap between commands
            await self._send_command(command)

        self._brightness_level = target_level

    async def _adjust_cct(self, target_level: int) -> None:
        """Adjust CCT to target level by cycling with toggle command."""
        if not self._cct_levels or self._cct_level is None:
            return

        current = self._cct_level

        if current == target_level:
            return

        # Calculate steps needed (cycling: 1->2->3->4->1...)
        # Always go forward since we can only toggle in one direction
        if target_level > current:
            steps = target_level - current
        else:
            # Need to wrap around: e.g., from 4 to 1 with 4 levels = 1 step
            steps = (self._cct_levels - current) + target_level

        _LOGGER.debug(
            "Adjusting CCT for %s: %d -> %d (%d %s commands)",
            self._attr_name,
            current,
            target_level,
            steps,
            CMD_CCT_TOGGLE,
        )

        for i in range(steps):
            if i > 0:
                await asyncio.sleep(0.3)  # 300ms gap between commands
            await self._send_command(CMD_CCT_TOGGLE)

        self._cct_level = target_level

    async def _send_command(self, command: str) -> None:
        """Send command via remote."""
        _LOGGER.debug(
            "Sending %s command to %s via %s",
            command,
            self._device_name,
            self._remote_entity,
        )

        await self.hass.services.async_call(
            "remote",
            "send_command",
            {
                "entity_id": self._remote_entity,
                "device": self._device_name,
                "command": command,
            },
            blocking=True,
        )
