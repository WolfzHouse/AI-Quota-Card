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
from homeassistant.helpers import device_registry as dr

from .const import DOMAIN, CONF_PROXY_URL, CONF_DATA_SOURCE, CONF_SESSION_TOKEN, CONF_ACCOUNT_LABEL

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the AI Web Quota sensors."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    data_source = entry.data.get(CONF_DATA_SOURCE, "9router")
    proxy_url = entry.data.get(CONF_PROXY_URL, "http://localhost:20128")
    
    import hashlib
    
    # Hub ID
    is_direct = data_source in ("claude_direct", "codex_direct", "antigravity_direct")
    if data_source == "trouter":
        api_key_hash = hashlib.md5(str(entry.data.get('api_key', '')).encode('utf-8')).hexdigest()[:10]
        hub_id = f"{data_source}_{api_key_hash}"
        hub_name = "Trouter.click Hub"
    elif is_direct:
        session_token = entry.data.get(CONF_SESSION_TOKEN, "")
        account_label = entry.data.get(CONF_ACCOUNT_LABEL, "").strip()
        token_hash = hashlib.md5(session_token.encode('utf-8')).hexdigest()[:10]
        provider_label = data_source.replace("_direct", "").capitalize()
        hub_id = f"{data_source}_{token_hash}"
        hub_name = f"{provider_label} Direct Hub" + (f" — {account_label}" if account_label else "")
    else:
        proxy_hash = hashlib.md5(str(proxy_url).encode('utf-8')).hexdigest()[:10]
        hub_id = f"{data_source}_{proxy_hash}"
        hub_name = f"9Router ({proxy_url})"
        
    # Ensure hub device is created in the device registry (only for proxy/hub sources)
    if not is_direct:
        device_registry = dr.async_get(hass)
        device_registry.async_get_or_create(
            config_entry_id=entry.entry_id,
            identifiers={(DOMAIN, hub_id)},
            name=hub_name,
            manufacturer="AI Quota",
            model="AI Quota Hub",
        )

    data = coordinator.data
    if not data or not isinstance(data, dict):
        return

    connections = data.get("connections", {})
    sensors = []

    for conn_id, conn_data in connections.items():
        provider = conn_data.get("provider", "unknown")
        name = conn_data.get("name", "Unknown")
        plan = conn_data.get("plan", "Unknown Plan")
        email = conn_data.get("email", "Unknown Email")
        
        device_id = f"{data_source}_{conn_id}"
        
        if is_direct:
            provider_display = data_source.replace("_direct", "").capitalize()
            device_name = f"{provider_display} Direct — {name}" if name else f"{provider_display} Direct"
        else:
            device_name = f"{provider.capitalize()} - {name}"

        device_info = DeviceInfo(
            identifiers={(DOMAIN, device_id)},
            name=device_name,
            manufacturer="AI Quota",
            model=plan,
            sw_version=email,
        )
        if not is_direct:
            device_info["via_device"] = (DOMAIN, hub_id)

        sensors.append(
            AIQuotaConnectionSensor(
                coordinator=coordinator,
                device_info=device_info,
                connection_id=conn_id,
                connection_data=conn_data,
                data_source=data_source
            )
        )

    if sensors:
        async_add_entities(sensors, update_before_add=False)


class AIQuotaConnectionSensor(CoordinatorEntity, SensorEntity):
    """Main sensor that contains quota data for a specific connection."""

    def __init__(
        self, coordinator, device_info, connection_id, connection_data, data_source
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_device_info = device_info
        self._connection_id = connection_id
        
        provider = connection_data.get("provider", "unknown")
        name = connection_data.get("name", "Unknown")

        # Sanitize entity ID
        safe_provider = provider.replace("-", "_").lower()
        safe_id = connection_id.replace("-", "_")[:8].lower()
        
        self.entity_id = f"sensor.{data_source}_{safe_provider}_{safe_id}"
        self._attr_unique_id = f"{data_source}_{connection_id}"
        self._attr_name = f"{provider.capitalize()} {name} Quota"

        self._attr_icon = "mdi:chart-donut"
        self._attr_native_unit_of_measurement = "%"
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self):
        """Return the main quota percentage."""
        if not self.coordinator.data:
            return None

        connections = self.coordinator.data.get("connections", {})
        conn_data = connections.get(self._connection_id, {})

        items = conn_data.get("items", [])
        if items and len(items) > 0:
            group = items[0]
            models = group.get("models", [])
            if models and len(models) > 0:
                return models[0].get("percentage")
            return group.get("percentage")

        return None

    @property
    def extra_state_attributes(self):
        """Return all quota data in attributes."""
        if not self.coordinator.data:
            return {}

        connections = self.coordinator.data.get("connections", {})
        conn_data = connections.get(self._connection_id, {})

        attrs = {
            "provider": conn_data.get("provider", "Unknown"),
            "email": conn_data.get("email", "Unknown"),
            "plan": conn_data.get("plan", "Unknown"),
            "isActive": conn_data.get("isActive", False),
            "api_payload": conn_data.get("api_payload", {}),
        }

        # Add summary of all groups and models
        items = conn_data.get("items", [])
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
