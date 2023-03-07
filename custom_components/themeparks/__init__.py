"""The Theme Park Wait Times integration."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr, entity_registry as er
from homeassistant.helpers.httpx_client import get_async_client

from .const import (
    DOMAIN,
    ENTITY_BASE_URL,
    ENTITY_TYPE,
    ID,
    LIVE,
    LIVE_DATA,
    METHOD_GET,
    NAME,
    PARKNAME,
    PARKSLUG,
    QUEUE,
    STANDBY,
    TIME,
    TYPE_ATTRACTION,
    TYPE_SHOW,
    WAIT_TIME,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Theme Park Wait Times from a config entry."""
    data = hass.data.setdefault(DOMAIN, {})

    api = ThemeParkAPI(hass, entry)
    await api.async_initialize()

    data[entry.entry_id] = api

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    device_registry = dr.async_get(hass)
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, entry.entry_id)},
        connections=None,
        name=entry.title,
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


class ThemeParkAPI:
    """Wrapper for theme parks API."""

    # -- Set in async_initialize --
    ha_device_registry: dr.DeviceRegistry
    ha_entity_registry: er.EntityRegistry

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        """Initialize the gateway."""
        self._hass = hass
        self._config_entry = config_entry
        self._parkslug = config_entry.data[PARKSLUG]
        self._parkname = config_entry.data[PARKNAME]

    async def async_initialize(self) -> None:
        """Initialize controller and connect radio."""
        self.ha_device_registry = dr.async_get(self._hass)
        self.ha_entity_registry = er.async_get(self._hass)

    async def do_live_lookup(self):
        """Do API lookup of the 'live' page of this park."""
        _LOGGER.debug("Running do_live_lookup in ThemeParkAPI")

        items = await self.do_api_lookup()

        def parse_live(item):
            """Parse live data from API."""

            _LOGGER.debug("Parsed API item for: %s", item[NAME])

            name = item[NAME] + " (" + self._parkname + ")"

            if "queue" not in item:
                _LOGGER.debug("No queue in item")
                return (item[ID], {ID: item[ID], NAME: name, TIME: None})

            if "STANDBY" not in item[QUEUE]:
                _LOGGER.debug("No STANDBY in item['queue']")
                return (item[ID], {ID: item[ID], NAME: name, TIME: None})

            _LOGGER.debug("Time found")
            return (
                item[ID],
                {
                    ID: item[ID],
                    NAME: name,
                    TIME: item[QUEUE][STANDBY][WAIT_TIME],
                },
            )

        return dict(map(parse_live, items))

    async def do_api_lookup(self):
        """Lookup the subpage and subfield in the API."""
        url = f"{ENTITY_BASE_URL}/{self._parkslug}/{LIVE}"

        client = get_async_client(self._hass)
        response = await client.request(
            METHOD_GET,
            url,
            timeout=30,
            follow_redirects=True,
        )

        items_data = response.json()

        def filter_item(item):
            return (
                item[ENTITY_TYPE] == TYPE_SHOW or item[ENTITY_TYPE] == TYPE_ATTRACTION
            )

        return filter(filter_item, items_data[LIVE_DATA])
