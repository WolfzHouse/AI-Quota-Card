"""Sensor platform for AI Web Quota."""
from __future__ import annotations

import logging

from homeassistant.components.sensor import (
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, CONF_PROVIDER, CONF_AUTH_INDEX

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the AI Web Quota sensors."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    provider = entry.data[CONF_PROVIDER]
    auth_index = entry.data.get(CONF_AUTH_INDEX, "0")

    # Access parsed data from coordinator
    data = coordinator.data
    if not data or "items" not in data:
        # If API failed on first fetch, data might be empty. Coordinator should handle retries
        return

    email = data.get("email", "Unknown Email")
    plan = data.get("plan", "Unknown Plan")

    device_id = f"ai_quota_{provider}_{auth_index}"
    device_name = f"{provider.capitalize()} Quota (Auth {auth_index})"

    device_info = DeviceInfo(
        identifiers={(DOMAIN, device_id)},
        name=device_name,
        manufacturer="AI Quota Metrics",
        model=plan,
        sw_version=email, # Hacky way to neatly show email attached to device
    )

    sensors = []

    # Iterate through groups (e.g. "Claude Quota", "GPT", "Gemini")
    for group in data["items"]:
        # We also create a sensor for the group's global avg quota just in case
        group_id = group["name"].lower().replace(" ", "_").replace(".", "_")
        sensors.append(AIQuotaPercentageSensor(
            coordinator=coordinator,
            device_info=device_info,
            provider=provider,
            auth_index=auth_index,
            group_name=group["name"],
            model_name=None,
            entity_id_base=f"{device_id}_{group_id}_avg"
        ))

        # Iterating through actual models/limits inside the group
        for model in group["models"]:
            # Sanitize names for entity registry
            raw_model_name = model["name"]
            sanitized_name = raw_model_name.lower().replace(" ", "_").replace("-", "_").replace(".", "_")

            # 1. Percentage Sensor
            sensors.append(AIQuotaPercentageSensor(
                coordinator=coordinator,
                device_info=device_info,
                provider=provider,
                auth_index=auth_index,
                group_name=group["name"],
                model_name=raw_model_name,
                entity_id_base=f"{device_id}_{sanitized_name}"
            ))

            # 2. Reset Time / Extra Info Sensor (Only if there's actually a reset value)
            if model.get("resetTime"):
                sensors.append(AIQuotaResetSensor(
                    coordinator=coordinator,
                    device_info=device_info,
                    provider=provider,
                    auth_index=auth_index,
                    group_name=group["name"],
                    model_name=raw_model_name,
                    entity_id_base=f"{device_id}_{sanitized_name}_reset"
                ))

    async_add_entities(sensors, update_before_add=False)


class AIQuotaPercentageSensor(CoordinatorEntity, SensorEntity):
    """Percentage sensor for a quota limit."""

    def __init__(
        self, coordinator, device_info, provider, auth_index, group_name, model_name, entity_id_base
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_device_info = device_info
        
        self._provider = provider
        self._auth_index = str(auth_index)
        self._group_name = group_name
        self._model_name = model_name
        
        self.entity_id = f"sensor.{entity_id_base}"
        self._attr_unique_id = self.entity_id
        
        display_name = f"{model_name}" if model_name else f"{group_name} Average"
        self._attr_name = f"{provider.capitalize()} {display_name} Quota"
        
        self._attr_icon = "mdi:chart-arc"
        self._attr_native_unit_of_measurement = "%"
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if not self.coordinator.data or "items" not in self.coordinator.data:
            return None
            
        # Parse through updated coordinator data to reflect current loop targets
        for group in self.coordinator.data["items"]:
            if group["name"] == self._group_name:
                if not self._model_name:
                    return group.get("percentage")
                
                for model in group["models"]:
                    if model["name"] == self._model_name:
                        return model.get("percentage")
        
        return None

    @property
    def extra_state_attributes(self):
        """Return entity specific state attributes."""
        attrs = {
            "group_name": self._group_name,
            "model_name": self._model_name,
            "provider": self._provider,
            "auth_index": self._auth_index,
        }
        if self.coordinator.data:
            attrs["plan"] = self.coordinator.data.get("plan", "Unknown Plan")
            attrs["email"] = self.coordinator.data.get("email", "Unknown Email")
        return attrs

class AIQuotaResetSensor(CoordinatorEntity, SensorEntity):
    """Auxiliary string sensor for reset times or usage stats."""

    def __init__(
        self, coordinator, device_info, provider, auth_index, group_name, model_name, entity_id_base
    ) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._attr_device_info = device_info
        
        self._group_name = group_name
        self._model_name = model_name
        
        self.entity_id = f"sensor.{entity_id_base}"
        self._attr_unique_id = self.entity_id
        self._attr_name = f"{provider.capitalize()} {model_name} Info"
        
        self._attr_icon = "mdi:information-outline"
        if "reset" in entity_id_base.lower() and "extra" not in entity_id_base.lower():
            self._attr_icon = "mdi:clock-outline"

    @property
    def native_value(self):
        """Return string values like $38.00 / $100.00 or ISO8601 Timestamp."""
        if not self.coordinator.data or "items" not in self.coordinator.data:
            return None
            
        for group in self.coordinator.data["items"]:
            if group["name"] == self._group_name:
                for model in group["models"]:
                    if model["name"] == self._model_name:
                        return model.get("resetTime")
        return None

    @property
    def extra_state_attributes(self):
        """Return entity specific state attributes."""
        attrs = {
            "group_name": self._group_name,
            "model_name": self._model_name,
        }
        if self.coordinator.data:
            attrs["plan"] = self.coordinator.data.get("plan", "Unknown Plan")
            attrs["email"] = self.coordinator.data.get("email", "Unknown Email")
        return attrs
