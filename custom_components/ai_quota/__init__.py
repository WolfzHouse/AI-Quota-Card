"""The AI Web Quota integration."""
from __future__ import annotations

import logging
from pathlib import Path

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from homeassistant.components.frontend import add_extra_js_url
from homeassistant.components.http import StaticPathConfig
from homeassistant.helpers.storage import Store

from .const import DOMAIN
from .coordinator import AIQuotaDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]

_CARD_VERSION = "1.0.1"
_SUMMARY_CARD_URL = f"/{DOMAIN}/ai-quota-summary-card.js?v={_CARD_VERSION}"
_STANDALONE_CARD_URL = f"/{DOMAIN}/ai-quota-standalone-card.js?v={_CARD_VERSION}"
_CARDS_REGISTERED = False


async def _ensure_lovelace_resource(hass: HomeAssistant, url: str) -> None:
    """Write the card URL into HA's persistent Lovelace resource store."""
    import uuid  # noqa: PLC0415

    store = Store(hass, version=1, key="lovelace_resources")
    data = await store.async_load()
    if data is None:
        data = {"items": []}

    items: list[dict] = data.get("items", [])
    if any(item.get("url") == url for item in items):
        _LOGGER.debug("AI Quota Card already in Lovelace resources")
        return

    items.append({"id": str(uuid.uuid4()), "type": "module", "url": url})
    data["items"] = items
    await store.async_save(data)
    _LOGGER.info("AI Quota Card added to persistent Lovelace resources: %s", url)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Register the Lovelace cards JS on every HA boot."""
    global _CARDS_REGISTERED
    if not _CARDS_REGISTERED:
        # Register summary card
        summary_card_path = Path(__file__).parent / "www" / "ai-quota-summary-card.js"
        await hass.http.async_register_static_paths([
            StaticPathConfig(_SUMMARY_CARD_URL, str(summary_card_path), cache_headers=False)
        ])
        add_extra_js_url(hass, _SUMMARY_CARD_URL)
        await _ensure_lovelace_resource(hass, _SUMMARY_CARD_URL)
        _LOGGER.info("AI Quota Summary Card fully registered at %s", _SUMMARY_CARD_URL)
        
        # Register standalone card
        standalone_card_path = Path(__file__).parent / "www" / "ai-quota-standalone-card.js"
        await hass.http.async_register_static_paths([
            StaticPathConfig(_STANDALONE_CARD_URL, str(standalone_card_path), cache_headers=False)
        ])
        add_extra_js_url(hass, _STANDALONE_CARD_URL)
        await _ensure_lovelace_resource(hass, _STANDALONE_CARD_URL)
        _LOGGER.info("AI Quota Standalone Card fully registered at %s", _STANDALONE_CARD_URL)
        
        _CARDS_REGISTERED = True

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
