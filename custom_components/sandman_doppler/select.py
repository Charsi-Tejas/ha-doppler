"""Select platform for Doppler Sandman."""
from __future__ import annotations

from collections.abc import Callable, Coroutine
from dataclasses import dataclass
from enum import Enum
from typing import Any
import zoneinfo

from doppyler.const import (
    ATTR_SOUND_PRESET,
    ATTR_TIME_MODE,
    ATTR_TIMEZONE,
    ATTR_WEATHER,
)
from doppyler.model.doppler import Doppler
from doppyler.model.sound import SoundPreset
from doppyler.model.weather import WeatherMode
from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import DopplerDataUpdateCoordinator
from .const import DOMAIN
from .entity import DopplerEntity
from .helpers import get_enum_from_name, normalize_enum_name


@dataclass
class DopplerEnumSelectEntityDescription(SelectEntityDescription):
    """Doppler Enum Select Entity Description."""

    enum_cls: Enum | None = None
    state_key: str | None = None
    state_func: Callable[[Enum], str] = lambda x: x
    set_value_func: Callable[[Doppler, int], Coroutine[Any, Any, Enum]] = lambda x: x


ENUM_SELECT_ENTITY_DESCRIPTIONS = [
    DopplerEnumSelectEntityDescription(
        "Sound Preset",
        name="Sound Preset",
        enum_cls=SoundPreset,
        state_key=ATTR_SOUND_PRESET,
        state_func=lambda x: normalize_enum_name(x),
        set_value_func=lambda dev, val: dev.set_sound_preset(val),
    ),
    DopplerEnumSelectEntityDescription(
        "Weather Mode",
        name="Weather Mode",
        enum_cls=WeatherMode,
        state_key=ATTR_WEATHER,
        state_func=lambda x: normalize_enum_name(x.mode),
        set_value_func=lambda dev, val: dev.set_weather_configuration(mode=val),
    ),
]


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_devices: AddEntitiesCallback
) -> None:
    """Setup sensor platform."""
    coordinator: DopplerDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []
    for device in coordinator.api.devices.values():
        entities.extend(
            [
                DopplerTimeModeSelect(coordinator, entry, device, "Time Mode"),
                DopplerTimezoneSelect(coordinator, entry, device, "Timezone"),
                *(
                    DopplerEnumSelect(coordinator, entry, device, description)
                    for description in ENUM_SELECT_ENTITY_DESCRIPTIONS
                ),
            ]
        )
    async_add_devices(entities)


class DopplerEnumSelect(DopplerEntity, SelectEntity):
    """Doppler Select class for enum attributes."""

    _attr_entity_category = EntityCategory.CONFIG

    def __init__(
        self,
        coordinator: DopplerDataUpdateCoordinator,
        entry: ConfigEntry,
        device: Doppler,
        description: DopplerEnumSelectEntityDescription,
    ) -> None:
        """Initialize the select."""
        super().__init__(coordinator, entry, device, description.name)
        self.entity_description = description
        self._enum_cls: Enum = description.enum_cls
        self._state_key: str = description.state_key
        self._state_func = description.state_func
        self._set_value_func = description.set_value_func

        self._attr_options = [
            normalize_enum_name(enum_val) for enum_val in self._enum_cls
        ]

    @property
    def current_option(self) -> str:
        """Return the current option."""
        current_option = self.device_data[self._state_key]
        return self._state_func(current_option)

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        enum_val = get_enum_from_name(self._enum_cls, option)
        self.device_data[self._state_key] = await self._set_value_func(
            self.device, enum_val
        )


class DopplerTimeModeSelect(DopplerEntity, SelectEntity):
    """Doppler Time Mode Select class."""

    _attr_entity_category = EntityCategory.CONFIG

    _attr_options = ["12", "24"]

    @property
    def current_option(self) -> str:
        """Return the current option."""
        return str(self.device_data[ATTR_TIME_MODE])

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        self.device_data[ATTR_TIME_MODE] = await self.device.set_time_mode(int(option))


class DopplerTimezoneSelect(DopplerEntity, SelectEntity):
    """Doppler Timezone Select class."""

    _attr_entity_category = EntityCategory.CONFIG

    @property
    def options(self) -> list[str]:
        """Return a list of available options."""
        return sorted(list(zoneinfo.available_timezones()))

    @property
    def current_option(self) -> str:
        """Return the current option."""
        return str(self.device_data[ATTR_TIMEZONE])

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        self.device_data[ATTR_TIMEZONE] = await self.device.set_timezone(option)
