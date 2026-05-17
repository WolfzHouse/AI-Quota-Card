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
    if not data:
        # If API failed on first fetch, data might be empty. Coordinator should handle retries
        return

    email = data.get("email", "Unknown Email")
    plan = data.get("plan", "Unknown Plan")

    device_id = f"ai_quota_{provider}_{auth_index}"
    device_name = f"{provider.capitalize()} (Auth {auth_index})"

    device_info = DeviceInfo(
        identifiers={(DOMAIN, device_id)},
        name=device_name,
        manufacturer="AI Quota",
        model=plan,
        sw_version=email,
    )

    # Create just ONE main sensor with all data in attributes
    sensors = [
        AIQuotaMainSensor(
            coordinator=coordinator,
            device_info=device_info,
            provider=provider,
            auth_index=auth_index,
            entity_id_base=f"{provider}_{provider}_auth_{auth_index}"
        )
    ]

    async_add_entities(sensors, update_before_add=False)


class AIQuotaMainSensor(CoordinatorEntity, SensorEntity):
    """Main sensor that contains all quota data in attributes."""

    def __init__(
        self, coordinator, device_info, provider, auth_index, entity_id_base
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_device_info = device_info

        self._provider = provider
        self._auth_index = str(auth_index)

        self.entity_id = f"sensor.{entity_id_base}"
        self._attr_unique_id = self.entity_id
        self._attr_name = f"{provider.capitalize()} Quota"

        self._attr_icon = "mdi:chart-donut"
        self._attr_native_unit_of_measurement = "%"
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self):
        """Return the main quota percentage."""
        if not self.coordinator.data:
            return None

        # Return the first group's first model's percentage as the main state
        items = self.coordinator.data.get("items", [])
        if items and len(items) > 0:
            group = items[0]
            models = group.get("models", [])
            if models and len(models) > 0:
                # Return the first model's percentage (usually the main quota)
                return models[0].get("percentage")
            # Fallback to group percentage if no models
            return group.get("percentage")

        return None

    @property
    def extra_state_attributes(self):
        """Return all quota data in attributes."""
        if not self.coordinator.data:
            return {}

        attrs = {
            "provider": self._provider,
            "auth_index": self._auth_index,
            "email": self.coordinator.data.get("email", "Unknown"),
            "plan": self.coordinator.data.get("plan", "Unknown"),
            "api_payload": self.coordinator.data,
        }

        # Add summary of all groups and models
        items = self.coordinator.data.get("items", [])
        if items:
            groups_summary = []
            for group in items:
                group_info = {
                    "name": group.get("name"),
                    "percentage": group.get("percentage"),
                    "models": []
                }
                for model in group.get("models", []):
                    model_info = {
                        "name": model.get("name"),
                        "percentage": model.get("percentage"),
                        "resetTime": model.get("resetTime"),
                        "usage": model.get("usage"),
                        "limit": model.get("limit"),
                        "usageDisplay": model.get("usageDisplay"),
                        "expiresIn": model.get("expiresIn"),
                    }
                    group_info["models"].append(model_info)
                groups_summary.append(group_info)

            attrs["groups"] = groups_summary

        return attrs
