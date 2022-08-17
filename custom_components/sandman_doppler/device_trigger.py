"""Provides device triggers for sandman_doppler."""
from __future__ import annotations

from typing import Any
import logging
_LOGGER: logging.Logger = logging.getLogger(__package__)

import voluptuous as vol

from homeassistant.components.automation import (
    AutomationActionType,
    AutomationTriggerInfo,
)
from homeassistant.components.device_automation import DEVICE_TRIGGER_BASE_SCHEMA
from homeassistant.components.homeassistant.triggers import event as event_trigger
from homeassistant.const import (
    CONF_EVENT,
    CONF_DEVICE_ID,
    CONF_DOMAIN,
    CONF_ENTITY_ID,
    CONF_PLATFORM,
    CONF_TYPE,
    CONF_SUBTYPE,
    STATE_OFF,
    STATE_ON,
)
from homeassistant.core import CALLBACK_TYPE, HomeAssistant
from homeassistant.helpers import config_validation as cv, entity_registry
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.typing import ConfigType

from .const import (
    DOMAIN,
    SANDMAN_DOPPLER_BUTTON1_EVENT,
    SANDMAN_DOPPLER_BUTTON2_EVENT,
    ATTR_DSN,
    ATTR_BUTTON,
)

# TODO specify your supported trigger types.
#TRIGGER_TYPES = {"Doppler-4fcd8f3c_butt_1", "Doppler-4fcd8f3c_butt2"}
TRIGGER_TYPES = {"sandman_doppler_button"}

TRIGGER_SCHEMA = DEVICE_TRIGGER_BASE_SCHEMA.extend(
    {
#        vol.Required(CONF_ENTITY_ID): cv.entity_id,
        vol.Required(CONF_TYPE): TRIGGER_TYPES,
    }
)


async def async_get_triggers(
    hass: HomeAssistant, device_id: str
) -> list[dict[str, Any]]:
    """List device triggers for sandman_doppler devices."""
    registry = entity_registry.async_get(hass)
    my_device_registry=dr.async_get(hass)
    triggers = []

    _LOGGER.warning(f"device_id={device_id}")


    device_entry=my_device_registry.async_get(device_id)
    _LOGGER.warning(f"device_entry.identifiers={device_entry.identifiers}")

#    for id in device_entry.identifiers:
#        if id[1].startswith("Doppler"):
#            trigger_base=id[1]
    
    
    triggers.append({
        # Required fields of TRIGGER_BASE_SCHEMA
        CONF_PLATFORM: "device",
        CONF_DOMAIN: "sandman_doppler",
#        CONF_DEVICE_ID: device_id,
        # Required fields of TRIGGER_SCHEMA
        CONF_TYPE: "sandman_doppler_button",
        
    })
    
    _LOGGER.warning(f"triggers= {triggers}")

    return triggers


async def async_attach_trigger(
    hass: HomeAssistant,
    config: ConfigType,
    action: AutomationActionType,
    automation_info: AutomationTriggerInfo,
) -> CALLBACK_TYPE:
    """Attach a trigger."""

    my_device_registry=dr.async_get(hass)
    device=my_device_registry.async_get(config[CONF_DEVICE_ID])

#    for id in device.identifiers:
#        if id.startswith("Doppler"):
#            dsn=id
    
    event_config = event_trigger.TRIGGER_SCHEMA({
        event_trigger.CONF_PLATFORM: CONF_EVENT,
        event_trigger.CONF_EVENT_TYPE: "sandman_doppler_button",
        event_trigger.CONF_EVENT_DATA: {
#            ATTR_DSN: dsn,
#            ATTR_BUTTON: {"button1","button2"},
            CONF_DEVICE_ID: config[CONF_DEVICE_ID],
            CONF_TYPE: config[CONF_TYPE]
        },
    },)
    
    _LOGGER.warning(f"event_config={event_config}")
            
    return await event_trigger.async_attach_trigger(
        hass, event_config, action, automation_info, platform_type="device"
    )
