"""Config flow for Theme Park Wait Times integration."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries

# from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.httpx_client import get_async_client

from .const import (
    DESTINATIONS,
    DESTINATIONS_URL,
    DOMAIN,
    METHOD_GET,
    NAME,
    PARKNAME,
    PARKSLUG,
    SLUG,
    STEP_USER,
)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {vol.Required(PARKSLUG): str, vol.Required(PARKNAME): str}
)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Theme Park Wait Times."""

    VERSION = 1
    _destinations: dict[str, Any] = {}

    async def _async_update_data(self):
        """Fetch list of parks."""

        client = get_async_client(self.hass)
        response = await client.request(
            METHOD_GET,
            DESTINATIONS_URL,
            timeout=10,
            follow_redirects=True,
        )

        parkdata = response.json()

        def parse_dest(item):
            slug = item[SLUG]
            name = item[NAME]
            return (name, slug)

        return dict(map(parse_dest, parkdata[DESTINATIONS]))

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Run the user config flow step."""

        if user_input is not None:

            return self.async_create_entry(
                title="Theme Park: %s" % user_input[PARKNAME],
                data={
                    PARKSLUG: self._destinations[user_input[PARKNAME]],
                    PARKNAME: user_input[PARKNAME],
                },
            )

        if self._destinations == {}:
            self._destinations = await self._async_update_data()

        schema = {vol.Required(PARKNAME): vol.In(sorted(self._destinations.keys()))}
        return self.async_show_form(
            step_id=STEP_USER, data_schema=vol.Schema(schema), last_step=True
        )
