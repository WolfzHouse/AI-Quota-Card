"""Config flow for AI Web Quota integration."""
import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .const import (
    DOMAIN,
    CONF_PROXY_URL,
    CONF_PROVIDER,
    CONF_AUTH_INDEX,
    CONF_PROXY_TOKEN,
    CONF_GEMINI_PROJECT_ID,
    CONF_CUSTOM_PLAN_NAME,
    DEFAULT_PROXY_URL,
    PROVIDERS
)

_LOGGER = logging.getLogger(__name__)

# Dropdown options for the provider selection
PROVIDER_OPTIONS = [
    selector.SelectOptionDict(value=key, label=name)
    for key, name in PROVIDERS.items()
]

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_PROVIDER): selector.SelectSelector(
            selector.SelectSelectorConfig(
                options=PROVIDER_OPTIONS,
                mode=selector.SelectSelectorMode.DROPDOWN,
            )
        ),
        vol.Required(CONF_AUTH_INDEX, default="0"): str,
        vol.Required(CONF_PROXY_TOKEN): str,
        vol.Optional(CONF_PROXY_URL, default=DEFAULT_PROXY_URL): str,
        vol.Optional(CONF_GEMINI_PROJECT_ID): str,
        vol.Optional(CONF_CUSTOM_PLAN_NAME): str,
    }
)


class AIQuotaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for AI Web Quota."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # We can do basic validation here if needed
            # For now, just create the entry
            title = f"{PROVIDERS.get(user_input[CONF_PROVIDER], user_input[CONF_PROVIDER])} (Auth: {user_input[CONF_AUTH_INDEX]})"
            return self.async_create_entry(title=title, data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )
