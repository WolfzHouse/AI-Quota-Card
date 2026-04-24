"""The AI Web Quota integration."""
from __future__ import annotations

import logging
from pathlib import Path

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.components.frontend import add_extra_js_url

from .const import DOMAIN
from .coordinator import AIQuotaDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]

_CARD_URL = f"/{DOMAIN}/ai-quota-card.js"
_CARD_REGISTERED = False


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Register the Lovelace card JS file as a static resource automatically."""
    global _CARD_REGISTERED
    if not _CARD_REGISTERED:
        card_path = Path(__file__).parent / "ai-quota-card.js"
        hass.http.register_static_path(_CARD_URL, str(card_path), cache_headers=False)
        add_extra_js_url(hass, _CARD_URL)
        _CARD_REGISTERED = True
        _LOGGER.info("AI Quota Card registered at %s", _CARD_URL)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up AI Web Quota from a config entry."""
    coordinator = AIQuotaDataUpdateCoordinator(hass, entry)
    
    # Fetch initial data so we have state when entities are added
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True

async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry when options change."""
    await hass.config_entries.async_reload(entry.entry_id)

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
