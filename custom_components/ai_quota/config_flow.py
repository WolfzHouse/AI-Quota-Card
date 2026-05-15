"""Config flow for AI Web Quota integration."""
import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .const import (
    DOMAIN,
    CONF_PROXY_URL,
    CONF_PROVIDER,
    CONF_AUTH_INDEX,
    CONF_PROXY_TOKEN,
    CONF_ACCOUNT_NAME,
    CONF_TROUTER_API_KEY,
    CONF_DATA_SOURCE,
    DEFAULT_PROXY_URL,
    DATA_SOURCES,
    PROVIDERS
)

_LOGGER = logging.getLogger(__name__)

# Dropdown options for the data source selection
DATA_SOURCE_OPTIONS = [
    selector.SelectOptionDict(value=key, label=name)
    for key, name in DATA_SOURCES.items()
]

# Dropdown options for the provider selection
PROVIDER_OPTIONS = [
    selector.SelectOptionDict(value=key, label=name)
    for key, name in PROVIDERS.items()
]

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_DATA_SOURCE, default="cliproxy"): selector.SelectSelector(
            selector.SelectSelectorConfig(
                options=DATA_SOURCE_OPTIONS,
                mode=selector.SelectSelectorMode.DROPDOWN,
            )
        ),
        vol.Required(CONF_PROVIDER): selector.SelectSelector(
            selector.SelectSelectorConfig(
                options=PROVIDER_OPTIONS,
                mode=selector.SelectSelectorMode.DROPDOWN,
            )
        ),
        vol.Required(CONF_AUTH_INDEX, default="0"): str,
        vol.Optional(CONF_PROXY_TOKEN, default=""): str,
        vol.Optional(CONF_TROUTER_API_KEY, default=""): str,
        vol.Optional(CONF_ACCOUNT_NAME, default=""): str,
        vol.Optional(CONF_PROXY_URL, default=DEFAULT_PROXY_URL): str,
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
            data_source = DATA_SOURCES.get(user_input[CONF_DATA_SOURCE], user_input[CONF_DATA_SOURCE])
            provider = PROVIDERS.get(user_input[CONF_PROVIDER], user_input[CONF_PROVIDER])
            title = f"{data_source} - {provider} (Auth: {user_input[CONF_AUTH_INDEX]})"
            return self.async_create_entry(title=title, data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return AIQuotaOptionsFlowHandler()


class AIQuotaOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for AI Web Quota."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        # Merge data and options to allow editing what was initially set in data
        options = dict(self.config_entry.data)
        if hasattr(self.config_entry, "options") and self.config_entry.options:
            options.update(self.config_entry.options)

        schema = vol.Schema(
            {
                vol.Optional(CONF_DATA_SOURCE, default=str(options.get(CONF_DATA_SOURCE) or "cliproxy")): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=DATA_SOURCE_OPTIONS,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
                vol.Optional(CONF_PROXY_TOKEN, default=str(options.get(CONF_PROXY_TOKEN) or "")): str,
                vol.Optional(CONF_TROUTER_API_KEY, default=str(options.get(CONF_TROUTER_API_KEY) or "")): str,
                vol.Optional(CONF_ACCOUNT_NAME, default=str(options.get(CONF_ACCOUNT_NAME) or "")): str,
                vol.Optional(CONF_PROXY_URL, default=str(options.get(CONF_PROXY_URL) or DEFAULT_PROXY_URL)): str,
            }
        )

        return self.async_show_form(step_id="init", data_schema=schema)
