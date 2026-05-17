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
    CONF_API_KEY,
    CONF_ACCOUNT_NAME,
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


def get_schema_for_data_source(data_source: str, defaults: dict[str, Any] | None = None) -> vol.Schema:
    """Generate schema based on data source."""
    if defaults is None:
        defaults = {}
    
    base_fields = {
        vol.Required(CONF_DATA_SOURCE, default=defaults.get(CONF_DATA_SOURCE, "cliproxy")): selector.SelectSelector(
            selector.SelectSelectorConfig(
                options=DATA_SOURCE_OPTIONS,
                mode=selector.SelectSelectorMode.DROPDOWN,
            )
        ),
        vol.Required(CONF_PROVIDER, default=defaults.get(CONF_PROVIDER, "")): selector.SelectSelector(
            selector.SelectSelectorConfig(
                options=PROVIDER_OPTIONS,
                mode=selector.SelectSelectorMode.DROPDOWN,
            )
        ),
        vol.Required(CONF_AUTH_INDEX, default=defaults.get(CONF_AUTH_INDEX, "0")): str,
    }
    
    # Add data-source-specific fields
    if data_source == "cliproxy":
        base_fields[vol.Required(CONF_PROXY_URL, default=defaults.get(CONF_PROXY_URL, DEFAULT_PROXY_URL))] = str
        base_fields[vol.Optional(CONF_ACCOUNT_NAME, default=defaults.get(CONF_ACCOUNT_NAME, ""))] = str
        # CLIProxy doesn't need API key - it uses provider auth index
        
    elif data_source == "trouter":
        base_fields[vol.Required(CONF_API_KEY, default=defaults.get(CONF_API_KEY, ""))] = selector.TextSelector(
            selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD)
        )
        base_fields[vol.Optional(CONF_ACCOUNT_NAME, default=defaults.get(CONF_ACCOUNT_NAME, ""))] = str
        
    elif data_source == "9router":
        base_fields[vol.Required(CONF_PROXY_URL, default=defaults.get(CONF_PROXY_URL, "http://localhost:20128"))] = str
        base_fields[vol.Required(CONF_API_KEY, default=defaults.get(CONF_API_KEY, ""))] = selector.TextSelector(
            selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD)
        )
        base_fields[vol.Optional(CONF_ACCOUNT_NAME, default=defaults.get(CONF_ACCOUNT_NAME, ""))] = str
    
    return vol.Schema(base_fields)


class AIQuotaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for AI Web Quota."""

    VERSION = 1

    def __init__(self):
        """Initialize the config flow."""
        self._data_source = "cliproxy"

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Validate based on data source
            data_source = user_input.get(CONF_DATA_SOURCE, "cliproxy")
            
            if data_source == "9router":
                if not user_input.get(CONF_API_KEY):
                    errors["base"] = "password_required"
                elif not user_input.get(CONF_PROXY_URL):
                    errors["base"] = "url_required"
            elif data_source == "trouter":
                if not user_input.get(CONF_API_KEY):
                    errors["base"] = "api_key_required"
            
            if not errors:
                # Generate a unique_id based on provider, auth_index, and data_source
                unique_id = f"{user_input[CONF_DATA_SOURCE]}_{user_input[CONF_PROVIDER]}_{user_input[CONF_AUTH_INDEX]}"
                
                # Set the unique_id to prevent duplicates
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()
                
                # Create the entry title
                data_source_name = DATA_SOURCES.get(user_input[CONF_DATA_SOURCE], user_input[CONF_DATA_SOURCE])
                provider = PROVIDERS.get(user_input[CONF_PROVIDER], user_input[CONF_PROVIDER])
                title = f"{data_source_name} - {provider} (Auth: {user_input[CONF_AUTH_INDEX]})"
                return self.async_create_entry(title=title, data=user_input)
        
        # Update data source if changed
        if user_input and CONF_DATA_SOURCE in user_input:
            self._data_source = user_input[CONF_DATA_SOURCE]
        
        schema = get_schema_for_data_source(self._data_source, user_input or {})
        
        return self.async_show_form(
            step_id="user", 
            data_schema=schema, 
            errors=errors,
            description_placeholders={
                "data_source": DATA_SOURCES.get(self._data_source, self._data_source)
            }
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return AIQuotaOptionsFlowHandler(config_entry)


class AIQuotaOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for AI Web Quota."""

    def __init__(self, config_entry: config_entries.ConfigEntry):
        """Initialize options flow."""
        self.config_entry = config_entry

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

        data_source = options.get(CONF_DATA_SOURCE, "cliproxy")
        schema = get_schema_for_data_source(data_source, options)

        return self.async_show_form(step_id="init", data_schema=schema)
