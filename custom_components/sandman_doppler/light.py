"""Light platform for Doppler Sandman."""
from __future__ import annotations

import logging
from typing import Any

from doppyler.model.color import Color
from doppyler.model.dotw import DOTWStatus
from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_RGB_COLOR,
    COLOR_MODE_RGB,
    LightEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import DopplerDataUpdateCoordinator
from .const import (
    ATTR_AUTO_BRIGHTNESS_ENABLED,
    ATTR_DAY_BUTTON_COLOR,
    ATTR_NIGHT_BUTTON_COLOR,
    ATTR_DAY_DISPLAY_BRIGHTNESS,
    ATTR_NIGHT_DISPLAY_BRIGHTNESS,
    ATTR_DAY_BUTTON_BRIGHTNESS,
    ATTR_NIGHT_BUTTON_BRIGHTNESS,
    ATTR_DAY_DISPLAY_COLOR,
    ATTR_NIGHT_DISPLAY_COLOR,
    ATTR_DOTW_STATUS,
    DOMAIN,
)
from .entity import DopplerEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_devices: AddEntitiesCallback
) -> None:
    """Setup sensor platform."""
    coordinator: DopplerDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []
    for device in coordinator.api.devices.values():
        entities.extend(
            [
                DopplerDisplayLightDay(coordinator, entry, device, "Day Display"),
                DopplerDisplayLightNight(coordinator, entry, device, "Night Display"),
                DopplerButtonLightDay(coordinator, entry, device, "Day Button"),
                DopplerButtonLightNight(coordinator, entry, device, "Night Button"),
                # DopplerDOTWLight(
                #     coordinator, entry, device, "Day of the Week Indicator"
                # ),
            ]
        )
    async_add_devices(entities)


class BaseDopplerLight(DopplerEntity, LightEntity):
    """Base Doppler Light class."""

    _attr_color_mode = COLOR_MODE_RGB
    _attr_supported_color_modes = {COLOR_MODE_RGB}


class DopplerDisplayLightDay(BaseDopplerLight):
    """Doppler Display Light class."""

    _attr_is_on = True
    _attr_icon = "mdi:clock-digital"

    @property
    def rgb_color(self) -> tuple[int, int, int] | None:
        """Return the rgb color value [int, int, int]."""
        color: Color | None = self.coordinator.data[self.device.name][
            ATTR_DAY_DISPLAY_COLOR
        ]
        if not color:
            return None
        return (color.red, color.green, color.blue)

    @property
    def brightness(self) -> int:
        """Return the brightness of this light between 0..255."""
        brightness = self.coordinator.data[self.device.name][ATTR_DAY_DISPLAY_BRIGHTNESS]
        if brightness is not None:
            return round((brightness / 100) * 255)
        return 0

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the device on."""
        brightness = kwargs.get(ATTR_DAY_DISPLAY_BRIGHTNESS)
        rgb_color = kwargs.get(ATTR_RGB_COLOR)
        if brightness is not None:
            await self.coordinator.api.set_day_display_brightness(
                self.device,
                int(100 * brightness / 255),
            )
        if rgb_color is not None:
            await self.coordinator.api.set_day_display_color(
                self.device, Color(rgb_color[0], rgb_color[1], rgb_color[2])
            )


class DopplerDisplayLightNight(BaseDopplerLight):
    """Doppler Display Light class."""

    _attr_is_on = True
    _attr_icon = "mdi:clock-digital"

    @property
    def rgb_color(self) -> tuple[int, int, int] | None:
        """Return the rgb color value [int, int, int]."""
        color: Color | None = self.coordinator.data[self.device.name][
            ATTR_NIGHT_DISPLAY_COLOR
        ]
        if not color:
            return None
        return (color.red, color.green, color.blue)

    @property
    def brightness(self) -> int:
        """Return the brightness of this light between 0..255."""
        brightness = self.coordinator.data[self.device.name][ATTR_NIGHT_DISPLAY_BRIGHTNESS]
        if brightness is not None:
            return round((brightness / 100) * 255)
        return 0

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the device on."""
        brightness = kwargs.get(ATTR_NIGHT_DISPLAY_BRIGHTNESS)
        rgb_color = kwargs.get(ATTR_RGB_COLOR)
        if brightness is not None:
            await self.coordinator.api.set_night_display_brightness(
                self.device,
                int(100 * brightness / 255),
            )
        if rgb_color is not None:
            await self.coordinator.api.set_night_display_color(
                self.device, Color(rgb_color[0], rgb_color[1], rgb_color[2])
            )


class DopplerButtonLightDay(BaseDopplerLight):
    """Doppler Button Light class."""

    _attr_is_on = True
    _attr_icon = "mdi:gesture-tap-button"

    @property
    def rgb_color(self) -> tuple[int, int, int] | None:
        """Return the rgb color value [int, int, int]."""
        color: Color | None = self.coordinator.data[self.device.name][ATTR_DAY_BUTTON_COLOR]
        if not color:
            return None
        return (color.red, color.green, color.blue)

    @property
    def brightness(self) -> int:
        """Return the brightness of this light between 0..255."""
        brightness = self.coordinator.data[self.device.name][ATTR_DAY_BUTTON_BRIGHTNESS]
        if brightness is not None:
            return round((brightness / 100) * 255)
        return 0

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the device on."""
        brightness = kwargs.get(ATTR_DAY_BUTTON_BRIGHTNESS)
        rgb_color = kwargs.get(ATTR_RGB_COLOR)
        if brightness is not None:
            await self.coordinator.api.set_day_button_brightness(
                self.device,
                int(100 * brightness / 255),
            )
        
        if rgb_color is not None:

            await self.coordinator.api.set_sync_button_display_color(
                self.device,False)
            await self.coordinator.api.set_day_button_color(
                self.device, Color(rgb_color[0], rgb_color[1], rgb_color[2])
            )

class DopplerButtonLightNight(BaseDopplerLight):
    """Doppler Button Light class."""

    _attr_is_on = True
    _attr_icon = "mdi:gesture-tap-button"

    @property
    def rgb_color(self) -> tuple[int, int, int] | None:
        """Return the rgb color value [int, int, int]."""
        color: Color | None = self.coordinator.data[self.device.name][ATTR_NIGHT_BUTTON_COLOR]
        if not color:
            return None
        return (color.red, color.green, color.blue)

    @property
    def brightness(self) -> int:
        """Return the brightness of this light between 0..255."""
        brightness = self.coordinator.data[self.device.name][ATTR_NIGHT_BUTTON_BRIGHTNESS]
        if brightness is not None:
            return round((brightness / 100) * 255)
        return 0


    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the device on."""
        brightness = kwargs.get(ATTR_NIGHT_BUTTON_BRIGHTNESS)
        rgb_color = kwargs.get(ATTR_RGB_COLOR)
        if brightness is not None:
            await self.coordinator.api.set_night_button_brightness(
                self.device,
                int(100 * brightness / 255),
            )
        if rgb_color is not None:

            await self.coordinator.api.set_sync_button_display_color(
                self.device, False)
            await self.coordinator.api.set_night_button_color(
                self.device, Color(rgb_color[0], rgb_color[1], rgb_color[2])
            )


class DopplerDOTWLight(BaseDopplerLight):
    """Doppler Day of the Week Light class."""

    _attr_icon = "mdi:calendar-today"

    @property
    def is_on(self) -> bool:
        """Return whether day of the week indicator is on."""
        dotw_status: DOTWStatus = self.coordinator.data[self.device.name][
            ATTR_DOTW_STATUS
        ]
        return dotw_status.is_on

    @property
    def rgb_color(self) -> tuple[int, int, int] | None:
        """Return the rgb color value [int, int, int]."""
        color: Color = self.coordinator.data[self.device.name][ATTR_DAY_DISPLAY_COLOR]
        return (color.red, color.green, color.blue)

    async def async_turn_off(self) -> None:
        """Turn the device off."""
        dotw_status: DOTWStatus = self.coordinator.data[self.device.name][
            ATTR_DOTW_STATUS
        ]
        color = dotw_status.color
        await self.coordinator.api.set_day_of_the_week_status(self.device, False, color)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the device on."""
        rgb_color = kwargs.get(ATTR_RGB_COLOR)
        dotw_status: DOTWStatus = self.coordinator.data[self.device.name][
            ATTR_DOTW_STATUS
        ]
        color = dotw_status.color
        if rgb_color is not None:
            color = Color(rgb_color[0], rgb_color[1], rgb_color[2])
        await self.coordinator.api.set_day_of_the_week_status(self.device, True, color)
