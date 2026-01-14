"""Config flow for RF Remote Lamp integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import (
    CONF_BRIGHTNESS_LEVELS,
    CONF_CCT_LEVELS,
    CONF_DEVICE_NAME,
    CONF_LAMP_NAME,
    CONF_REMOTE_ENTITY,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class RfRemoteLampConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for RF Remote Lamp."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Validate the remote entity exists
            remote_entity = user_input[CONF_REMOTE_ENTITY]
            if not self.hass.states.get(remote_entity):
                errors["base"] = "remote_not_found"
            else:
                # Create a unique ID based on remote + device name
                unique_id = f"{remote_entity}_{user_input[CONF_DEVICE_NAME]}"
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=user_input[CONF_LAMP_NAME],
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_LAMP_NAME): str,
                    vol.Required(CONF_REMOTE_ENTITY): selector.EntitySelector(
                        selector.EntitySelectorConfig(domain="remote")
                    ),
                    vol.Required(CONF_DEVICE_NAME): str,
                    vol.Optional(CONF_BRIGHTNESS_LEVELS): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=2, max=100, step=1, mode=selector.NumberSelectorMode.BOX
                        )
                    ),
                    vol.Optional(CONF_CCT_LEVELS): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=2, max=20, step=1, mode=selector.NumberSelectorMode.BOX
                        )
                    ),
                }
            ),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Get the options flow for this handler."""
        return RfRemoteLampOptionsFlow()


class RfRemoteLampOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for RF Remote Lamp."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Manage the options."""
        if user_input is not None:
            # Clean up None values from optional fields
            clean_data = {k: v for k, v in user_input.items() if v is not None}

            # Update entry.data directly (not just options)
            self.hass.config_entries.async_update_entry(
                self.config_entry,
                data=clean_data,
                title=clean_data[CONF_LAMP_NAME],
            )
            return self.async_create_entry(title="", data={})

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_LAMP_NAME,
                        default=self.config_entry.data.get(CONF_LAMP_NAME, ""),
                    ): str,
                    vol.Required(
                        CONF_REMOTE_ENTITY,
                        default=self.config_entry.data.get(CONF_REMOTE_ENTITY, ""),
                    ): selector.EntitySelector(
                        selector.EntitySelectorConfig(domain="remote")
                    ),
                    vol.Required(
                        CONF_DEVICE_NAME,
                        default=self.config_entry.data.get(CONF_DEVICE_NAME, ""),
                    ): str,
                    vol.Optional(
                        CONF_BRIGHTNESS_LEVELS,
                        default=self.config_entry.data.get(CONF_BRIGHTNESS_LEVELS),
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=2, max=100, step=1, mode=selector.NumberSelectorMode.BOX
                        )
                    ),
                    vol.Optional(
                        CONF_CCT_LEVELS,
                        default=self.config_entry.data.get(CONF_CCT_LEVELS),
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=2, max=20, step=1, mode=selector.NumberSelectorMode.BOX
                        )
                    ),
                }
            ),
        )
