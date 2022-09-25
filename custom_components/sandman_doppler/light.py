"""Light platform for Doppler Sandman."""
from __future__ import annotations

from collections.abc import Callable, Coroutine
from dataclasses import dataclass
import logging
from typing import Any, Literal

from doppyler.const import (
    ATTR_DAY_BUTTON_BRIGHTNESS,
    ATTR_DAY_BUTTON_COLOR,
    ATTR_DAY_DISPLAY_BRIGHTNESS,
    ATTR_DAY_DISPLAY_COLOR,
    ATTR_NIGHT_BUTTON_BRIGHTNESS,
    ATTR_NIGHT_BUTTON_COLOR,
    ATTR_NIGHT_DISPLAY_BRIGHTNESS,
    ATTR_NIGHT_DISPLAY_COLOR,
)
from doppyler.model.color import Color
from doppyler.model.doppler import Doppler
from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_RGB_COLOR,
    COLOR_MODE_RGB,
    LightEntity,
    LightEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import DopplerDataUpdateCoordinator
from .const import DOMAIN
from .entity import DopplerEntity

_LOGGER = logging.getLogger(__name__)


@dataclass
class DopplerLightEntityDescription(LightEntityDescription):
    """Class to describe Doppler light entities."""

    color_key: str | None = None
    set_color_func: Callable[[Doppler, Color], Coroutine[Any, Any, Color]] | None = None
    brightness_key: str | None = None
    set_brightness_func: Callable[
        [Doppler, Color], Coroutine[Any, Any, int | float]
    ] | None = None
    opposite_day_or_night: Literal["day", "night"] | None = None
    opposite_display_or_button: Literal["display", "button"] | None = None


LIGHT_ENTITY_DESCRIPTIONS = [
    DopplerLightEntityDescription(
        "Day Display",
        icon="mdi:clock-digital",
        name="Day Display",
        color_key=ATTR_DAY_DISPLAY_COLOR,
        set_color_func=lambda dev, color: dev.set_day_display_color(color),
        brightness_key=ATTR_DAY_DISPLAY_BRIGHTNESS,
        set_brightness_func=lambda dev, brightness: dev.set_day_display_brightness(
            brightness
        ),
        opposite_day_or_night="night",
        opposite_display_or_button="button",
    ),
    DopplerLightEntityDescription(
        "Night Display",
        icon="mdi:clock-digital",
        name="Night Display",
        color_key=ATTR_NIGHT_DISPLAY_COLOR,
        set_color_func=lambda dev, color: dev.set_night_display_color(color),
        brightness_key=ATTR_NIGHT_DISPLAY_BRIGHTNESS,
        set_brightness_func=lambda dev, brightness: dev.set_night_display_brightness(
            brightness
        ),
        opposite_day_or_night="day",
        opposite_display_or_button="button",
    ),
    DopplerLightEntityDescription(
        "Day Button",
        icon="mdi:gesture-tap-button",
        name="Day Button",
        color_key=ATTR_DAY_BUTTON_COLOR,
        set_color_func=lambda dev, color: dev.set_day_button_color(color),
        brightness_key=ATTR_DAY_BUTTON_BRIGHTNESS,
        set_brightness_func=lambda dev, brightness: dev.set_day_button_brightness(
            brightness
        ),
        opposite_day_or_night="night",
        opposite_display_or_button="display",
    ),
    DopplerLightEntityDescription(
        "Night Button",
        icon="mdi:gesture-tap-button",
        name="Night Button",
        color_key=ATTR_NIGHT_BUTTON_COLOR,
        set_color_func=lambda dev, color: dev.set_night_button_color(color),
        brightness_key=ATTR_NIGHT_BUTTON_BRIGHTNESS,
        set_brightness_func=lambda dev, brightness: dev.set_night_button_brightness(
            brightness
        ),
        opposite_day_or_night="day",
        opposite_display_or_button="display",
    ),
]


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_devices: AddEntitiesCallback
) -> None:
    """Setup sensor platform."""

    @callback
    def async_add_device(device: Doppler) -> None:
        """Add Doppler binary sensor entities."""
        coordinator: DopplerDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
        entities = [
            DopplerLight(coordinator, entry, device, description)
            for description in LIGHT_ENTITY_DESCRIPTIONS
        ]
        async_add_devices(entities)

    entry.async_on_unload(
        async_dispatcher_connect(
            hass, f"{DOMAIN}_{entry.entry_id}_device_added", async_add_device
        )
    )


class DopplerLight(DopplerEntity[DopplerLightEntityDescription], LightEntity):
    """Doppler Light class."""

    _attr_color_mode = COLOR_MODE_RGB
    _attr_supported_color_modes = {COLOR_MODE_RGB}
    _attr_is_on = True

    @property
    def rgb_color(self) -> tuple[int, int, int] | None:
        """Return the rgb color value [int, int, int]."""
        color: Color | None = self.device_data[self.ed.color_key]
        if not color:
            return None
        return (color.red, color.green, color.blue)

    @property
    def brightness(self) -> int:
        """Return the brightness of this light between 0..255."""
        brightness = self.device_data[self.ed.brightness_key]
        if brightness is not None:
            return brightness * 255 // 100
        return 0

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the device on."""
        brightness = kwargs.get(ATTR_BRIGHTNESS)
        rgb_color = kwargs.get(ATTR_RGB_COLOR)
        if brightness is not None:
            self.device_data[
                self.ed.brightness_key
            ] = await self.ed.set_brightness_func(self.device, brightness * 100 // 255)
        if rgb_color is not None:
            self.device_data[self.ed.color_key] = await self.ed.set_color_func(
                self.device, Color(rgb_color[0], rgb_color[1], rgb_color[2])
            )

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the device off."""
        _LOGGER.warning(
            "Turning off the Doppler %s %s is not supported.",
            self.ed.opposite_display_or_button,
            "light" if self.ed.opposite_display_or_button == "display" else "lights",
        )
