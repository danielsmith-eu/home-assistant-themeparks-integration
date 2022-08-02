"""Platform for Theme Park sensor integration."""
from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import TIME_MINUTES
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import DOMAIN, NAME, TIME

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""

    my_api = hass.data[DOMAIN][config_entry.entry_id]
    coordinator = ThemeParksCoordinator(hass, my_api)

    await coordinator.async_config_entry_first_refresh()

    _LOGGER.info("Config entry first refresh completed, adding entities")
    entities = [AttractionSensor(coordinator, idx) for idx in coordinator.data.keys()]

    _LOGGER.info(
        "Entities to add (count: %s): %s", str(entities.__len__), str(entities)
    )
    async_add_entities(entities)


class AttractionSensor(SensorEntity, CoordinatorEntity):
    """An entity using CoordinatorEntity."""

    def __init__(self, coordinator, idx):
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator)
        self.idx = idx
        self._attr_name = coordinator.data[idx][NAME]
        self._attr_native_unit_of_measurement = TIME_MINUTES
        self._attr_device_class = SensorDeviceClass.DURATION
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_value = self.coordinator.data[self.idx][TIME]

        _LOGGER.debug("Adding AttractionSensor called %s", self._attr_name)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        newtime = self.coordinator.data[self.idx][TIME]
        _LOGGER.debug(
            "Setting updated time from coordinator for %s to %s",
            str(self._attr_name),
            str(newtime),
        )
        self._attr_native_value = newtime
        self.async_write_ha_state()


class ThemeParksCoordinator(DataUpdateCoordinator):
    """Theme parks coordinator."""

    def __init__(self, hass, api):
        """Initialize theme parks coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="Theme Park Wait Time Sensor",
            update_interval=timedelta(minutes=5),
        )
        self.api = api

    async def _async_update_data(self):
        """Fetch data from API endpoint."""
        _LOGGER.debug("Calling do_live_lookup in ThemeParksCoordinator")
        return await self.api.do_live_lookup()
